#!/bin/bash
# Script to find where OpenWebUI loads functions from

CONTAINER_NAME="${1:-open-webui-template-formatter}"

echo "Finding OpenWebUI functions directory..."
echo ""

# Check common locations
echo "Checking common function directories:"
docker exec -it "$CONTAINER_NAME" ls -la /app/functions/ 2>/dev/null && echo "✓ Found /app/functions/" || echo "✗ /app/functions/ not found"
docker exec -it "$CONTAINER_NAME" ls -la /app/backend/functions/ 2>/dev/null && echo "✓ Found /app/backend/functions/" || echo "✗ /app/backend/functions/ not found"
docker exec -it "$CONTAINER_NAME" ls -la /root/.open-webui/functions/ 2>/dev/null && echo "✓ Found /root/.open-webui/functions/" || echo "✗ /root/.open-webui/functions/ not found"

echo ""
echo "Searching for function directories:"
docker exec -it "$CONTAINER_NAME" find /app -name "functions" -type d 2>/dev/null

echo ""
echo "Checking if our functions exist:"
docker exec -it "$CONTAINER_NAME" ls -la /app/functions/ | grep template || echo "No template functions found in /app/functions/"

echo ""
echo "Checking OpenWebUI logs for function loading:"
docker logs "$CONTAINER_NAME" 2>&1 | grep -i "function" | tail -20
