#!/bin/bash
# Startup script that runs init then starts OpenWebUI
# This can be used as an alternative to entrypoint override

# Run initialization
/app/init-template-functions.sh || true

# Start OpenWebUI with original command
# This preserves OpenWebUI's original startup behavior
exec "$@"
