#!/bin/bash
# MCP Inspector for RAG-Anything HTTP Server

export DANGEROUSLY_OMIT_AUTH=true

echo "Starting MCP Inspector for RAG-Anything HTTP Server..."
echo "Inspector will open in your browser at http://localhost:6274"
echo ""

npx @modelcontextprotocol/inspector  python3 run_http_server.py
