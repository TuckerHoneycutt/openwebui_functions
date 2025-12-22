# Setting Up Functions in OpenWebUI

## Quick Setup

Run the installation script:

```bash
./install_and_verify.sh
```

This will:
1. Find OpenWebUI's functions directory
2. Copy all function files there
3. Verify they import correctly
4. Show you next steps

## Manual Setup

If the script doesn't work, follow these steps:

### Step 1: Find OpenWebUI's Functions Directory

```bash
# Search for functions directories
docker exec -it open-webui-template-formatter find /app -name "functions" -type d

# Check common locations
docker exec -it open-webui-template-formatter ls -la /app/functions/ 2>/dev/null
docker exec -it open-webui-template-formatter ls -la /app/backend/functions/ 2>/dev/null
docker exec -it open-webui-template-formatter ls -la /root/.open-webui/functions/ 2>/dev/null
```

### Step 2: Copy Functions to the Correct Location

Once you find the directory (let's say it's `/app/backend/functions/`):

```bash
# Copy all function files
docker exec -it open-webui-template-formatter cp /app/functions/template_function.py /app/backend/functions/
docker exec -it open-webui-template-formatter cp /app/functions/template_extractor.py /app/backend/functions/
docker exec -it open-webui-template-formatter cp /app/functions/template_manager.py /app/backend/functions/
docker exec -it open-webui-template-formatter cp /app/functions/pdf_generator.py /app/backend/functions/
```

### Step 3: Verify Functions Import

```bash
docker exec -it open-webui-template-formatter python3 -c "
import sys
sys.path.insert(0, '/app/backend/functions')  # Use your directory
from template_function import get_function_schema
print(get_function_schema())
"
```

### Step 4: Restart OpenWebUI

```bash
docker restart open-webui-template-formatter
```

### Step 5: Check Admin Panel

1. Open OpenWebUI in your browser
2. Go to **Admin Panel** → **Functions**
3. Look for `manage_document_template`

## Troubleshooting

### Function Not Appearing in Admin Panel

1. **Check logs for errors:**
   ```bash
   docker logs open-webui-template-formatter | grep -i "function\|error\|import"
   ```

2. **Verify files are in the right place:**
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/backend/functions/ | grep template
   ```

3. **Test import manually:**
   ```bash
   docker exec -it open-webui-template-formatter python3 -c "
   import sys
   sys.path.insert(0, '/app/backend/functions')
   from template_function import get_function_schema
   schema = get_function_schema()
   print('Function name:', schema['name'])
   "
   ```

4. **Check OpenWebUI version compatibility:**
   - Some versions load functions differently
   - Check OpenWebUI documentation for your version

### Import Errors

If you see import errors:

1. **Check all files are present:**
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/backend/functions/ | grep -E "template|pdf_generator"
   ```

2. **Verify dependencies:**
   ```bash
   docker exec -it open-webui-template-formatter pip list | grep -E "pdfplumber|PyMuPDF|python-docx|reportlab"
   ```

3. **Check Python path:**
   ```bash
   docker exec -it open-webui-template-formatter python3 -c "import sys; print('\n'.join(sys.path))"
   ```

## Using the Function

Once it appears in the Admin Panel:

1. **In chat, try:**
   - "List all templates"
   - "Upload this as template 'My Template'" (with file attached)
   - "Format this using the 'My Template' template"

2. **The function should appear:**
   - In the functions list in Admin Panel
   - As an available function the LLM can call
   - In chat when you mention template-related actions

## Common Function Directories

OpenWebUI may use:
- `/app/functions/`
- `/app/backend/functions/`
- `/app/open-webui/functions/`
- `/root/.open-webui/functions/`
- `~/.open-webui/functions/`

The installation script will find the correct one automatically.
