# OpenWebUI Integration Guide

## Setting Up the Function in OpenWebUI

### Method 1: Direct Function File

1. Copy all Python files to your OpenWebUI functions directory:
   ```bash
   cp functions.py template_extractor.py pdf_generator.py template_manager.py /path/to/open-webui/functions/
   ```

2. OpenWebUI should automatically detect the function. The function will appear in the functions list.

### Method 2: Custom Functions Directory

If your OpenWebUI uses a custom functions directory:

1. Create a directory for this function:
   ```bash
   mkdir -p ~/.open-webui/functions/pdf_template_formatter
   ```

2. Copy all files:
   ```bash
   cp *.py ~/.open-webui/functions/pdf_template_formatter/
   ```

3. Ensure OpenWebUI is configured to load functions from this directory.

## Function Registration

The function is registered via the `get_function_schema()` function which returns the OpenWebUI function schema. The main handler is `format_to_pdf_template()`.

## Usage in OpenWebUI Chat

### Example 1: Upload a Template

User message:
```
Upload a template called "Business Report" from the attached PDF
```

The function will be called with:
```json
{
  "action": "upload_template",
  "template_name": "Business Report",
  "template_file": "<base64_encoded_pdf>",
  "file_type": "pdf"
}
```

### Example 2: Generate PDF from Response

After getting an AI response, the user can say:
```
Format this response using the "Business Report" template
```

The function will be called with:
```json
{
  "action": "generate_pdf",
  "template_name": "Business Report",
  "content": "<AI generated content>"
}
```

### Example 3: List Templates

User message:
```
Show me all available templates
```

Function call:
```json
{
  "action": "list_templates"
}
```

## Advanced Usage

### User-Specific Templates

The function supports user isolation. When calling the function, pass `user_id` parameter:

```python
await format_to_pdf_template(
    action="upload_template",
    template_name="Personal Template",
    template_file=file_data,
    file_type="pdf",
    user_id="user123"
)
```

### Programmatic Usage

You can also call the function programmatically in custom OpenWebUI workflows:

```python
from functions import format_to_pdf_template

# Upload template
result = await format_to_pdf_template(
    action="upload_template",
    template_name="My Template",
    template_file=base64_file_data,
    file_type="pdf"
)

# Generate PDF
result = await format_to_pdf_template(
    action="generate_pdf",
    template_name="My Template",
    content="Your content here..."
)

pdf_data = result["pdf_data"]  # Base64 encoded PDF
```

## Configuration

### Storage Location

Templates are stored in the `templates/` directory relative to where the function is executed. To change this:

1. Modify `template_manager.py`:
   ```python
   template_manager = TemplateManager(storage_dir="/custom/path/templates")
   ```

### Permissions

Ensure the templates directory is writable:
```bash
chmod 755 templates
```

## Troubleshooting

### Function Not Appearing

1. Check that all files are in the correct directory
2. Verify Python syntax is correct: `python -m py_compile functions.py`
3. Check OpenWebUI logs for import errors

### Import Errors

Install all dependencies:
```bash
pip install -r requirements.txt
```

### Template Extraction Fails

- For PDFs: Ensure pdfplumber or PyMuPDF is installed
- For DOCX: Ensure python-docx is installed
- Check file permissions on template files

### PDF Generation Issues

- Verify reportlab is installed: `pip install reportlab`
- Check that fonts are available on your system
- Review template metadata extraction for completeness

## API Reference

### Function Parameters

- `action` (required): One of `upload_template`, `list_templates`, `get_template_info`, `generate_pdf`
- `template_name` (optional): Name of template (required for some actions)
- `content` (optional): Content to format (required for `generate_pdf`)
- `template_file` (optional): Base64 encoded file (required for `upload_template`)
- `file_type` (optional): `pdf` or `docx` (required for `upload_template`)
- `user_id` (optional): User ID for template isolation

### Return Format

All functions return a dictionary with:
- `success` (bool): Whether the operation succeeded
- `error` (str, optional): Error message if failed
- Additional fields depending on action

## Example Workflow

1. User uploads a PDF template via OpenWebUI
2. Function extracts formatting metadata
3. User asks AI a question
4. AI generates response
5. User requests PDF formatting
6. Function applies template formatting to response
7. PDF is generated and returned to user

This creates a seamless workflow where users can format AI responses to match their document templates.
