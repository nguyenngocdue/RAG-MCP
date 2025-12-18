"""
VS Code MCP Client Configuration Example
Shows how to configure VS Code to use the RAG-Anything MCP Server
"""
import json

# Example VS Code settings.json configuration
vscode_config = {
    "mcp.servers": {
        "rag-anything": {
            "command": "python",
            "args": [
                "/home/nguyenngocdue/sj-project/twin-editor-rag/src/server.py"
            ],
            "env": {
                "OPENAI_API_KEY": "your_openai_api_key",
                "OPENAI_BASE_URL": "https://api.openai.com/v1",
                "LLM_MODEL": "gpt-4o-mini",
                "VISION_MODEL": "gpt-4o",
                "EMBEDDING_MODEL": "text-embedding-3-large",
                "EMBEDDING_DIM": "3072",
                "RAG_STORAGE_DIR": "./rag_storage",
                "UPLOAD_DIR": "./uploads",
                "LOG_LEVEL": "INFO"
            }
        }
    }
}

# Example Claude Desktop configuration
claude_config = {
    "mcpServers": {
        "rag-anything": {
            "command": "python",
            "args": [
                "/home/nguyenngocdue/sj-project/twin-editor-rag/src/server.py"
            ],
            "env": {
                "OPENAI_API_KEY": "your_openai_api_key"
            }
        }
    }
}


def print_configurations():
    """Print example configurations"""
    print("🔧 MCP Client Configuration Examples")
    print("=" * 80)
    
    print("\n📘 VS Code Configuration")
    print("-" * 80)
    print("Add this to your VS Code settings.json:\n")
    print(json.dumps(vscode_config, indent=2))
    
    print("\n\n💬 Claude Desktop Configuration")
    print("-" * 80)
    print("Add this to your claude_desktop_config.json:\n")
    print(json.dumps(claude_config, indent=2))
    
    print("\n\n📝 Notes:")
    print("-" * 80)
    print("1. Update the 'args' path to match your installation directory")
    print("2. Replace 'your_openai_api_key' with your actual API key")
    print("3. Or use .env file instead of setting env variables here")
    print("4. Restart VS Code / Claude Desktop after configuration")
    
    print("\n\n🚀 Using with Python MCP Client Library")
    print("-" * 80)
    print("""
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Server parameters
server_params = StdioServerParameters(
    command="python",
    args=["/path/to/twin-editor-rag/src/server.py"],
    env={
        "OPENAI_API_KEY": "your_key"
    }
)

# Connect to server
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Call a tool
        result = await session.call_tool("upload_document", {
            "file_path": "./document.pdf"
        })
        print(result)
    """)
    
    print("\n✅ Configuration examples complete!")


if __name__ == "__main__":
    print_configurations()
