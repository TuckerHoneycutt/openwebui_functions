# Connecting Template Formatter to Your OpenWebUI

## ✅ Yes, This Will Connect!

The template formatter is designed to work with OpenWebUI. Here's how to connect it:

## Quick Connection Steps

### Option 1: If You're Building a New Container (Recommended)

1. **Build the custom image:**
   ```bash
   docker build -t open-webui-template-formatter .
   ```

2. **Start with docker-compose:**
   ```bash
   docker-compose up -d
   ```

3. **Install functions into container:**
   ```bash
   ./install_functions.sh
   ```

4. **Restart container:**
   ```bash
   docker-compose restart
   ```

5. **Verify it's working:**
   - Open OpenWebUI in your browser
   - Go to Settings → Functions (or check the functions list)
   - Look for `manage_document_template` in the list
   - Or try using it: "List all templates"

### Option 2: If You Already Have OpenWebUI Running

1. **Copy files into your existing container:**
   ```bash
   # Find your container name
   docker ps | grep open-webui

   # Copy files (replace CONTAINER_NAME with your container name)
   docker cp template_function.py CONTAINER_NAME:/app/functions/
   docker cp template_extractor.py CONTAINER_NAME:/app/functions/
   docker cp template_manager.py CONTAINER_NAME:/app/functions/
   docker cp pdf_generator.py CONTAINER_NAME:/app/functions/
   ```

2. **Install dependencies in container:**
   ```bash
   docker exec -it CONTAINER_NAME pip install pdfplumber PyMuPDF python-docx reportlab Pillow
   ```

3. **Restart container:**
   ```bash
   docker restart CONTAINER_NAME
   ```

## How OpenWebUI Detects Functions

OpenWebUI automatically detects functions that:
1. Are Python files (`.py`) in the functions directory
2. Have a `get_function_schema()` function that returns a schema
3. Have a handler function matching the schema name

Our function (`template_function.py`) has:
- ✅ `get_function_schema()` - Returns the schema for `manage_document_template`
- ✅ `manage_document_template()` - The handler function (matches schema name)

## Verifying Connection

### Method 1: Check Functions List

1. Open OpenWebUI
2. Go to Settings → Functions (or Admin → Functions)
3. Look for `manage_document_template` in the list

### Method 2: Test in Chat

Try these commands in OpenWebUI chat:

```
List all templates
```

If the function is connected, the LLM should recognize it and call it.

### Method 3: Check Logs

```bash
docker logs open-webui-template-formatter | grep -i template
docker logs open-webui-template-formatter | grep -i function
```

Look for:
- Function loading messages
- Any import errors
- Function registration messages

### Method 4: Use Verification Script

```bash
docker exec -it open-webui-template-formatter python3 /app/verify_setup.py
```

This will check:
- ✅ All imports work
- ✅ Dependencies are installed
- ✅ Directories are writable
- ✅ Function schema is valid

## Troubleshooting Connection Issues

### Function Not Appearing?

1. **Check file location:**
   ```bash
   docker exec -it CONTAINER_NAME ls -la /app/functions/ | grep template
   ```

2. **Check Python syntax:**
   ```bash
   docker exec -it CONTAINER_NAME python3 -m py_compile /app/functions/template_function.py
   ```

3. **Check OpenWebUI logs:**
   ```bash
   docker logs CONTAINER_NAME | tail -100
   ```
   Look for:
   - Import errors
   - Function registration errors
   - Syntax errors

### Import Errors?

If you see import errors for `template_extractor`, `template_manager`, or `pdf_generator`:

1. **Verify all files are copied:**
   ```bash
   docker exec -it CONTAINER_NAME ls -la /app/functions/ | grep -E "template|pdf_generator"
   ```

2. **Check they're in the same directory:**
   All files must be in the same directory (`/app/functions/`) so imports work.

### Function Schema Not Loading?

1. **Test schema manually:**
   ```bash
   docker exec -it CONTAINER_NAME python3 -c "from template_function import get_function_schema; import json; print(json.dumps(get_function_schema(), indent=2))"
   ```

2. **Check function name matches:**
   The schema name (`manage_document_template`) must match the handler function name.

## Expected Behavior After Connection

Once connected, you should be able to:

1. **Upload templates:**
   - Attach PDF/DOCX file
   - Say: "Upload this as template 'My Template'"
   - Function extracts formatting and stores template

2. **List templates:**
   - Say: "List all templates"
   - Function returns list of available templates

3. **Format content:**
   - Get AI response
   - Say: "Format this using the 'My Template' template"
   - Function generates PDF matching template

## File Structure in Container

After installation, your container should have:

```
/app/functions/
├── template_function.py      ← Main function (OpenWebUI loads this)
├── template_extractor.py     ← Core module
├── template_manager.py        ← Core module
└── pdf_generator.py          ← Core module

/app/templates/               ← Template storage (persisted)
├── metadata.json
└── user_*/                   ← User-specific templates

/app/temp/                    ← Temp files (persisted)
└── pdf_template_formatter/
```

## Testing the Connection

Run this test sequence:

1. **Upload a template:**
   ```
   [Attach PDF file]
   Upload this as template "Test Template"
   ```

2. **List templates:**
   ```
   List all templates
   ```
   Should return: "Found 1 template(s)" or similar

3. **Format content:**
   ```
   [Get AI to generate some content]
   Format this using the "Test Template" template
   ```
   Should generate and download a PDF

## Still Having Issues?

1. **Check OpenWebUI version compatibility:**
   - OpenWebUI v0.5.0+ recommended
   - Check your version: `docker exec -it CONTAINER_NAME cat /app/package.json | grep version`

2. **Check function format:**
   - Some OpenWebUI versions expect different function formats
   - Check OpenWebUI docs for your version

3. **Enable debug logging:**
   ```bash
   docker exec -it CONTAINER_NAME export LOG_LEVEL=DEBUG
   docker restart CONTAINER_NAME
   ```

4. **Manual function registration:**
   If auto-detection doesn't work, you may need to manually register the function in OpenWebUI's admin panel (if your version supports it).

## Success Indicators

You'll know it's connected when:
- ✅ Function appears in functions list
- ✅ You can call it from chat
- ✅ Templates upload successfully
- ✅ PDFs generate correctly

## Next Steps

Once connected:
1. Upload a few templates
2. Test formatting with different content types
3. Customize template extraction if needed
4. Set up user-specific templates if using authentication
