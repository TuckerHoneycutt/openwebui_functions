# Docker Compatibility Notes

## Will This Work in OpenWebUI Docker?

**Yes, but with some considerations:**

### ✅ What Works Out of the Box

1. **Dependencies**: All Python dependencies (`pdfplumber`, `PyMuPDF`, `python-docx`, `reportlab`) can be installed in the Docker container without conflicts
2. **File Storage**: Template storage uses configurable paths via environment variables, compatible with Docker volumes
3. **Function Structure**: The function follows standard Python async function patterns compatible with OpenWebUI

### ⚠️ Potential Issues & Solutions

#### 1. OpenWebUI Function Format

OpenWebUI may expect functions in a specific format. The current implementation uses:
- `get_function_schema()` - Returns function schema
- `format_to_pdf_template()` - Main async handler

**If the function doesn't appear in OpenWebUI:**
- Check OpenWebUI documentation for the exact function format
- You may need to adjust the function registration
- Some versions use decorators or different naming conventions

**Solution**: The function files are modular - you can adjust `functions.py` to match your OpenWebUI version's expected format without changing the core logic.

#### 2. Function Directory Location

The functions directory path varies by OpenWebUI version and installation method.

**Solution**:
- Use the verification script to check imports
- Mount function files as volumes for easy updates
- Check OpenWebUI logs for import errors

#### 3. Dependencies Installation

Installing dependencies directly in a running container works, but they'll be lost on container restart unless:
- You use a custom Dockerfile (recommended)
- You mount a requirements.txt and install on startup
- You use a volume for Python packages (advanced)

**Solution**: Use the provided Dockerfile to build a custom image with all dependencies pre-installed.

#### 4. File Permissions

Docker containers may have permission issues with file creation.

**Solution**:
- Set proper permissions in Dockerfile
- Use environment variables for paths
- Ensure volumes are writable

### 🔧 Recommended Approach

**For Production:**
1. Build custom Docker image with dependencies (Dockerfile provided)
2. Use named volumes for template storage
3. Mount function files or copy them into the image
4. Set environment variables for paths

**For Development:**
1. Use docker-compose with volume mounts
2. Install dependencies in running container
3. Mount function files for easy updates
4. Use bind mounts for templates (easier debugging)

### 📋 Quick Checklist

Before deploying, verify:

- [ ] All dependencies installed (`pip list | grep -E "pdfplumber|PyMuPDF|python-docx|reportlab"`)
- [ ] Function files in correct directory
- [ ] Directories writable (`chmod 755`)
- [ ] Environment variables set (`TEMPLATE_STORAGE_DIR`, `PDF_TEMP_DIR`)
- [ ] Function imports successfully (`python3 -c "import functions"`)
- [ ] Function schema retrievable (`python3 verify_setup.py`)

### 🐛 Troubleshooting

**Function not appearing:**
```bash
# Check if function is in correct location
docker exec -it <container> find /app -name "functions.py"

# Check for import errors
docker exec -it <container> python3 -c "import functions"

# Check OpenWebUI logs
docker logs <container> | grep -i function
```

**Dependencies missing:**
```bash
# Install in running container
docker exec -it <container> pip install pdfplumber PyMuPDF python-docx reportlab Pillow

# Or rebuild image with Dockerfile
docker build -t open-webui-pdf-formatter .
```

**Permission errors:**
```bash
# Fix permissions
docker exec -it <container> chmod -R 755 /app/templates /app/temp
```

### 💡 Best Practices

1. **Use Custom Dockerfile**: Pre-install dependencies to avoid runtime issues
2. **Persist Templates**: Use volumes to persist templates across restarts
3. **Test First**: Use verification script before production deployment
4. **Monitor Logs**: Check container logs for errors
5. **Backup Templates**: Regularly backup template volumes

### 🔄 Updating the Function

When updating function code:

```bash
# Copy new files
docker cp functions.py <container>:/app/functions/

# Restart container
docker restart <container>

# Or use volume mounts for automatic updates (dev only)
```

### 📚 Additional Resources

- OpenWebUI Docker Documentation
- Docker Volume Management
- Python Package Management in Containers
