"""
HTTP Server wrapper for RAG-Anything MCP Server
Runs MCP server over HTTP for cloud deployment
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import json

from src.server import RAGAnythingMCPServer
from src.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="RAG-Anything MCP Server")

# Initialize MCP server
try:
    config = Config.load()
    mcp_server_instance = RAGAnythingMCPServer()
    logger.info("MCP Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP server: {e}")
    mcp_server_instance = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "RAG-Anything MCP Server",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_server": "initialized" if mcp_server_instance else "error"
    }


@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    if not mcp_server_instance:
        return JSONResponse(
            status_code=503,
            content={"error": "MCP server not initialized"}
        )
    
    try:
        tools = mcp_server_instance.tools.get_tool_definitions()
        return {
            "total": len(tools),
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/mcp")
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP protocol endpoint - handles JSON-RPC requests"""
    if not mcp_server_instance:
        return JSONResponse(
            status_code=503,
            content={"jsonrpc": "2.0", "error": {"code": -32603, "message": "MCP server not initialized"}}
        )
    
    try:
        # Get request body
        if request.method == "POST":
            body = await request.json()
        else:
            # For GET requests, check for query parameters
            body = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
        
        # Handle JSON-RPC request
        jsonrpc_version = body.get("jsonrpc", "2.0")
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        logger.info(f"MCP request: method={method}, params={params}")
        
        # Route to appropriate handler
        if method == "tools/list":
            # List available tools
            tool_definitions = mcp_server_instance.tools.get_tool_definitions()
            tools = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": tool["inputSchema"],
                }
                for tool in tool_definitions
            ]
            return JSONResponse({
                "jsonrpc": jsonrpc_version,
                "result": {"tools": tools},
                "id": request_id
            })
        
        elif method == "tools/call":
            # Call a tool
            tool_name = params.get("name")
            tool_arguments = params.get("arguments", {})
            
            # Initialize RAG if needed
            if not mcp_server_instance.rag_manager._initialized:
                await mcp_server_instance.rag_manager.initialize()
            
            # Call the tool
            result = await mcp_server_instance.tools.handle_tool_call(tool_name, tool_arguments)
            
            return JSONResponse({
                "jsonrpc": jsonrpc_version,
                "result": result,
                "id": request_id
            })
        
        else:
            # Unknown method
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": jsonrpc_version,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id
                }
            )
    
    except Exception as e:
        logger.error(f"MCP endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request.get("id") if isinstance(request, dict) else None
            }
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting HTTP server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
