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

# Copy function files directly to OpenWebUI functions directory during build
# This avoids needing runtime installation and entrypoint overrides
# Try common OpenWebUI function directories - copy to all possible locations
COPY template_function.py template_action.py template_extractor.py pdf_generator.py template_manager.py /app/functions/
COPY template_function.py template_action.py template_extractor.py pdf_generator.py template_manager.py /app/custom-functions/
COPY verify_setup.py /app/

# Copy entrypoint script that handles automatic installation
COPY entrypoint.sh /app/entrypoint-template.sh

# Set permissions
RUN chmod -R 755 /app/templates /app/temp /app/custom-functions /app/verify_setup.py /app/entrypoint-template.sh

# Functions are copied directly to /app/functions/ during build
# This avoids needing runtime installation and entrypoint overrides
# If OpenWebUI uses a different functions directory, you can:
# 1. Run manually: docker exec -it <container> cp /app/functions/*.py /path/to/functions/
# 2. Or mount /app/functions as a volume to the correct location
