# Using current_main.py in OpenWebUI

## Overview

The modified `current_main.py` now includes template support for PDF generation while maintaining all existing functionality.

## Setup

### 1. Copy Required Files

Copy all these files to your OpenWebUI functions directory (usually `/app/functions/` or `~/.open-webui/functions/`):

- `current_main.py` (main function file)
- `template_extractor.py` (template extraction module)
- `template_manager.py` (template management module)
- `pdf_generator.py` (PDF generation module)

### 2. Install Dependencies

The requirements are listed in the file header:
```
python-docx>=1.1.0
pandas>=2.0.0
xhtml2pdf>=0.2.11
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
reportlab>=4.0.0
```

Install them:
```bash
pip install python-docx pandas xhtml2pdf pdfplumber PyMuPDF reportlab
```

### 3. Set Environment Variables (Optional)

For Docker deployments:
```bash
export TEMPLATE_STORAGE_DIR=/app/templates
export PDF_TEMP_DIR=/app/temp
```

## Features

### Existing Features (Still Work)
- ✅ DOCX generation with department selection
- ✅ PDF generation with department selection
- ✅ Markdown sanitization and parsing
- ✅ Enhanced text formatting
- ✅ Department-specific customization

### New Features
- ✅ Template upload functionality
- ✅ Template listing
- ✅ Template-based PDF generation (when templates are available)
- ✅ Template selection in export modal

## Usage

### Export Documents (Existing Functionality)

1. Get an AI response in chat
2. The function automatically triggers
3. Select department and optionally a template
4. Download DOCX or PDF

### Upload Templates (New)

To upload a template, you'll need to call the function with action `upload_template`. This can be done programmatically or through a custom UI.

Example API call:
```python
{
    "action": "upload_template",
    "template_name": "My Template",
    "template_file": "<base64_encoded_pdf_or_docx>",
    "file_type": "pdf"  # or "docx"
}
```

### List Templates (New)

```python
{
    "action": "list_templates"
}
```

## How It Works

1. **Default Mode**: Works exactly as before - generates DOCX/PDF with default formatting
2. **Template Mode**: When templates are available:
   - Templates appear in the export modal dropdown
   - Selecting a template uses template-based PDF generation
   - Falls back to default if template generation fails

## Template Support

The function gracefully handles missing template modules:
- If template modules aren't available, it works in default mode
- Template features are automatically disabled if imports fail
- No errors are thrown if templates aren't configured

## File Structure

```
open-webui/functions/
├── current_main.py          # Main function (this file)
├── template_extractor.py    # Template extraction
├── template_manager.py      # Template storage/retrieval
└── pdf_generator.py         # PDF generation with templates
```

## Troubleshooting

### Templates Not Appearing

1. Check that all template modules are in the same directory
2. Verify imports work: `python3 -c "from template_extractor import TemplateExtractor"`
3. Check OpenWebUI logs for import errors

### Template Generation Fails

- Falls back to default PDF generation automatically
- Check that template files are valid PDF/DOCX
- Verify template metadata was extracted correctly

### Import Errors

If you see import errors:
```bash
# Install missing packages
pip install pdfplumber PyMuPDF python-docx reportlab

# Verify imports
python3 -c "import template_extractor; import template_manager; import pdf_generator"
```

## Notes

- Template functionality is optional - the function works without it
- All existing functionality is preserved
- Templates are user-specific (if user context is available)
- Template storage uses environment variables for Docker compatibility
