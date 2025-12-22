# OpenWebUI Template Formatter - Setup Guide

This guide walks you through setting up the template formatter functionality in your Docker-hosted OpenWebUI instance.

## Overview

The template formatter allows you to:
1. **Upload PDF/DOCX templates** - Extract formatting (headers, fonts, layout, etc.) from documents
2. **Format chat output** - Apply template formatting to AI-generated content
3. **Preserve styling** - Maintain fonts, sizes, margins, and layout from your templates

## Architecture

The solution consists of:
- **Template Extractor** (`template_extractor.py`) - Extracts formatting metadata from PDF/DOCX files
- **Template Manager** (`template_manager.py`) - Manages template storage and retrieval
- **PDF Generator** (`pdf_generator.py`) - Generates PDFs matching template formatting
- **OpenWebUI Function** (`template_function.py`) - Chat-based interface for template operations
- **OpenWebUI Action** (`template_action.py`) - UI button/action interface (optional)

## Docker Setup

### Step 1: Build the Custom Docker Image

```bash
cd /path/to/openwebui_functions
docker build -t open-webui-template-formatter .
```

### Step 2: Update docker-compose.yml

Make sure your `docker-compose.yml` includes volume mounts for templates:

```yaml
version: '3.8'

services:
  open-webui:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: open-webui-template-formatter
    ports:
      - "3000:8080"
    volumes:
      - open-webui-data:/app/backend/data
      # Persist templates across container restarts
      - ./templates:/app/templates
      # Temp directory for generated PDFs
      - ./temp:/app/temp
      # Mount custom functions (optional, for easier updates)
      - ./custom-functions:/app/custom-functions
    environment:
      - TEMPLATE_STORAGE_DIR=/app/templates
      - PDF_TEMP_DIR=/app/temp
    restart: unless-stopped

volumes:
  open-webui-data:
```

### Step 3: Start the Container

```bash
docker-compose up -d
```

### Step 4: Copy Functions to OpenWebUI Functions Directory

OpenWebUI loads functions from specific directories. Copy the function files:

```bash
# Find the correct functions directory
docker exec -it open-webui-template-formatter ls -la /app/functions/ 2>/dev/null || \
docker exec -it open-webui-template-formatter ls -la ~/.open-webui/functions/ 2>/dev/null

# Copy files (adjust path based on output above)
docker exec -it open-webui-template-formatter cp /app/custom-functions/template_function.py /app/functions/ 2>/dev/null || \
docker exec -it open-webui-template-formatter mkdir -p ~/.open-webui/functions && \
docker exec -it open-webui-template-formatter cp /app/custom-functions/*.py ~/.open-webui/functions/
```

**Alternative**: If OpenWebUI supports loading from `/app/custom-functions/`, you may not need to copy files. Check your OpenWebUI configuration.

### Step 5: Restart OpenWebUI

```bash
docker-compose restart
```

## Usage

### Method 1: Using Chat Function (Recommended)

The function `manage_document_template` is available in chat. Here's how to use it:

#### Upload a Template

1. **Attach a PDF or DOCX file** to your message in OpenWebUI
2. **Send a message** like:
   ```
   Upload this as a template named "Business Report"
   ```
   Or explicitly call the function:
   ```
   Use function manage_document_template with action=upload_template, template_name="Business Report"
   ```

#### List Templates

Send a message:
```
List all available templates
```
Or:
```
Use function manage_document_template with action=list_templates
```

#### Format Output Using Template

After getting an AI response:
```
Format this content using the "Business Report" template
```
Or:
```
Use function manage_document_template with action=format_output, template_name="Business Report"
```

### Method 2: Using Action Button (If Configured)

If you've set up the Action (`template_action.py`):

1. Look for a **"Template"** or **"Format Document"** button in the message toolbar
2. Click it to open a modal
3. Upload a template or select an existing one
4. Format your content

## How It Works

### Template Extraction

When you upload a template, the system extracts:

- **Headers and Footers** - Position, text, font, size
- **Fonts** - Font families and sizes used throughout
- **Text Sizes** - Different text sizes and their usage
- **Tables** - Structure, borders, cell formatting
- **Page Layout** - Margins, page size, orientation
- **Styles** - Paragraph styles, heading styles
- **Page Breaks** - Where pages break

### Content Formatting

When formatting content:

1. The system parses your chat content (markdown, headings, lists, etc.)
2. It maps content elements to template styles:
   - Headings → Template heading styles
   - Paragraphs → Template body text styles
   - Lists → Template list styles
   - Tables → Template table styles
3. It generates a PDF matching:
   - Page size and margins from template
   - Fonts and sizes from template
   - Layout structure from template

### Template Storage

- Templates are stored in `/app/templates/` (persisted via Docker volume)
- Each template includes:
  - Original file (PDF/DOCX)
  - Extracted metadata (JSON)
  - Template ID and name
- User-specific templates are stored in `user_<user_id>/` subdirectories

## Troubleshooting

### Function Not Appearing

1. **Check function files are in the right location:**
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/functions/
   ```

2. **Check OpenWebUI logs:**
   ```bash
   docker logs open-webui-template-formatter | grep -i template
   ```

3. **Verify Python syntax:**
   ```bash
   docker exec -it open-webui-template-formatter python3 -m py_compile /app/functions/template_function.py
   ```

### Import Errors

If you see import errors:

1. **Check dependencies are installed:**
   ```bash
   docker exec -it open-webui-template-formatter pip list | grep -E "pdfplumber|PyMuPDF|python-docx|reportlab"
   ```

2. **Reinstall if needed:**
   ```bash
   docker exec -it open-webui-template-formatter pip install pdfplumber PyMuPDF python-docx reportlab Pillow
   ```

### Template Upload Fails

1. **Check file permissions:**
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/templates/
   ```

2. **Check disk space:**
   ```bash
   docker exec -it open-webui-template-formatter df -h
   ```

3. **Check logs for specific errors:**
   ```bash
   docker logs open-webui-template-formatter | tail -50
   ```

### PDF Generation Issues

1. **Verify template metadata was extracted:**
   - Check `/app/templates/metadata.json`
   - Look for template entries

2. **Check temp directory:**
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/temp/
   ```

3. **Test PDF generation manually:**
   ```bash
   docker exec -it open-webui-template-formatter python3 -c "from pdf_generator import PDFGenerator; print('OK')"
   ```

## File Structure

```
openwebui_functions/
├── template_function.py      # Main OpenWebUI function (chat interface)
├── template_action.py         # OpenWebUI action (UI button, optional)
├── template_extractor.py      # Template extraction logic
├── template_manager.py        # Template storage/retrieval
├── pdf_generator.py           # PDF generation with template formatting
├── Dockerfile                 # Custom Docker image
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
└── templates/                # Template storage (created automatically)
    ├── metadata.json          # Template metadata index
    └── user_*/                # User-specific templates
```

## Advanced Configuration

### Custom Template Storage Location

Set environment variable:
```yaml
environment:
  - TEMPLATE_STORAGE_DIR=/custom/path/templates
```

### Custom Temp Directory

```yaml
environment:
  - PDF_TEMP_DIR=/custom/path/temp
```

### User Isolation

Templates are automatically isolated by user ID when available. Global templates are accessible to all users.

## Example Workflow

1. **Upload Template:**
   - User attaches `report_template.pdf`
   - Sends: "Upload this as template 'Company Report'"
   - System extracts formatting and stores template

2. **Generate Content:**
   - User asks AI: "Write a quarterly report"
   - AI generates markdown content

3. **Format Output:**
   - User: "Format this using the 'Company Report' template"
   - System generates PDF matching template formatting
   - PDF downloads automatically

## Support

For issues or questions:
1. Check OpenWebUI logs: `docker logs open-webui-template-formatter`
2. Verify all dependencies are installed
3. Check file permissions and disk space
4. Review template metadata in `/app/templates/metadata.json`
