"""LunVex Code terminal AI coding assistant."""

import os

__version__ = "0.1.0"
APP_COMMAND_NAME = "lunvex-code"
APP_DISPLAY_NAME = "LunVex Code"
APP_STATE_DIRNAME = ".lunvex-code"
APP_CONTEXT_FILENAME = "LUNVEX.md"

# File cache configuration from environment variables
CACHE_MAX_SIZE = int(os.getenv("LUNVEX_CACHE_MAX_SIZE", "100"))
CACHE_TTL_SECONDS = int(os.getenv("LUNVEX_CACHE_TTL_SECONDS", "300"))

# LLM cache configuration from environment variables
LLM_CACHE_MAX_SIZE = int(os.getenv("LUNVEX_LLM_CACHE_MAX_SIZE", "100"))
LLM_CACHE_TTL_SECONDS = int(os.getenv("LUNVEX_LLM_CACHE_TTL_SECONDS", "3600"))
