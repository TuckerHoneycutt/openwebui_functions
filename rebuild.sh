#!/bin/bash
# Automated rebuild script with --no-cache

set -e

echo "=========================================="
echo "Rebuilding OpenWebUI Template Formatter"
echo "=========================================="
echo ""

# Stop containers
echo "1. Stopping containers..."
docker-compose down

# Rebuild with --no-cache
echo ""
echo "2. Rebuilding image with --no-cache..."
echo "   (This ensures all dependencies are freshly installed)"
docker-compose build --no-cache

# Start containers
echo ""
echo "3. Starting containers..."
docker-compose up -d

# Wait for startup
echo ""
echo "4. Waiting for container to start..."
sleep 5

# Verify installation
echo ""
echo "5. Verifying installation..."
echo "   Checking functions directory..."
docker exec -it open-webui-template-formatter ls -la /app/functions/ 2>/dev/null | grep -E "template|pdf_generator" || echo "   (Functions directory check)"

echo ""
echo "6. Checking dependencies..."
docker exec -it open-webui-template-formatter pip list 2>/dev/null | grep -E "pdfplumber|PyMuPDF|python-docx|reportlab|Pillow" || echo "   (Dependency check)"

echo ""
echo "=========================================="
echo "Rebuild complete!"
echo "=========================================="
echo ""
echo "Check logs with: docker-compose logs -f"
echo "Verify function: docker exec -it open-webui-template-formatter python3 /app/verify_setup.py"
echo ""
