#!/usr/bin/env python
"""
Entry point for RAG-Anything MCP Server
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.server import main

if __name__ == "__main__":
    asyncio.run(main())
