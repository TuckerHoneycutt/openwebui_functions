# Template Workflow Implementation

## How It Works

The modified `current_main.py` now implements the following workflow:

1. **User clicks the export button** → Function is triggered
2. **Template Selection Modal appears** with:
   - Dropdown to select existing templates
   - File upload to add new templates
   - Department selection
   - Generate button

3. **When user uploads a template**:
   - File is read as base64
   - Template name is entered
   - On "Generate" click, template is uploaded first, then document is generated

4. **When user selects existing template**:
   - Template is used directly for document generation

5. **Document Generation**:
   - If template selected: Content is overlaid on template PDF, preserving:
     - Images
     - Watermarks
     - Headers and footers
     - Fonts and formatting
     - Page layout
   - If no template: Uses default formatting

## Key Features

- **Template Upload**: Upload PDF or DOCX templates
- **Template Parsing**: Extracts formatting metadata including:
  - Fonts and sizes
  - Headers and footers
  - Images and watermarks
  - Page layout
  - Tables and formatting
- **Content Overlay**: New content is placed on template while preserving visual elements
- **Fallback**: If template processing fails, falls back to default formatting

## Usage Flow

1. Get AI response in chat
2. Click export function button
3. Modal appears:
   - Select existing template OR
   - Upload new template (PDF/DOCX)
   - Select department
   - Click "Generate Document"
4. Document downloads with template formatting applied

## Technical Implementation

### Template Upload
- Files are stored in `templates/` directory
- Metadata extracted and stored in `metadata.json`
- Images and watermarks extracted and stored

### PDF Generation with Template
- Uses PyMuPDF to overlay content on template
- Template page is copied as background
- New content is inserted in content areas
- All visual elements (images, watermarks) are preserved

### DOCX Generation with Template
- Opens template DOCX
- Inserts content while preserving template structure
- Converts to PDF if possible

## Files Required

- `current_main.py` - Main function file
- `template_extractor.py` - Extracts template metadata
- `template_manager.py` - Manages template storage
- `pdf_generator.py` - Generates PDFs with templates

## Dependencies

```
python-docx>=1.1.0
pandas>=2.0.0
xhtml2pdf>=0.2.11
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
reportlab>=4.0.0
```

## Notes

- Templates are user-specific (if user context available)
- Template storage uses environment variables for Docker compatibility
- Falls back gracefully if template processing fails
- All existing functionality is preserved
