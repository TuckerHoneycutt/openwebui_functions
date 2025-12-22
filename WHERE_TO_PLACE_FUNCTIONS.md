# Where to Place Your Functions

## Current Setup

Your functions are **already incorporated** during the Docker build! Here's where they go:

### During Build (Automatic)

The Dockerfile copies your functions to:
- `/app/functions/` - Primary location
- `/app/custom-functions/` - Backup location

Files copied:
- `template_function.py` - Main function (this is what OpenWebUI loads)
- `template_extractor.py` - Template extraction module
- `template_manager.py` - Template storage module
- `pdf_generator.py` - PDF generation module
- `template_action.py` - Optional action/button interface

## Verify Functions Are Loaded

### Step 1: Check if functions are in the container

```bash
# List functions in the container
docker exec -it open-webui-template-formatter ls -la /app/functions/ | grep template
```

You should see:
```
template_function.py
template_extractor.py
template_manager.py
pdf_generator.py
template_action.py
```

### Step 2: Find OpenWebUI's actual functions directory

OpenWebUI might use a different directory. Find it:

```bash
# Search for functions directories
docker exec -it open-webui-template-formatter find /app -name "functions" -type d

# Common locations to check:
docker exec -it open-webui-template-formatter ls -la /app/functions/ 2>/dev/null
docker exec -it open-webui-template-formatter ls -la /app/backend/functions/ 2>/dev/null
docker exec -it open-webui-template-formatter ls -la ~/.open-webui/functions/ 2>/dev/null
docker exec -it open-webui-template-formatter ls -la /root/.open-webui/functions/ 2>/dev/null
```

### Step 3: Copy to correct location (if needed)

If OpenWebUI uses a different directory, copy functions there:

```bash
# Example: If OpenWebUI uses /app/backend/functions/
docker exec -it open-webui-template-formatter cp /app/functions/template*.py /app/backend/functions/
docker exec -it open-webui-template-formatter cp /app/functions/pdf_generator.py /app/backend/functions/

# Or if it uses ~/.open-webui/functions/
docker exec -it open-webui-template-formatter mkdir -p ~/.open-webui/functions
docker exec -it open-webui-template-formatter cp /app/functions/template*.py ~/.open-webui/functions/
docker exec -it open-webui-template-formatter cp /app/functions/pdf_generator.py ~/.open-webui/functions/
```

### Step 4: Restart container

```bash
docker-compose restart
```

### Step 5: Verify in OpenWebUI

1. **Open OpenWebUI** in your browser
2. **Go to Settings → Functions** (or Admin → Functions)
3. **Look for `manage_document_template`** in the functions list

OR test in chat:
```
List all templates
```

If the function is loaded, the LLM should recognize it and call it.

## Quick Verification Script

Run this to check everything:

```bash
#!/bin/bash
CONTAINER="open-webui-template-formatter"

echo "1. Checking functions in /app/functions/"
docker exec -it $CONTAINER ls -la /app/functions/ | grep template || echo "   Not found"

echo ""
echo "2. Searching for OpenWebUI functions directories..."
docker exec -it $CONTAINER find /app -name "functions" -type d 2>/dev/null

echo ""
echo "3. Testing function import..."
docker exec -it $CONTAINER python3 -c "
import sys
sys.path.insert(0, '/app/functions')
try:
    from template_function import get_function_schema
    schema = get_function_schema()
    print(f'✓ Function loaded: {schema.get(\"name\", \"unknown\")}')
except Exception as e:
    print(f'✗ Import failed: {e}')
"

echo ""
echo "4. Check OpenWebUI logs for function loading..."
docker logs $CONTAINER 2>&1 | grep -i "template\|function" | tail -10
```

## If Functions Don't Appear

### Option 1: Use Volume Mount (Recommended for Development)

Update `docker-compose.yml`:

```yaml
volumes:
  # ... existing volumes ...
  # Mount functions directory directly
  - ./functions:/app/functions
```

Then create a `functions/` directory locally and copy your files there:

```bash
mkdir -p functions
cp template_function.py template_extractor.py template_manager.py pdf_generator.py functions/
```

Rebuild:
```bash
docker-compose down
docker-compose up -d
```

### Option 2: Manual Copy After Container Starts

Use the `install_functions.sh` script:

```bash
./install_functions.sh open-webui-template-formatter
```

### Option 3: Check OpenWebUI Logs

```bash
docker logs open-webui-template-formatter | grep -i "function\|template\|error"
```

Look for:
- Function loading messages
- Import errors
- Path issues

## Summary

**Your functions are already incorporated** during build to `/app/functions/`.

**To use them:**
1. Verify they're in the container: `docker exec -it open-webui-template-formatter ls -la /app/functions/`
2. Find OpenWebUI's functions directory: `docker exec -it open-webui-template-formatter find /app -name "functions" -type d`
3. Copy to correct location if needed
4. Restart container
5. Verify in OpenWebUI UI or test in chat

The functions should appear automatically if OpenWebUI loads from `/app/functions/`. If not, copy them to wherever OpenWebUI actually loads functions from.
