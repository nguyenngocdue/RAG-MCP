"""
HTTP Server wrapper for RAG-Anything MCP Server
Runs MCP server over HTTP for cloud deployment
"""
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from src.server import RAGAnythingMCPServer
from src.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize MCP server
try:
    config = Config.load()
    mcp_server_instance = RAGAnythingMCPServer()
    logger.info("MCP Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP server: {e}")
    mcp_server_instance = None

session_manager = None
if mcp_server_instance:
    session_manager = StreamableHTTPSessionManager(mcp_server_instance.server)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if session_manager:
        async with session_manager.run():
            yield
    else:
        yield


# Create FastAPI app
app = FastAPI(title="RAG-Anything MCP Server", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"],  # Allows all headers
)


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

if session_manager:
    app.mount("/mcp", session_manager.handle_request)
else:
    @app.api_route("/mcp", methods=["GET", "POST", "DELETE"])
    async def mcp_unavailable():
        return JSONResponse(
            status_code=503,
            content={"error": "MCP server not initialized"}
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "4000"))
    logger.info(f"Starting HTTP server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
