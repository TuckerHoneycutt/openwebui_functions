# OpenWebUI Template Formatter

A complete solution for uploading PDF/DOCX templates and formatting AI-generated chat content to match your document templates exactly.

## 🎯 What This Does

1. **Upload Templates**: Upload PDF or DOCX files and extract all formatting details (headers, fonts, sizes, layout, margins, etc.)
2. **Format Output**: Take any AI-generated content and format it into a PDF matching your template's styling
3. **Preserve Layout**: Maintains fonts, text sizes, margins, page layout, headers, footers, and more

## 🚀 Quick Start

### 1. Build and Start Docker Container

```bash
# Build the custom image
docker build -t open-webui-template-formatter .

# Start with docker-compose
docker-compose up -d
```

### 2. Install Functions into Container

```bash
# Run the installation script
./install_functions.sh

# Or manually copy files
docker exec -it open-webui-template-formatter cp /app/custom-functions/*.py /app/functions/
```

### 3. Restart Container

```bash
docker-compose restart
```

### 4. Use in OpenWebUI

1. **Upload a template**: Attach a PDF/DOCX file and say "Upload this as template 'My Template'"
2. **List templates**: Say "List all templates"
3. **Format content**: After getting AI output, say "Format this using the 'My Template' template"

## 📋 How It Works

### Template Extraction Process

When you upload a template (PDF or DOCX), the system:

1. **Analyzes the document structure**:
   - Identifies headers and footers (position, text, styling)
   - Extracts all fonts and text sizes used
   - Maps paragraph styles and formatting
   - Identifies tables and their structure
   - Captures page layout (margins, size, orientation)

2. **Stores metadata**:
   - Saves the original template file
   - Stores extracted formatting metadata as JSON
   - Creates a template entry you can reference by name

### Content Formatting Process

When formatting content:

1. **Parses your content**:
   - Recognizes markdown headings (# ## ###)
   - Identifies lists (bulleted and numbered)
   - Detects tables
   - Processes paragraphs

2. **Applies template styling**:
   - Maps headings to template heading styles (font, size)
   - Applies template body text styles to paragraphs
   - Uses template fonts and sizes throughout
   - Maintains template page size and margins
   - Preserves template layout structure

3. **Generates PDF**:
   - Creates PDF matching template formatting exactly
   - Downloads automatically

## 📁 File Structure

```
openwebui_functions/
├── template_function.py      # Main function (chat interface)
├── template_action.py         # Action/button interface (optional)
├── template_extractor.py      # Extracts formatting from PDF/DOCX
├── template_manager.py        # Manages template storage
├── pdf_generator.py           # Generates formatted PDFs
├── Dockerfile                 # Custom Docker image
├── docker-compose.yml         # Docker configuration
├── install_functions.sh       # Installation script
├── SETUP_GUIDE.md            # Detailed setup instructions
└── templates/                # Template storage (auto-created)
    ├── metadata.json         # Template index
    └── user_*/              # User-specific templates
```

## 💡 Usage Examples

### Upload Template

**Method 1: Chat**
```
Attach: report_template.pdf
Message: "Upload this as a template named 'Company Report'"
```

**Method 2: Function Call**
```
Use function manage_document_template with:
- action: "upload_template"
- template_name: "Company Report"
```

### List Templates

```
Message: "List all available templates"
```

### Format Content

```
Message: "Format this content using the 'Company Report' template"
```

## 🔧 Configuration

### Environment Variables

Set in `docker-compose.yml`:

- `TEMPLATE_STORAGE_DIR`: Where templates are stored (default: `/app/templates`)
- `PDF_TEMP_DIR`: Where temporary PDFs are created (default: `/app/temp`)

### Storage Locations

- **Templates**: `/app/templates/` (persisted via Docker volume)
- **Metadata**: `/app/templates/metadata.json`
- **User Templates**: `/app/templates/user_<user_id>/`

## 🐛 Troubleshooting

### Function Not Appearing

1. Check files are copied:
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/functions/ | grep template
   ```

2. Check logs:
   ```bash
   docker logs open-webui-template-formatter | grep -i template
   ```

3. Verify syntax:
   ```bash
   docker exec -it open-webui-template-formatter python3 -m py_compile /app/functions/template_function.py
   ```

### Import Errors

Install dependencies:
```bash
docker exec -it open-webui-template-formatter pip install pdfplumber PyMuPDF python-docx reportlab Pillow
```

### Template Upload Fails

1. Check permissions:
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/templates/
   ```

2. Check disk space:
   ```bash
   docker exec -it open-webui-template-formatter df -h
   ```

## 📚 Detailed Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[INTEGRATION.md](INTEGRATION.md)** - Integration details (if exists)

## 🎨 Features

✅ **PDF Template Support** - Extract formatting from PDF files
✅ **DOCX Template Support** - Extract formatting from Word documents
✅ **Font Preservation** - Maintains original fonts and sizes
✅ **Layout Preservation** - Keeps margins, page size, orientation
✅ **Header/Footer Support** - Preserves document headers and footers
✅ **Table Formatting** - Maintains table structure and styling
✅ **User Isolation** - Templates can be user-specific
✅ **Session Storage** - Templates stored per session/user
✅ **Easy Upload** - Simple file attachment workflow

## 🔐 Security Notes

- Templates are stored per-user when user authentication is available
- Global templates are accessible to all users
- File uploads are validated (PDF/DOCX only)
- Temporary files are cleaned up after processing

## 📝 Requirements

- Docker and Docker Compose
- OpenWebUI (hosted in Docker)
- Python dependencies (installed in Docker image):
  - pdfplumber >= 0.10.0
  - PyMuPDF >= 1.23.0
  - python-docx >= 1.1.0
  - reportlab >= 4.0.0
  - Pillow >= 10.0.0

## 🤝 Support

For issues:
1. Check container logs: `docker logs open-webui-template-formatter`
2. Verify dependencies: `docker exec -it open-webui-template-formatter pip list`
3. Check template storage: `docker exec -it open-webui-template-formatter ls -la /app/templates/`

## 📄 License

Use as needed for your OpenWebUI instance.
