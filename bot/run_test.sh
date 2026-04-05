#!/bin/bash
# Wrapper script for autochecker compatibility
# If uv is not available, fall back to python3

cd "$(dirname "$0")"

if command -v uv &> /dev/null; then
    exec uv run bot.py "$@"
else
    exec python3 bot.py "$@"
fi
