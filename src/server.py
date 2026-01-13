"""
MCP Server for RAG-Anything
Main server implementation using Model Context Protocol
"""
import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.rag_manager import RAGManager
from src.tools import MCPTools

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("rag_mcp_server.log"),
    ],
)

logger = logging.getLogger(__name__)


class RAGAnythingMCPServer:
    """MCP Server for RAG-Anything"""

    def __init__(self):
        self.config = Config.load()
        self.server = Server("rag-anything-server")
        self.rag_manager = RAGManager(self.config)
        self.tools = MCPTools(self.config, self.rag_manager)

        # Validate configuration
        if not self.config.validate_api_keys():
            logger.error("API keys not configured. Please set OPENAI_API_KEY or AZURE_OPENAI_API_KEY")
            raise ValueError("API keys not configured")

        # Register handlers
        self._register_handlers()

        logger.info("RAG-Anything MCP Server initialized")

    def _register_handlers(self):
        """Register MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            tool_definitions = self.tools.get_tool_definitions()
            return [
                Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["inputSchema"],
                )
                for tool in tool_definitions
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool calls"""
            try:
                logger.info(f"Tool call: {name}")

                # Initialize RAG if needed
                if not self.rag_manager._initialized:
                    await self.rag_manager.initialize()

                # Handle the tool call
                result = await self.tools.handle_tool_call(name, arguments or {})

                # Format result as JSON string for text content
                import json
                result_text = json.dumps(result, indent=2, ensure_ascii=False)

                return [TextContent(type="text", text=result_text)]

            except Exception as e:
                logger.error(f"Tool call error: {e}", exc_info=True)
                error_result = {
                    "success": False,
                    "error": str(e),
                    "tool": name,
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def run(self):
        """Run the MCP server"""
        try:
            logger.info("Starting RAG-Anything MCP Server...")
            logger.info(f"Storage directory: {self.config.storage.rag_storage_dir}")
            logger.info(f"Upload directory: {self.config.storage.upload_dir}")

            # Run server with stdio transport
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )

        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            await self.rag_manager.shutdown()
            logger.info("Server shutdown complete")


async def main():
    """Main entry point"""
    server = RAGAnythingMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
