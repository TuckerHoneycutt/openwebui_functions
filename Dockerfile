# Custom OpenWebUI Dockerfile with PDF Template Formatter dependencies
FROM ghcr.io/open-webui/open-webui:main

# Install system dependencies for PDF/DOCX processing
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for PDF template formatter
RUN pip install --no-cache-dir \
    pdfplumber>=0.10.0 \
    PyMuPDF>=1.23.0 \
    python-docx>=1.1.0 \
    reportlab>=4.0.0 \
    Pillow>=10.0.0

# Create directories for templates and temp files
RUN mkdir -p /app/templates /app/temp

# Set environment variables for template storage
ENV TEMPLATE_STORAGE_DIR=/app/templates
ENV PDF_TEMP_DIR=/app/temp

# Copy function files to OpenWebUI functions directory
# OpenWebUI typically loads functions from /app/functions/ or ~/.open-webui/functions/
# We'll copy to a custom location and mount as volume for easier updates
COPY template_function.py template_action.py template_extractor.py pdf_generator.py template_manager.py /app/custom-functions/
COPY verify_setup.py /app/

# Set permissions
RUN chmod -R 755 /app/templates /app/temp /app/custom-functions /app/verify_setup.py

# Note: After container starts, copy files to OpenWebUI functions directory:
# docker exec -it <container> cp /app/custom-functions/*.py /app/functions/ 2>/dev/null || \
# docker exec -it <container> mkdir -p ~/.open-webui/functions && cp /app/custom-functions/*.py ~/.open-webui/functions/
