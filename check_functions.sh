#!/bin/bash
# Script to check where OpenWebUI loads functions from

CONTAINER_NAME="${1:-open-webui-template-formatter}"

echo "=========================================="
echo "Checking OpenWebUI Functions Setup"
echo "=========================================="
echo ""

echo "1. Checking if container is running..."
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   ✗ Container '$CONTAINER_NAME' is not running"
    echo "   Start it with: docker-compose up -d"
    exit 1
fi
echo "   ✓ Container is running"
echo ""

echo "2. Finding OpenWebUI functions directories..."
docker exec "$CONTAINER_NAME" find /app -name "functions" -type d 2>/dev/null | head -10
docker exec "$CONTAINER_NAME" find /root -name "functions" -type d 2>/dev/null | head -10
docker exec "$CONTAINER_NAME" find /home -name "functions" -type d 2>/dev/null | head -10
echo ""

echo "3. Checking where functions are currently located..."
echo "   Functions in /app/functions/:"
docker exec "$CONTAINER_NAME" ls -la /app/functions/ 2>/dev/null | grep -E "template|pdf_generator" || echo "   (none found)"
echo ""

echo "4. Checking OpenWebUI logs for function loading..."
echo "   Recent function-related log entries:"
docker logs "$CONTAINER_NAME" 2>&1 | grep -i "function\|template\|error\|import" | tail -20 || echo "   (no relevant logs found)"
echo ""

echo "5. Testing function import..."
docker exec "$CONTAINER_NAME" python3 -c "
import sys
sys.path.insert(0, '/app/functions')
try:
    from template_function import get_function_schema
    schema = get_function_schema()
    print(f'   ✓ Function imports successfully: {schema.get(\"name\", \"unknown\")}')
except Exception as e:
    print(f'   ✗ Function import failed: {e}')
    import traceback
    traceback.print_exc()
" 2>&1
echo ""

echo "6. Checking Python path in container..."
docker exec "$CONTAINER_NAME" python3 -c "import sys; print('   Python paths:'); [print(f'     {p}') for p in sys.path]"
echo ""

echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo "1. If functions directory was found, copy functions there"
echo "2. Check OpenWebUI admin panel → Functions"
echo "3. Restart container if needed: docker restart $CONTAINER_NAME"
echo ""
