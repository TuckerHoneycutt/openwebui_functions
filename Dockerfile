# Custom OpenWebUI Dockerfile with PDF Template Formatter dependencies
FROM ghcr.io/open-webui/open-webui:main

# Install system dependencies for PDF/DOCX processing
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for PDF template formatter
# These are installed during build so they persist across rebuilds
RUN pip install --no-cache-dir \
    pdfplumber>=0.10.0 \
    PyMuPDF>=1.23.0 \
    python-docx>=1.1.0 \
    reportlab>=4.0.0 \
    Pillow>=10.0.0

# Create directories for templates and temp files
RUN mkdir -p /app/templates /app/temp /app/custom-functions /app/functions

# Set environment variables for template storage
ENV TEMPLATE_STORAGE_DIR=/app/templates
ENV PDF_TEMP_DIR=/app/temp

# Copy function files to custom-functions directory
# These will be automatically installed to the functions directory on container start
COPY template_function.py template_action.py template_extractor.py pdf_generator.py template_manager.py /app/custom-functions/
COPY verify_setup.py /app/

# Copy entrypoint script that handles automatic installation
COPY entrypoint.sh /app/entrypoint-template.sh

# Set permissions
RUN chmod -R 755 /app/templates /app/temp /app/custom-functions /app/verify_setup.py /app/entrypoint-template.sh

# Create init script that will be run on container start
# This script installs functions automatically every time the container starts
RUN cat > /app/init-template-functions.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

echo "=========================================="
echo "Installing Template Formatter Functions"
echo "=========================================="

# Find and create functions directory
FUNC_DIRS=("/app/functions" "/app/backend/functions" "/root/.open-webui/functions")
FOUND=""
for dir in "${FUNC_DIRS[@]}"; do
  if mkdir -p "$dir" 2>/dev/null; then
    FOUND="$dir"
    break
  fi
done
if [ -z "$FOUND" ]; then
  FOUND="/app/functions"
  mkdir -p "$FOUND"
fi

# Copy function files
if [ -d "/app/custom-functions" ]; then
  echo "Copying functions to $FOUND..."
  cp -f /app/custom-functions/template_function.py "$FOUND/" 2>/dev/null || true
  cp -f /app/custom-functions/template_extractor.py "$FOUND/" 2>/dev/null || true
  cp -f /app/custom-functions/template_manager.py "$FOUND/" 2>/dev/null || true
  cp -f /app/custom-functions/pdf_generator.py "$FOUND/" 2>/dev/null || true
  cp -f /app/custom-functions/template_action.py "$FOUND/" 2>/dev/null || true
  echo "✓ Functions installed to $FOUND"
  ls -lh "$FOUND"/*.py 2>/dev/null | grep -E "template|pdf_generator" || true
fi

# Verify dependencies
echo ""
echo "Verifying dependencies..."
python3 -c "import pdfplumber" 2>/dev/null && echo "✓ pdfplumber" || echo "✗ pdfplumber"
python3 -c "import fitz" 2>/dev/null && echo "✓ PyMuPDF" || echo "✗ PyMuPDF"
python3 -c "from docx import Document" 2>/dev/null && echo "✓ python-docx" || echo "✗ python-docx"
python3 -c "from reportlab.lib.pagesizes import letter" 2>/dev/null && echo "✓ reportlab" || echo "✗ reportlab"
python3 -c "from PIL import Image" 2>/dev/null && echo "✓ Pillow" || echo "✗ Pillow"

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
EOFSCRIPT
RUN chmod +x /app/init-template-functions.sh

# Note: The init script will be called via docker-compose entrypoint override
# This ensures functions are installed every time the container starts,
# even after rebuilds with --no-cache
