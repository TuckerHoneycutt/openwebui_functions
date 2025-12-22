"""
OpenWebUI Function: Template Manager

This function allows users to:
1. Upload PDF/DOCX templates via chat (with file attachment)
2. List available templates
3. Format chat output using templates

The function works with file attachments in OpenWebUI messages.
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile

try:
    from template_extractor import TemplateExtractor
    from template_manager import TemplateManager
    from pdf_generator import PDFGenerator
    TEMPLATE_SUPPORT = True
except ImportError:
    TEMPLATE_SUPPORT = False
    TemplateExtractor = None
    TemplateManager = None
    PDFGenerator = None


# Initialize components
if TEMPLATE_SUPPORT:
    template_manager = TemplateManager()
    template_extractor = TemplateExtractor()
    pdf_generator = PDFGenerator()
else:
    template_manager = None
    template_extractor = None
    pdf_generator = None


def get_function_schema():
    """Return the function schema for OpenWebUI"""
    return {
        "name": "manage_document_template",
        "description": "Upload PDF/DOCX templates, list templates, or format chat output using a template. Upload templates by attaching a PDF/DOCX file and mentioning the template name. Format output by specifying a template name.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["upload_template", "list_templates", "format_output"],
                    "description": "Action to perform: 'upload_template' to upload a template (requires file attachment), 'list_templates' to see available templates, 'format_output' to format the last message using a template"
                },
                "template_name": {
                    "type": "string",
                    "description": "Name for the template (required for upload_template and format_output). For upload_template, this is the name you want to give the template. For format_output, this is the name of an existing template to use."
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to uploaded file (automatically provided by OpenWebUI when file is attached)"
                },
                "file_content": {
                    "type": "string",
                    "description": "Base64 encoded file content (automatically provided by OpenWebUI)"
                }
            },
            "required": ["action"]
        }
    }


async def manage_document_template(
    action: str,
    template_name: Optional[str] = None,
    file_path: Optional[str] = None,
    file_content: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function handler for template management

    Args:
        action: Action to perform
        template_name: Name of template
        file_path: Path to uploaded file (from OpenWebUI)
        file_content: Base64 encoded file content
        user_id: User ID for isolation
        **kwargs: Additional parameters (may include file attachments from OpenWebUI)

    Returns:
        Dictionary with result data
    """
    if not TEMPLATE_SUPPORT:
        return {
            "success": False,
            "error": "Template support not available. Please ensure all dependencies are installed."
        }

    try:
        if action == "upload_template":
            return await _handle_upload_template(
                template_name=template_name,
                file_path=file_path,
                file_content=file_content,
                user_id=user_id,
                **kwargs
            )

        elif action == "list_templates":
            templates = template_manager.list_templates(user_id=user_id)
            return {
                "success": True,
                "templates": templates,
                "count": len(templates),
                "message": f"Found {len(templates)} template(s)" if templates else "No templates found. Upload one using 'upload_template' action with a file attachment."
            }

        elif action == "format_output":
            if not template_name:
                return {
                    "success": False,
                    "error": "template_name is required for format_output action"
                }

            # Get the last assistant message content from kwargs
            content = kwargs.get("content") or kwargs.get("last_message_content") or ""

            if not content:
                return {
                    "success": False,
                    "error": "No content provided to format. Please provide the content to format."
                }

            return await _handle_format_output(
                template_name=template_name,
                content=content,
                user_id=user_id
            )

        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}. Use 'upload_template', 'list_templates', or 'format_output'"
            }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Error processing request: {str(e)}",
            "traceback": traceback.format_exc()
        }


async def _handle_upload_template(
    template_name: Optional[str],
    file_path: Optional[str],
    file_content: Optional[str],
    user_id: Optional[str],
    **kwargs
) -> Dict[str, Any]:
    """Handle template upload"""

    # OpenWebUI may pass files in different ways
    # Check for file in kwargs (common OpenWebUI pattern)
    uploaded_file = kwargs.get("file") or kwargs.get("uploaded_file")

    # Determine file path and content
    if uploaded_file:
        # File object from OpenWebUI
        if hasattr(uploaded_file, "file_path"):
            file_path = uploaded_file.file_path
        elif hasattr(uploaded_file, "read"):
            # Read file content
            file_content = base64.b64encode(uploaded_file.read()).decode("utf-8")
            file_path = None

    # If we have file_path, read the file
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        file_type = "pdf" if file_path.lower().endswith(".pdf") else "docx"
    elif file_content:
        # Decode base64 content
        if isinstance(file_content, str):
            if file_content.startswith("data:"):
                file_content = file_content.split(",", 1)[1]
            file_bytes = base64.b64decode(file_content)
        else:
            file_bytes = file_content

        # Determine file type from template_name or default
        if template_name:
            if template_name.lower().endswith(".pdf"):
                file_type = "pdf"
            elif template_name.lower().endswith(".docx"):
                file_type = "docx"
            else:
                file_type = kwargs.get("file_type", "pdf")
        else:
            file_type = kwargs.get("file_type", "pdf")
    else:
        return {
            "success": False,
            "error": "No file provided. Please attach a PDF or DOCX file when uploading a template."
        }

    # Generate template name if not provided
    if not template_name:
        template_name = f"Template_{Path(file_path).stem if file_path else 'uploaded'}"

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    try:
        # Extract template metadata
        metadata = template_extractor.extract_template(tmp_path, file_type)

        # Save template
        template_id = template_manager.save_template(
            template_name=template_name,
            file_path=tmp_path,
            metadata=metadata,
            file_type=file_type,
            user_id=user_id
        )

        return {
            "success": True,
            "message": f"Template '{template_name}' uploaded and processed successfully",
            "template_id": template_id,
            "template_name": template_name,
            "metadata_summary": {
                "headers": len(metadata.get("headers", [])),
                "tables": len(metadata.get("tables", [])),
                "fonts": len(metadata.get("fonts", {})),
                "styles": len(metadata.get("styles", {})),
                "page_count": metadata.get("page_count", 0)
            }
        }

    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise e


async def _handle_format_output(
    template_name: str,
    content: str,
    user_id: Optional[str]
) -> Dict[str, Any]:
    """Handle formatting output using template"""

    # Get template info
    template_info = template_manager.get_template_info(template_name, user_id=user_id)
    if not template_info:
        return {
            "success": False,
            "error": f"Template '{template_name}' not found. Use 'list_templates' to see available templates."
        }

    # Generate PDF using template
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
        "message": f"Content formatted using template '{template_name}'",
        "pdf_data": pdf_data,
        "filename": f"{template_name}_formatted.pdf",
        "download_instruction": "The formatted PDF is available as base64 data. Use a download handler to save it."
    }
