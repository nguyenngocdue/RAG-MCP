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

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

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
async def mcp_endpoint():
    """MCP protocol endpoint - returns Server-Sent Events stream"""
    if not mcp_server_instance:
        return JSONResponse(
            status_code=503,
            content={"error": "MCP server not initialized"}
        )
    
    async def event_generator():
        try:
            # Send initialization message
            yield f"data: {{'status': 'initialized', 'tools_available': True}}\n\n"
            
            # Keep connection alive
            while True:
                yield f"data: {{'status': 'ready'}}\n\n"
                await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"SSE error: {e}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
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
