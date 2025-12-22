#!/bin/bash
# Entrypoint script to automatically install functions on container start

set -e

echo "=========================================="
echo "OpenWebUI Template Formatter Setup"
echo "=========================================="

# Function to copy files to OpenWebUI functions directory
install_functions() {
    echo "Installing template functions..."

    # Try common OpenWebUI function directories
    FUNCTION_DIRS=(
        "/app/functions"
        "/app/backend/functions"
        "/root/.open-webui/functions"
        "$HOME/.open-webui/functions"
    )

    FOUND_DIR=""

    for dir in "${FUNCTION_DIRS[@]}"; do
        if [ -d "$(dirname "$dir")" ] 2>/dev/null || mkdir -p "$(dirname "$dir")" 2>/dev/null; then
            mkdir -p "$dir" 2>/dev/null || true
            if [ -w "$dir" ] 2>/dev/null || [ -w "$(dirname "$dir")" ] 2>/dev/null; then
                FOUND_DIR="$dir"
                echo "Found functions directory: $dir"
                break
            fi
        fi
    done

    if [ -z "$FOUND_DIR" ]; then
        # Create default location
        FOUND_DIR="/app/functions"
        mkdir -p "$FOUND_DIR"
        echo "Created functions directory: $FOUND_DIR"
    fi

    # Copy function files
    if [ -d "/app/custom-functions" ]; then
        echo "Copying function files from /app/custom-functions to $FOUND_DIR..."
        cp -f /app/custom-functions/template_function.py "$FOUND_DIR/" 2>/dev/null || true
        cp -f /app/custom-functions/template_extractor.py "$FOUND_DIR/" 2>/dev/null || true
        cp -f /app/custom-functions/template_manager.py "$FOUND_DIR/" 2>/dev/null || true
        cp -f /app/custom-functions/pdf_generator.py "$FOUND_DIR/" 2>/dev/null || true

        # Also copy action file if it exists
        if [ -f "/app/custom-functions/template_action.py" ]; then
            cp -f /app/custom-functions/template_action.py "$FOUND_DIR/" 2>/dev/null || true
        fi

        echo "✓ Functions installed to $FOUND_DIR"

        # List installed files
        echo "Installed files:"
        ls -lh "$FOUND_DIR"/*.py 2>/dev/null | grep -E "template|pdf_generator" || echo "  (checking...)"

    else
        echo "Warning: /app/custom-functions directory not found"
    fi
}

# Function to verify Python dependencies
verify_dependencies() {
    echo ""
    echo "Verifying Python dependencies..."

    python3 -c "import pdfplumber" 2>/dev/null && echo "✓ pdfplumber" || echo "✗ pdfplumber - MISSING"
    python3 -c "import fitz" 2>/dev/null && echo "✓ PyMuPDF (fitz)" || echo "✗ PyMuPDF - MISSING"
    python3 -c "from docx import Document" 2>/dev/null && echo "✓ python-docx" || echo "✗ python-docx - MISSING"
    python3 -c "from reportlab.lib.pagesizes import letter" 2>/dev/null && echo "✓ reportlab" || echo "✗ reportlab - MISSING"
    python3 -c "from PIL import Image" 2>/dev/null && echo "✓ Pillow" || echo "✗ Pillow - MISSING"
}

# Function to verify function files
verify_functions() {
    echo ""
    echo "Verifying function files..."

    # Try to import the function
    python3 -c "
import sys
sys.path.insert(0, '/app/functions')
try:
    from template_function import get_function_schema
    schema = get_function_schema()
    print(f'✓ Function schema loaded: {schema.get(\"name\", \"unknown\")}')
except Exception as e:
    print(f'✗ Function import failed: {e}')
    sys.exit(1)
" 2>/dev/null || {
    echo "Warning: Could not verify function import (this may be normal if functions directory differs)"
}

}

# Function to ensure directories exist
setup_directories() {
    echo ""
    echo "Setting up directories..."

    # Template storage directory
    TEMPLATE_DIR="${TEMPLATE_STORAGE_DIR:-/app/templates}"
    mkdir -p "$TEMPLATE_DIR"
    chmod 755 "$TEMPLATE_DIR" 2>/dev/null || true
    echo "✓ Template directory: $TEMPLATE_DIR"

    # Temp directory
    TEMP_DIR="${PDF_TEMP_DIR:-/app/temp}"
    mkdir -p "$TEMP_DIR"
    chmod 755 "$TEMP_DIR" 2>/dev/null || true
    echo "✓ Temp directory: $TEMP_DIR"
}

# Run setup
echo ""
setup_directories
install_functions
verify_dependencies
verify_functions

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""

# Execute the original OpenWebUI entrypoint if it exists
# This allows the container to start normally after our setup
if [ -f "/app/entrypoint.sh" ]; then
    exec /app/entrypoint.sh "$@"
elif [ -f "/entrypoint.sh" ]; then
    exec /entrypoint.sh "$@"
else
    # If no original entrypoint, just execute what was passed
    exec "$@"
fi
