#!/bin/bash
# Script to install template functions into OpenWebUI container

CONTAINER_NAME="${1:-open-webui-template-formatter}"

echo "Installing template functions into container: $CONTAINER_NAME"

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Error: Container '$CONTAINER_NAME' not found"
    echo "Available containers:"
    docker ps -a --format '{{.Names}}'
    exit 1
fi

# Try common OpenWebUI function directories
FUNCTION_DIRS=(
    "/app/functions"
    "/app/backend/functions"
    "~/.open-webui/functions"
    "/root/.open-webui/functions"
)

FOUND_DIR=""

for dir in "${FUNCTION_DIRS[@]}"; do
    echo "Checking $dir..."
    if docker exec "$CONTAINER_NAME" test -d "$dir" 2>/dev/null || \
       docker exec "$CONTAINER_NAME" mkdir -p "$dir" 2>/dev/null; then
        FOUND_DIR="$dir"
        echo "Found functions directory: $dir"
        break
    fi
done

if [ -z "$FOUND_DIR" ]; then
    echo "Warning: Could not find functions directory. Creating ~/.open-webui/functions"
    docker exec "$CONTAINER_NAME" mkdir -p ~/.open-webui/functions
    FOUND_DIR="~/.open-webui/functions"
fi

# Copy function files
echo "Copying function files to $FOUND_DIR..."

docker exec "$CONTAINER_NAME" cp /app/custom-functions/template_function.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/template_function.py $FOUND_DIR/"

docker exec "$CONTAINER_NAME" cp /app/custom-functions/template_extractor.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/template_extractor.py $FOUND_DIR/"

docker exec "$CONTAINER_NAME" cp /app/custom-functions/template_manager.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/template_manager.py $FOUND_DIR/"

docker exec "$CONTAINER_NAME" cp /app/custom-functions/pdf_generator.py "$FOUND_DIR/" 2>/dev/null || \
docker exec "$CONTAINER_NAME" sh -c "cp /app/custom-functions/pdf_generator.py $FOUND_DIR/"

# Verify installation
echo ""
echo "Verifying installation..."
docker exec "$CONTAINER_NAME" ls -la "$FOUND_DIR/" | grep -E "template|pdf_generator"

echo ""
echo "Installation complete!"
echo ""
echo "To verify the function is loaded:"
echo "1. Restart the container: docker restart $CONTAINER_NAME"
echo "2. Check OpenWebUI logs: docker logs $CONTAINER_NAME | grep -i template"
echo "3. Look for 'manage_document_template' in the functions list in OpenWebUI UI"
