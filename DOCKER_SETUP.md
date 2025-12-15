# Docker Setup Guide for PDF Template Formatter

This guide explains how to set up the PDF Template Formatter function in OpenWebUI running in a Docker container.

## Option 1: Custom Docker Image (Recommended)

This approach creates a custom Docker image with all dependencies pre-installed.

### Step 1: Build the Custom Image

```bash
docker build -t open-webui-pdf-formatter .
```

### Step 2: Run with Docker Compose

```bash
docker-compose up -d
```

Or run directly:

```bash
docker run -d \
  --name open-webui-pdf-formatter \
  -p 3000:8080 \
  -v open-webui-data:/app/backend/data \
  -v $(pwd)/templates:/app/templates \
  -e TEMPLATE_STORAGE_DIR=/app/templates \
  -e PDF_TEMP_DIR=/app/temp \
  open-webui-pdf-formatter
```

### Step 3: Copy Function Files

After the container is running, copy the function files into the container:

```bash
docker cp functions.py open-webui-pdf-formatter:/app/functions/
docker cp template_extractor.py open-webui-pdf-formatter:/app/functions/
docker cp pdf_generator.py open-webui-pdf-formatter:/app/functions/
docker cp template_manager.py open-webui-pdf-formatter:/app/functions/
```

Or mount them as a volume:

```bash
docker run -d \
  --name open-webui-pdf-formatter \
  -p 3000:8080 \
  -v open-webui-data:/app/backend/data \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd):/app/custom-functions \
  -e TEMPLATE_STORAGE_DIR=/app/templates \
  -e PDF_TEMP_DIR=/app/temp \
  open-webui-pdf-formatter
```

Then copy files inside the container or modify the Dockerfile to copy from `/app/custom-functions`.

## Option 2: Install Dependencies in Running Container

If you already have OpenWebUI running, you can install dependencies directly:

### Step 1: Install Dependencies

```bash
docker exec -it <container-name> pip install pdfplumber PyMuPDF python-docx reportlab Pillow
```

### Step 2: Copy Function Files

```bash
docker cp functions.py <container-name>:/app/functions/
docker cp template_extractor.py <container-name>:/app/functions/
docker cp pdf_generator.py <container-name>:/app/functions/
docker cp template_manager.py <container-name>:/app/functions/
```

### Step 3: Create Storage Directories

```bash
docker exec -it <container-name> mkdir -p /app/templates /app/temp
docker exec -it <container-name> chmod 755 /app/templates /app/temp
```

### Step 4: Set Environment Variables

Add to your docker run command or docker-compose.yml:

```yaml
environment:
  - TEMPLATE_STORAGE_DIR=/app/templates
  - PDF_TEMP_DIR=/app/temp
```

## Option 3: Extend Existing Docker Compose

If you're already using docker-compose for OpenWebUI:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    # ... your existing configuration ...
    environment:
      - TEMPLATE_STORAGE_DIR=/app/templates
      - PDF_TEMP_DIR=/app/temp
    volumes:
      - ./templates:/app/templates
      - ./temp:/app/temp
      - ./functions.py:/app/functions/functions.py
      - ./template_extractor.py:/app/functions/template_extractor.py
      - ./pdf_generator.py:/app/functions/pdf_generator.py
      - ./template_manager.py:/app/functions/template_manager.py
```

Then install dependencies:

```bash
docker-compose exec open-webui pip install pdfplumber PyMuPDF python-docx reportlab Pillow
```

## Finding OpenWebUI Functions Directory

The functions directory location may vary. Common locations:

- `/app/functions/`
- `/app/backend/functions/`
- `/app/open-webui/functions/`

To find it:

```bash
docker exec -it <container-name> find /app -name "functions" -type d
```

## Verifying Installation

After setting up, verify everything works:

```bash
# Copy verification script
docker cp verify_setup.py <container-name>:/app/

# Run verification
docker exec -it <container-name> python3 /app/verify_setup.py
```

This will check:
- All modules can be imported
- All dependencies are installed
- Directories are writable
- Function schema is valid

## Persisting Templates

Templates are stored in `/app/templates` inside the container. To persist them:

1. **Volume Mount** (Recommended):
   ```bash
   -v $(pwd)/templates:/app/templates
   ```

2. **Named Volume**:
   ```yaml
   volumes:
     - template-storage:/app/templates
   ```

## Troubleshooting

### Function Not Appearing

1. Check function files are in the correct directory:
   ```bash
   docker exec -it <container-name> ls -la /app/functions/
   ```

2. Check for import errors:
   ```bash
   docker exec -it <container-name> python3 -c "import functions"
   ```

3. Check OpenWebUI logs:
   ```bash
   docker logs <container-name>
   ```

### Missing Dependencies

If you get import errors:

```bash
docker exec -it <container-name> pip list | grep -E "pdfplumber|PyMuPDF|python-docx|reportlab"
```

Install missing packages:

```bash
docker exec -it <container-name> pip install <package-name>
```

### Permission Issues

Ensure directories are writable:

```bash
docker exec -it <container-name> chmod -R 755 /app/templates /app/temp
```

### Container Restart

After installing dependencies or copying files, restart the container:

```bash
docker restart <container-name>
```

## Production Considerations

1. **Use Named Volumes**: For production, use named Docker volumes instead of bind mounts for better portability.

2. **Resource Limits**: PDF generation can be memory-intensive. Consider setting memory limits:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

3. **Backup Templates**: Regularly backup the templates volume:
   ```bash
   docker run --rm -v template-storage:/data -v $(pwd):/backup alpine tar czf /backup/templates-backup.tar.gz /data
   ```

4. **Health Checks**: Add health checks to ensure the function is working:
   ```yaml
   healthcheck:
     test: ["CMD", "python3", "-c", "import functions"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## Updating the Function

To update the function files:

1. Copy new files:
   ```bash
   docker cp functions.py <container-name>:/app/functions/
   ```

2. Restart container:
   ```bash
   docker restart <container-name>
   ```

Or use volume mounts for automatic updates (development only).
