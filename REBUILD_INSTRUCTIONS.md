# Rebuilding Docker Container with --no-cache

This guide explains how to rebuild your Docker container with `--no-cache` to ensure all installations happen fresh.

## Quick Rebuild Command

```bash
# Stop and remove existing container
docker-compose down

# Rebuild with --no-cache (ensures all dependencies are freshly installed)
docker-compose build --no-cache

# Start the container
docker-compose up -d

# Check logs to verify installation
docker-compose logs -f
```

## What Happens Automatically

When you rebuild with `--no-cache`, the Dockerfile will:

1. ✅ **Install system dependencies** (python3-dev, gcc, bash)
2. ✅ **Install Python packages** (pdfplumber, PyMuPDF, python-docx, reportlab, Pillow)
3. ✅ **Create directories** (/app/templates, /app/temp, /app/custom-functions, /app/functions)
4. ✅ **Copy function files** to /app/custom-functions/
5. ✅ **Set up initialization script** that installs functions on container start

When the container starts, the initialization script automatically:

1. ✅ **Finds the OpenWebUI functions directory**
2. ✅ **Copies function files** from /app/custom-functions/ to the functions directory
3. ✅ **Verifies dependencies** are installed
4. ✅ **Starts OpenWebUI** normally

## Manual Rebuild Steps

If you prefer manual control:

```bash
# 1. Stop container
docker-compose stop

# 2. Remove container (keeps volumes)
docker-compose rm -f

# 3. Rebuild image with no cache
docker build --no-cache -t open-webui-template-formatter .

# 4. Start container
docker-compose up -d

# 5. Verify installation
docker-compose logs | grep -i template
```

## Verifying Fresh Installation

After rebuilding, verify everything is installed:

```bash
# Check that functions are installed
docker exec -it open-webui-template-formatter ls -la /app/functions/ | grep template

# Check dependencies
docker exec -it open-webui-template-formatter pip list | grep -E "pdfplumber|PyMuPDF|python-docx|reportlab|Pillow"

# Run verification script
docker exec -it open-webui-template-formatter python3 /app/verify_setup.py

# Check container logs for initialization messages
docker logs open-webui-template-formatter | grep -i "template\|function"
```

## Expected Output

When the container starts, you should see:

```
==========================================
Installing Template Formatter Functions
==========================================
✓ Functions installed to /app/functions
✓ Dependencies OK
==========================================
```

## Troubleshooting

### Functions Not Installing

If functions don't appear after rebuild:

1. **Check initialization script ran:**
   ```bash
   docker logs open-webui-template-formatter | grep -i "installing\|template"
   ```

2. **Manually run initialization:**
   ```bash
   docker exec -it open-webui-template-formatter /app/init-template-functions.sh
   ```

3. **Check functions directory:**
   ```bash
   docker exec -it open-webui-template-formatter ls -la /app/functions/
   ```

### Dependencies Missing

If dependencies are missing after rebuild:

1. **Check Dockerfile build:**
   ```bash
   docker build --no-cache -t open-webui-template-formatter . 2>&1 | grep -i "pip install"
   ```

2. **Manually install:**
   ```bash
   docker exec -it open-webui-template-formatter pip install pdfplumber PyMuPDF python-docx reportlab Pillow
   ```

### Container Won't Start

If the container fails to start:

1. **Check logs:**
   ```bash
   docker logs open-webui-template-formatter
   ```

2. **Try without command override:**
   Comment out the `command:` section in docker-compose.yml temporarily

3. **Run initialization manually:**
   ```bash
   docker run -it --rm open-webui-template-formatter /app/init-template-functions.sh
   ```

## Clean Rebuild (Removes Everything)

For a completely fresh start:

```bash
# Stop and remove everything (including volumes - WARNING: deletes data!)
docker-compose down -v

# Remove image
docker rmi open-webui-template-formatter

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

**⚠️ Warning:** `docker-compose down -v` will delete your templates and data volumes!

## Best Practices

1. **Always use --no-cache for production builds** to ensure consistency
2. **Check logs after rebuild** to verify installation
3. **Test function availability** before deploying
4. **Keep templates in volumes** so they persist across rebuilds
5. **Use docker-compose** for easier management

## Automated Rebuild Script

Create a `rebuild.sh` script:

```bash
#!/bin/bash
set -e

echo "Stopping containers..."
docker-compose down

echo "Rebuilding with --no-cache..."
docker-compose build --no-cache

echo "Starting containers..."
docker-compose up -d

echo "Waiting for startup..."
sleep 5

echo "Checking installation..."
docker exec -it open-webui-template-formatter /app/init-template-functions.sh

echo "Verifying functions..."
docker exec -it open-webui-template-formatter ls -la /app/functions/ | grep template

echo "Done! Check logs with: docker-compose logs -f"
```

Make it executable:
```bash
chmod +x rebuild.sh
```

Then run:
```bash
./rebuild.sh
```
