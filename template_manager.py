"""
Template Manager Module

Manages template storage, retrieval, and metadata.
"""

import os
import json
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib


class TemplateManager:
    """Manage template storage and retrieval"""

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize template manager

        Args:
            storage_dir: Directory to store templates (defaults to env var or ./templates)
        """
        # Use environment variable for Docker compatibility, fallback to default
        if storage_dir is None:
            storage_dir = os.getenv("TEMPLATE_STORAGE_DIR", "templates")

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.storage_dir / "metadata.json"
        self._metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load template metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_metadata(self):
        """Save template metadata to disk"""
        with open(self.metadata_file, "w") as f:
            json.dump(self._metadata, f, indent=2)

    def save_template(
        self,
        template_name: str,
        file_path: str,
        metadata: Dict[str, Any],
        file_type: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Save a template and its metadata

        Args:
            template_name: Name of the template
            file_path: Path to the template file
            metadata: Extracted metadata
            file_type: Type of file (pdf/docx)
            user_id: Optional user ID for isolation

        Returns:
            Template ID
        """
        # Create user-specific directory if user_id provided
        if user_id:
            user_dir = self.storage_dir / f"user_{user_id}"
            user_dir.mkdir(exist_ok=True)
            template_dir = user_dir
        else:
            template_dir = self.storage_dir

        # Generate template ID
        template_id = hashlib.md5(
            f"{template_name}_{user_id or 'global'}_{file_type}".encode()
        ).hexdigest()

        # Copy template file
        template_file_path = template_dir / f"{template_id}.{file_type}"
        shutil.copy2(file_path, template_file_path)

        # Store metadata
        template_key = f"{user_id or 'global'}_{template_name}" if user_id else template_name

        self._metadata[template_key] = {
            "template_id": template_id,
            "template_name": template_name,
            "file_path": str(template_file_path),
            "file_type": file_type,
            "metadata": metadata,
            "user_id": user_id,
            "created_at": str(Path(file_path).stat().st_mtime)
        }

        self._save_metadata()

        return template_id

    def list_templates(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available templates

        Args:
            user_id: Optional user ID to filter templates

        Returns:
            List of template information dictionaries
        """
        templates = []

        for key, template_info in self._metadata.items():
            # Filter by user_id if provided
            if user_id:
                if template_info.get("user_id") == user_id or template_info.get("user_id") is None:
                    templates.append({
                        "template_name": template_info["template_name"],
                        "template_id": template_info["template_id"],
                        "file_type": template_info["file_type"],
                        "created_at": template_info.get("created_at")
                    })
            else:
                # Show global templates and templates for this user
                if template_info.get("user_id") is None:
                    templates.append({
                        "template_name": template_info["template_name"],
                        "template_id": template_info["template_id"],
                        "file_type": template_info["file_type"],
                        "created_at": template_info.get("created_at")
                    })

        return templates

    def get_template_info(
        self,
        template_name: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get template information by name

        Args:
            template_name: Name of the template
            user_id: Optional user ID

        Returns:
            Template information dictionary or None if not found
        """
        # Try user-specific first
        if user_id:
            user_key = f"{user_id}_{template_name}"
            if user_key in self._metadata:
                return self._metadata[user_key]

        # Try global
        if template_name in self._metadata:
            template_info = self._metadata[template_name]
            # Only return if it's global (no user_id) or matches user_id
            if template_info.get("user_id") is None or template_info.get("user_id") == user_id:
                return template_info

        # Search for exact match
        for key, template_info in self._metadata.items():
            if template_info["template_name"] == template_name:
                if user_id is None or template_info.get("user_id") == user_id or template_info.get("user_id") is None:
                    return template_info

        return None

    def delete_template(
        self,
        template_name: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Delete a template

        Args:
            template_name: Name of the template
            user_id: Optional user ID

        Returns:
            True if deleted, False if not found
        """
        template_info = self.get_template_info(template_name, user_id)

        if not template_info:
            return False

        # Delete template file
        file_path = template_info["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)

        # Remove from metadata
        template_key = f"{user_id}_{template_name}" if user_id else template_name

        # Find the actual key in metadata
        for key in list(self._metadata.keys()):
            if self._metadata[key]["template_name"] == template_name:
                if user_id is None or self._metadata[key].get("user_id") == user_id:
                    del self._metadata[key]
                    break

        self._save_metadata()

        return True

    def get_template_file_path(
        self,
        template_name: str,
        user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the file path for a template

        Args:
            template_name: Name of the template
            user_id: Optional user ID

        Returns:
            File path or None if not found
        """
        template_info = self.get_template_info(template_name, user_id)
        if template_info:
            return template_info["file_path"]
        return None
