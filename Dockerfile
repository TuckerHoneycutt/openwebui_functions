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

# Create startup script that runs automatically on container start
# This ensures functions are copied to the correct location even if it's created at runtime
RUN cat > /app/startup-functions.sh << 'EOFSTARTUP'
#!/bin/bash
# This script runs automatically on container start to ensure functions are in the right place

# Find and copy functions to any newly created functions directories
FUNC_SOURCE="/app/functions"
FUNC_TARGETS=(
    "/app/backend/functions"
    "/app/open-webui/functions"
    "/root/.open-webui/functions"
    "$HOME/.open-webui/functions"
)

# Copy functions to any existing or newly created directories
for target in "${FUNC_TARGETS[@]}"; do
    if [ -d "$(dirname "$target")" ] 2>/dev/null || mkdir -p "$(dirname "$target")" 2>/dev/null; then
        mkdir -p "$target" 2>/dev/null || true
        cp -f "$FUNC_SOURCE"/*.py "$target/" 2>/dev/null || true
    fi
done

# Also search for any functions directories that might exist
FOUND_DIRS=$(find /app -name "functions" -type d 2>/dev/null || true)
for dir in $FOUND_DIRS; do
    if [ "$dir" != "$FUNC_SOURCE" ]; then
        cp -f "$FUNC_SOURCE"/*.py "$dir/" 2>/dev/null || true
    fi
done
EOFSTARTUP
RUN chmod +x /app/startup-functions.sh

# Create wrapper that runs startup script then preserves OpenWebUI's original entrypoint
# This ensures functions are available on every container start
RUN cat > /app/docker-entrypoint-wrapper.sh << 'EOFWRAPPER'
#!/bin/bash
# Run startup script to ensure functions are in place
/app/startup-functions.sh || true

# Preserve OpenWebUI's original entrypoint
# Check for common entrypoint locations
if [ -f /entrypoint.sh ]; then
    exec /entrypoint.sh "$@"
elif [ -f /app/entrypoint.sh ]; then
    exec /app/entrypoint.sh "$@"
elif [ -f /docker-entrypoint.sh ]; then
    exec /docker-entrypoint.sh "$@"
else
    # No entrypoint found - execute command directly (preserves CMD from base image)
    exec "$@"
fi
EOFWRAPPER
RUN chmod +x /app/docker-entrypoint-wrapper.sh

# Override entrypoint to use our wrapper
# This runs automatically on every container start
ENTRYPOINT ["/app/docker-entrypoint-wrapper.sh"]
