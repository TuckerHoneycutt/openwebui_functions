"""
OpenWebUI Action: Template Upload and Format

This action provides a UI button to:
1. Upload PDF/DOCX templates and extract formatting
2. Format chat output using the extracted template

title: Document Template Formatter
author: Custom
version: 1.0.0
required_open_webui_version: "0.5.0"
description: Upload PDF/DOCX templates and format chat output to match template styling
icon_url: data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTE0IDJINkMyLjY5IDIgMCA0LjY5IDAgOFYxOEMwIDIxLjMxIDIuNjkgMjQgNiAyNEgxOEMyMS4zMSAyNCAyNCAyMS4zMSAyNCAxOFY4TDE0IDJaIiBmaWxsPSIjNDA5RUZGIi8+CjxwYXRoIGQ9Ik0xNCAyVjhIMjQiIGZpbGw9IiM0MDlFRkYiLz4KPC9zdmc+
requirements: pdfplumber>=0.10.0,PyMuPDF>=1.23.0,python-docx>=1.1.0,reportlab>=4.0.0,Pillow>=10.0.0
"""

import asyncio
import base64
import os
import tempfile
from typing import Awaitable, Any, Callable, Optional, Dict
from pathlib import Path

# Import template functionality
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


class Action:
    """OpenWebUI Action for template upload and formatting"""

    def __init__(self):
        if TEMPLATE_SUPPORT:
            self.template_manager = TemplateManager()
            self.template_extractor = TemplateExtractor()
            self.pdf_generator = PDFGenerator()
        else:
            self.template_manager = None
            self.template_extractor = None
            self.pdf_generator = None

    async def action(
        self,
        body: dict,
        __user__=None,
        __event_emitter__=None,
        __event_call__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ):
        """
        Main action handler

        Actions:
        - upload_template: Upload and extract template from file
        - format_output: Format chat output using template
        - list_templates: List available templates
        """

        action_type = body.get("action", "upload_template")
        user_id = __user__.get("id") if __user__ else None

        if action_type == "upload_template":
            return await self._handle_template_upload(body, user_id, __event_call__)
        elif action_type == "format_output":
            return await self._handle_format_output(body, user_id, __event_emitter__, __event_call__)
        elif action_type == "list_templates":
            return await self._handle_list_templates(user_id)
        else:
            return {"error": f"Unknown action: {action_type}"}

    async def _handle_template_upload(
        self,
        body: dict,
        user_id: Optional[str],
        __event_call__: Optional[Callable]
    ) -> Dict[str, Any]:
        """Handle template upload and extraction"""
        if not TEMPLATE_SUPPORT:
            return {"error": "Template support not available. Check dependencies."}

        try:
            # Get file data from body
            # OpenWebUI passes files in different ways, check common patterns
            file_data = body.get("file") or body.get("file_data") or body.get("template_file")
            file_name = body.get("file_name") or body.get("filename", "template")
            template_name = body.get("template_name") or file_name.rsplit(".", 1)[0]

            # Determine file type
            if isinstance(file_name, str):
                if file_name.lower().endswith(".pdf"):
                    file_type = "pdf"
                elif file_name.lower().endswith(".docx"):
                    file_type = "docx"
                else:
                    return {"error": "Unsupported file type. Please upload PDF or DOCX."}
            else:
                file_type = body.get("file_type", "pdf")

            # Handle base64 encoded file
            if isinstance(file_data, str):
                if file_data.startswith("data:"):
                    # Data URL format: data:application/pdf;base64,...
                    file_data = file_data.split(",", 1)[1]
                file_bytes = base64.b64decode(file_data)
            elif isinstance(file_data, bytes):
                file_bytes = file_data
            else:
                return {"error": "Invalid file data format"}

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
                tmp_file.write(file_bytes)
                tmp_path = tmp_file.name

            try:
                # Extract template metadata
                if __event_call__:
                    await __event_call__({
                        "type": "execute",
                        "data": {
                            "code": """
                                if (window.templateUploadStatus) {
                                    window.templateUploadStatus.textContent = 'Extracting template formatting...';
                                }
                            """
                        }
                    })

                metadata = self.template_extractor.extract_template(tmp_path, file_type)

                # Save template
                template_id = self.template_manager.save_template(
                    template_name=template_name,
                    file_path=tmp_path,
                    metadata=metadata,
                    file_type=file_type,
                    user_id=user_id
                )

                # Get available templates for response
                templates = self.template_manager.list_templates(user_id=user_id)

                if __event_call__:
                    await __event_call__({
                        "type": "execute",
                        "data": {
                            "code": f"""
                                alert('Template "{template_name}" uploaded successfully!\\n\\nExtracted:\\n- {len(metadata.get("headers", []))} headers\\n- {len(metadata.get("tables", []))} tables\\n- {len(metadata.get("fonts", {}))} font styles');
                            """
                        }
                    })

                return {
                    "success": True,
                    "message": f"Template '{template_name}' uploaded and processed successfully",
                    "template_id": template_id,
                    "template_name": template_name,
                    "metadata": {
                        "headers": len(metadata.get("headers", [])),
                        "tables": len(metadata.get("tables", [])),
                        "fonts": len(metadata.get("fonts", {})),
                        "styles": len(metadata.get("styles", {}))
                    },
                    "templates": templates
                }

            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise e

        except Exception as e:
            import traceback
            return {
                "error": f"Error uploading template: {str(e)}",
                "traceback": traceback.format_exc()
            }

    async def _handle_format_output(
        self,
        body: dict,
        user_id: Optional[str],
        __event_emitter__: Optional[Callable],
        __event_call__: Optional[Callable]
    ) -> Dict[str, Any]:
        """Format chat output using selected template"""
        if not TEMPLATE_SUPPORT:
            return {"error": "Template support not available"}

        try:
            template_name = body.get("template_name")
            content = body.get("content") or body.get("text", "")

            if not template_name:
                return {"error": "template_name is required"}
            if not content:
                return {"error": "content is required"}

            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"Formatting content with template '{template_name}'...", "done": False}
                })

            # Get template info
            template_info = self.template_manager.get_template_info(template_name, user_id=user_id)
            if not template_info:
                return {"error": f"Template '{template_name}' not found"}

            # Generate PDF using template
            pdf_path = self.pdf_generator.generate_pdf(
                content=content,
                template_metadata=template_info["metadata"],
                template_file_path=template_info["file_path"],
                output_name=f"{template_name}_output.pdf"
            )

            # Read PDF and encode
            with open(pdf_path, "rb") as f:
                pdf_data = base64.b64encode(f.read()).decode("utf-8")

            # Clean up
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

            # Trigger download
            if __event_call__:
                await __event_call__({
                    "type": "execute",
                    "data": {
                        "code": self._get_download_script(pdf_data, f"{template_name}_formatted.pdf")
                    }
                })

            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": "Document formatted successfully!", "done": True}
                })

            return {
                "success": True,
                "message": "Document formatted successfully",
                "filename": f"{template_name}_formatted.pdf"
            }

        except Exception as e:
            import traceback
            return {
                "error": f"Error formatting document: {str(e)}",
                "traceback": traceback.format_exc()
            }

    async def _handle_list_templates(self, user_id: Optional[str]) -> Dict[str, Any]:
        """List available templates"""
        if not TEMPLATE_SUPPORT:
            return {"templates": []}

        templates = self.template_manager.list_templates(user_id=user_id)
        return {
            "templates": templates,
            "count": len(templates)
        }

    def _get_download_script(self, pdf_data: str, filename: str) -> str:
        """Generate JavaScript to download PDF"""
        return f"""
            const binary = atob('{pdf_data}');
            const buffer = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) buffer[i] = binary.charCodeAt(i);
            const blob = new Blob([buffer], {{type: 'application/pdf'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{filename}';
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(url);
            document.body.removeChild(a);
        """
