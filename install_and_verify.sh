#!/bin/bash
# Comprehensive script to install functions and verify they're working

CONTAINER_NAME="${1:-open-webui-template-formatter}"

echo "=========================================="
echo "Installing Template Functions to OpenWebUI"
echo "=========================================="
echo ""

# Step 1: Find OpenWebUI's functions directory
echo "Step 1: Finding OpenWebUI functions directory..."
echo ""

FUNC_DIRS=(
    "/app/functions"
    "/app/backend/functions"
    "/app/open-webui/functions"
    "/root/.open-webui/functions"
    "$HOME/.open-webui/functions"
)

# Search for existing functions directories
echo "Searching for function directories..."
SEARCH_RESULT=$(docker exec "$CONTAINER_NAME" find /app -name "functions" -type d 2>/dev/null | head -1)
if [ -n "$SEARCH_RESULT" ]; then
    echo "✓ Found: $SEARCH_RESULT"
    FUNC_DIRS=("$SEARCH_RESULT" "${FUNC_DIRS[@]}")
fi

# Also check backend directory
BACKEND_FUNC=$(docker exec "$CONTAINER_NAME" test -d "/app/backend/functions" 2>/dev/null && echo "/app/backend/functions" || echo "")
if [ -n "$BACKEND_FUNC" ]; then
    echo "✓ Found: $BACKEND_FUNC"
fi

# Check which directories exist and are writable
FOUND_DIR=""
for dir in "${FUNC_DIRS[@]}"; do
    if docker exec "$CONTAINER_NAME" test -d "$dir" 2>/dev/null || docker exec "$CONTAINER_NAME" mkdir -p "$dir" 2>/dev/null; then
        if docker exec "$CONTAINER_NAME" test -w "$dir" 2>/dev/null || docker exec "$CONTAINER_NAME" test -w "$(dirname "$dir")" 2>/dev/null; then
            FOUND_DIR="$dir"
            echo "✓ Using: $dir"
            break
        fi
    fi
done

# Default to /app/functions if nothing found
if [ -z "$FOUND_DIR" ]; then
    echo "⚠ No functions directory found, creating: /app/functions"
    docker exec "$CONTAINER_NAME" mkdir -p /app/functions
    FOUND_DIR="/app/functions"
fi

echo ""
echo "Using functions directory: $FOUND_DIR"
echo ""

# Step 2: Copy function files
echo "Step 2: Copying function files..."
docker exec "$CONTAINER_NAME" cp /app/functions/template_function.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" cp /app/custom-functions/template_function.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/template_function.py $FOUND_DIR/" 2>/dev/null

docker exec "$CONTAINER_NAME" cp /app/functions/template_extractor.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" cp /app/custom-functions/template_extractor.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/template_extractor.py $FOUND_DIR/" 2>/dev/null

docker exec "$CONTAINER_NAME" cp /app/functions/template_manager.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" cp /app/custom-functions/template_manager.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/template_manager.py $FOUND_DIR/" 2>/dev/null

docker exec "$CONTAINER_NAME" cp /app/functions/pdf_generator.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" cp /app/custom-functions/pdf_generator.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/pdf_generator.py $FOUND_DIR/" 2>/dev/null

echo "✓ Files copied"
echo ""

# Step 3: Verify files are in place
echo "Step 3: Verifying files..."
docker exec "$CONTAINER_NAME" ls -lh "$FOUND_DIR"/*.py 2>/dev/null | grep -E "template|pdf_generator" || echo "⚠ Some files may be missing"
echo ""

# Step 4: Test import
echo "Step 4: Testing function import..."
docker exec "$CONTAINER_NAME" python3 -c "
import sys
import os
sys.path.insert(0, '$FOUND_DIR')
os.chdir('$FOUND_DIR')
try:
    from template_function import get_function_schema
    schema = get_function_schema()
    print(f'✓ Function imports successfully!')
    print(f'  Function name: {schema.get(\"name\", \"unknown\")}')
    print(f'  Description: {schema.get(\"description\", \"\")[:60]}...')
except Exception as e:
    print(f'✗ Function import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Function import test passed!"
else
    echo ""
    echo "✗ Function import test failed - check errors above"
fi
echo ""

# Step 5: Check OpenWebUI logs
echo "Step 5: Checking OpenWebUI logs for function loading..."
docker logs "$CONTAINER_NAME" 2>&1 | grep -i "function\|template\|error" | tail -10 || echo "  (no relevant logs found)"
echo ""

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart OpenWebUI: docker restart $CONTAINER_NAME"
echo "2. Check Admin Panel → Functions for 'manage_document_template'"
echo "3. Try using it in chat: 'List all templates'"
echo ""
echo "If function still doesn't appear:"
echo "- Check logs: docker logs $CONTAINER_NAME | grep -i function"
echo "- Verify files: docker exec -it $CONTAINER_NAME ls -la $FOUND_DIR/"
echo "- Test import: docker exec -it $CONTAINER_NAME python3 -c \"import sys; sys.path.insert(0, '$FOUND_DIR'); from template_function import get_function_schema; print(get_function_schema())\""
echo ""
