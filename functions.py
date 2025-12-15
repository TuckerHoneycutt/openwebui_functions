"""
OpenWebUI Function: PDF Template Formatter

This function allows users to:
1. Upload PDF/DOCX templates and extract formatting metadata
2. Select from uploaded templates
3. Format AI responses into PDFs matching the template formatting
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import shutil

from template_extractor import TemplateExtractor
from pdf_generator import PDFGenerator
from template_manager import TemplateManager


# Initialize components
template_manager = TemplateManager()
template_extractor = TemplateExtractor()
pdf_generator = PDFGenerator()


def get_function_schema():
    """Return the function schema for OpenWebUI"""
    return {
        "name": "format_to_pdf_template",
        "description": "Format AI responses into PDFs using uploaded templates. Extract formatting from templates and apply it to generated content.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["upload_template", "list_templates", "generate_pdf", "get_template_info"],
                    "description": "Action to perform: upload_template, list_templates, generate_pdf, or get_template_info"
                },
                "template_name": {
                    "type": "string",
                    "description": "Name of the template to use (required for generate_pdf and get_template_info)"
                },
                "content": {
                    "type": "string",
                    "description": "The AI-generated content to format into PDF (required for generate_pdf)"
                },
                "template_file": {
                    "type": "string",
                    "description": "Base64 encoded template file (required for upload_template)"
                },
                "file_type": {
                    "type": "string",
                    "enum": ["pdf", "docx"],
                    "description": "Type of template file: pdf or docx (required for upload_template)"
                }
            },
            "required": ["action"]
        }
    }


async def format_to_pdf_template(
    action: str,
    template_name: Optional[str] = None,
    content: Optional[str] = None,
    template_file: Optional[str] = None,
    file_type: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function handler for PDF template formatting

    Args:
        action: Action to perform
        template_name: Name of the template
        content: Content to format
        template_file: Base64 encoded template file
        file_type: Type of template file (pdf/docx)
        user_id: User ID for template isolation

    Returns:
        Dictionary with result data
    """
    try:
        if action == "upload_template":
            if not template_name or not template_file or not file_type:
                return {
                    "success": False,
                    "error": "template_name, template_file, and file_type are required for upload_template"
                }

            # Decode base64 file
            try:
                file_data = base64.b64decode(template_file)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to decode template file: {str(e)}"
                }

            # Save template file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
                tmp_file.write(file_data)
                tmp_path = tmp_file.name

            try:
                # Extract template metadata
                metadata = template_extractor.extract_template(tmp_path, file_type)

                # Save template and metadata
                template_id = template_manager.save_template(
                    template_name=template_name,
                    file_path=tmp_path,
                    metadata=metadata,
                    file_type=file_type,
                    user_id=user_id
                )

                return {
                    "success": True,
                    "message": f"Template '{template_name}' uploaded successfully",
                    "template_id": template_id,
                    "metadata_summary": {
                        "headers": len(metadata.get("headers", [])),
                        "tables": len(metadata.get("tables", [])),
                        "page_breaks": len(metadata.get("page_breaks", [])),
                        "styles": len(metadata.get("styles", {}))
                    }
                }
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        elif action == "list_templates":
            templates = template_manager.list_templates(user_id=user_id)
            return {
                "success": True,
                "templates": templates
            }

        elif action == "get_template_info":
            if not template_name:
                return {
                    "success": False,
                    "error": "template_name is required for get_template_info"
                }

            info = template_manager.get_template_info(template_name, user_id=user_id)
            if not info:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' not found"
                }

            return {
                "success": True,
                "template_info": info
            }

        elif action == "generate_pdf":
            if not template_name or not content:
                return {
                    "success": False,
                    "error": "template_name and content are required for generate_pdf"
                }

            # Get template metadata
            template_info = template_manager.get_template_info(template_name, user_id=user_id)
            if not template_info:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' not found"
                }

            # Generate PDF
            pdf_path = pdf_generator.generate_pdf(
                content=content,
                template_metadata=template_info["metadata"],
                template_file_path=template_info["file_path"],
                output_name=f"{template_name}_output.pdf"
            )

            # Read PDF and encode as base64
            with open(pdf_path, "rb") as f:
                pdf_data = base64.b64encode(f.read()).decode("utf-8")

            # Clean up generated PDF
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

            return {
                "success": True,
                "message": "PDF generated successfully",
                "pdf_data": pdf_data,
                "filename": f"{template_name}_output.pdf"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing request: {str(e)}"
        }
