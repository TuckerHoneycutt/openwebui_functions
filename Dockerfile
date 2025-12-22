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

# Copy function files to multiple possible locations during build
# OpenWebUI may load functions from different directories depending on version
COPY template_function.py template_action.py template_extractor.py pdf_generator.py template_manager.py /app/functions/
COPY template_function.py template_action.py template_extractor.py pdf_generator.py template_manager.py /app/custom-functions/
COPY verify_setup.py /app/

# Create all possible functions directories and copy functions there during build
# This ensures functions are available regardless of where OpenWebUI looks
RUN mkdir -p /app/backend/functions && \
    mkdir -p /app/open-webui/functions && \
    mkdir -p /root/.open-webui/functions && \
    cp /app/functions/template_function.py /app/backend/functions/ && \
    cp /app/functions/template_extractor.py /app/backend/functions/ && \
    cp /app/functions/template_manager.py /app/backend/functions/ && \
    cp /app/functions/pdf_generator.py /app/backend/functions/ && \
    cp /app/functions/template_action.py /app/backend/functions/ && \
    cp /app/functions/template_function.py /app/open-webui/functions/ && \
    cp /app/functions/template_extractor.py /app/open-webui/functions/ && \
    cp /app/functions/template_manager.py /app/open-webui/functions/ && \
    cp /app/functions/pdf_generator.py /app/open-webui/functions/ && \
    cp /app/functions/template_action.py /app/open-webui/functions/ && \
    cp /app/functions/template_function.py /root/.open-webui/functions/ && \
    cp /app/functions/template_extractor.py /root/.open-webui/functions/ && \
    cp /app/functions/template_manager.py /root/.open-webui/functions/ && \
    cp /app/functions/pdf_generator.py /root/.open-webui/functions/ && \
    cp /app/functions/template_action.py /root/.open-webui/functions/ && \
    chmod -R 755 /app/functions /app/backend/functions /app/open-webui/functions /root/.open-webui/functions

# Functions are copied to all possible locations during build
# This ensures they're available regardless of where OpenWebUI looks
# No entrypoint override needed - OpenWebUI will start normally and find functions
# If OpenWebUI creates a new functions directory at runtime, functions can be manually copied
# or you can mount /app/functions as a volume to the functions directory
