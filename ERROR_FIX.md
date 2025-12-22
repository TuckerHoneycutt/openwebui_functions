# Fix for "ModuleNotFoundError: No module named 'app'"

## Problem

The error occurred because we were overriding OpenWebUI's ENTRYPOINT incorrectly, which broke its startup command.

## Solution Applied

I've simplified the approach:

1. **Removed ENTRYPOINT override** - No longer overriding OpenWebUI's entrypoint
2. **Copy functions during build** - Functions are now copied directly to `/app/functions/` during Docker build
3. **No runtime installation needed** - Functions are already in place when container starts

## What Changed

### Dockerfile
- Functions are copied to `/app/functions/` during build
- Removed entrypoint-wrapper.sh and init script complexity
- No ENTRYPOINT override

### docker-compose.yml
- Removed command/entrypoint overrides
- OpenWebUI starts normally with its original entrypoint

## How It Works Now

1. **During build**: Functions are copied to `/app/functions/`
2. **On container start**: OpenWebUI starts normally and loads functions from `/app/functions/`
3. **If functions directory differs**: You can manually copy or mount volumes

## If Functions Don't Appear

If OpenWebUI uses a different functions directory:

1. **Find the correct directory:**
   ```bash
   docker exec -it open-webui-template-formatter find /app -name "functions" -type d
   ```

2. **Copy functions manually:**
   ```bash
   docker exec -it open-webui-template-formatter cp /app/functions/template*.py /path/to/functions/
   docker exec -it open-webui-template-formatter cp /app/functions/pdf_generator.py /path/to/functions/
   ```

3. **Or mount as volume** (update docker-compose.yml):
   ```yaml
   volumes:
     - ./functions:/path/to/functions
   ```

## Rebuild Instructions

```bash
# Rebuild with the fix
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify OpenWebUI starts
docker-compose logs -f
```

You should see OpenWebUI start normally without the "No module named 'app'" error.
