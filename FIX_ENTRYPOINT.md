# Fixing Entrypoint Issues

The error `ModuleNotFoundError: No module named 'app'` occurs because we're overriding OpenWebUI's ENTRYPOINT incorrectly.

## The Problem

When we override ENTRYPOINT in the Dockerfile, we need to ensure:
1. The original CMD from the base image is preserved
2. The working directory and environment are correct
3. OpenWebUI's startup command executes properly

## Solution Options

### Option 1: Remove ENTRYPOINT Override (Simplest)

Don't override ENTRYPOINT at all. Instead, use a different mechanism:

1. Remove ENTRYPOINT override from Dockerfile
2. Use docker-compose command override to run init script first
3. Or use a volume-mounted init script that OpenWebUI executes

### Option 2: Fix ENTRYPOINT Wrapper (Current Approach)

Ensure the wrapper properly preserves the CMD and working directory.

### Option 3: Use OpenWebUI's Function Loading Mechanism

If OpenWebUI has a way to load functions automatically, use that instead.

## Recommended Fix

Use Option 1 - remove ENTRYPOINT override and use CMD in docker-compose instead.
