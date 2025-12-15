# OpenWebUI PDF Template Formatter

A custom OpenWebUI function that formats AI-generated responses into PDFs using user-uploaded templates. The function extracts formatting metadata (headers, fonts, tables, page breaks, etc.) from templates and applies it to generated content, creating PDFs that match the original template formatting exactly.

## Features

- **Template Upload**: Upload PDF or DOCX templates
- **Formatting Extraction**: Automatically extracts:
  - Headers and footers
  - Page breaks
  - Fonts and text sizes
  - Numbering and bullets
  - Tables
  - Styles and formatting
  - Margins and page sizes
- **Template Selection**: Choose from multiple uploaded templates
- **PDF Generation**: Generate PDFs with identical formatting to templates
- **User Isolation**: Support for user-specific templates

## Installation

### For Docker Deployment (Recommended)

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker setup instructions.

Quick start:
```bash
# Build custom image with dependencies
docker build -t open-webui-pdf-formatter .

# Run with docker-compose
docker-compose up -d
```

### For Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place the function files in your OpenWebUI functions directory:
   - Copy `functions.py`, `template_extractor.py`, `pdf_generator.py`, and `template_manager.py` to your OpenWebUI functions directory
   - Typically located at: `~/.open-webui/functions/` or your OpenWebUI installation directory

3. Ensure the templates directory is writable:
```bash
mkdir -p templates
chmod 755 templates
```

4. Set environment variables (optional):
```bash
export TEMPLATE_STORAGE_DIR=./templates
export PDF_TEMP_DIR=./temp
```

## Usage

### Upload a Template

Use the function with action `upload_template`:

```json
{
  "action": "upload_template",
  "template_name": "My Template",
  "template_file": "<base64_encoded_file>",
  "file_type": "pdf"
}
```

### List Available Templates

```json
{
  "action": "list_templates"
}
```

### Get Template Information

```json
{
  "action": "get_template_info",
  "template_name": "My Template"
}
```

### Generate PDF from Template

After receiving an AI response, format it using a template:

```json
{
  "action": "generate_pdf",
  "template_name": "My Template",
  "content": "Your AI-generated content here..."
}
```

The function will return a base64-encoded PDF that matches your template's formatting.

## Function Schema

The function exposes the following actions:

- **upload_template**: Upload and extract metadata from a template file
- **list_templates**: List all available templates
- **get_template_info**: Get detailed information about a template
- **generate_pdf**: Generate a PDF from content using a template

## How It Works

1. **Template Extraction**: When you upload a template, the system extracts all formatting metadata including fonts, styles, page layout, tables, headers, etc.

2. **Metadata Storage**: The extracted metadata is stored along with the template file for future use.

3. **Content Formatting**: When generating a PDF, the system:
   - Parses your content (supports markdown-style headers, lists, etc.)
   - Applies the template's formatting metadata
   - Generates a PDF matching the original template's appearance

4. **Format Preservation**: The generated PDF maintains:
   - Same fonts and sizes
   - Same page layout and margins
   - Same header/footer styles
   - Same table formatting
   - Same overall document structure

## Supported File Types

- **PDF**: Full support for PDF templates using pdfplumber or PyMuPDF
- **DOCX**: Full support for Word document templates using python-docx

## Content Formatting

The system supports markdown-style formatting in your content:

- Headers: `# Header 1`, `## Header 2`, etc.
- Bullet lists: Lines starting with `-` or `*`
- Numbered lists: Lines starting with numbers
- Regular paragraphs: Plain text

## Template Storage

Templates are stored in the `templates/` directory with metadata stored in `templates/metadata.json`. User-specific templates are stored in `templates/user_{user_id}/` directories.

## Requirements

- Python 3.8+
- OpenWebUI installed and configured
- Required Python packages (see requirements.txt)

## Troubleshooting

### Font Issues
If fonts don't match exactly, the system falls back to standard fonts (Helvetica, Times-Roman, Courier). For exact font matching, ensure fonts are available on your system.

### PDF Generation Errors
Make sure reportlab is properly installed:
```bash
pip install reportlab --upgrade
```

### Template Not Found
Ensure template names match exactly (case-sensitive). Use `list_templates` to see available templates.

## License

This project is provided as-is for use with OpenWebUI.
