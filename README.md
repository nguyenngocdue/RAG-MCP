# 🚀 RAG-Anything MCP Server

A powerful **Model Context Protocol (MCP)** server that exposes **RAG-Anything** capabilities, enabling any MCP-compatible application to perform advanced multi-modal document processing and retrieval.

## 🌟 Features

- **📄 Multi-format Document Processing**: PDF, Office documents, images, text files
- **🔍 Intelligent RAG Queries**: Text and multimodal query support
- **🧠 Knowledge Graph Integration**: Powered by LightRAG
- **🖼️ Vision Language Model**: Analyze images, tables, and equations
- **🔌 MCP Protocol**: Standardized interface for any client application
- **⚡ Async Operations**: High-performance async processing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Clients                           │
│  (VS Code, Claude Desktop, Custom Apps, etc.)           │
└─────────────────────────────────────────────────────────┘
                         │
                    MCP Protocol
                         │
┌─────────────────────────────────────────────────────────┐
│              RAG-Anything MCP Server                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Document Processing Tools                       │   │
│  │  - upload_document                               │   │
│  │  - process_document                              │   │
│  │  - batch_process                                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Query Tools                                     │   │
│  │  - query_text                                    │   │
│  │  - query_multimodal                              │   │
│  │  - query_with_context                            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Management Tools                                │   │
│  │  - list_documents                                │   │
│  │  - get_document_info                             │   │
│  │  - delete_document                               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  RAG-Anything Core                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   MinerU     │  │   LightRAG   │  │     VLM      │  │
│  │   Parser     │  │  Knowledge   │  │   Analysis   │  │
│  │              │  │    Graph     │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd twin-editor-rag

# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file:

```bash
# API Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional

# Model Configuration
LLM_MODEL=gpt-4o-mini
VISION_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072

# Storage Configuration
RAG_STORAGE_DIR=./rag_storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100  # MB

# Server Configuration
LOG_LEVEL=INFO
```

### Running the Server

```bash
# Start MCP server
python src/server.py

# Or use with specific config
python src/server.py --config config.json
```

### Using with MCP Clients

#### VS Code (with MCP Extension)

Add to your VS Code settings:

```json
{
  "mcp.servers": {
    "rag-anything": {
      "command": "python",
      "args": ["/path/to/twin-editor-rag/src/server.py"],
      "env": {
        "OPENAI_API_KEY": "your_key"
      }
    }
  }
}
```

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-anything": {
      "command": "python",
      "args": ["/path/to/twin-editor-rag/src/server.py"],
      "env": {
        "OPENAI_API_KEY": "your_key"
      }
    }
  }
}
```

## 📚 Available Tools

### Document Processing

#### `upload_document`
Upload a document file to the server.

```python
# Parameters:
- file_path: str - Path to document file
- doc_id: Optional[str] - Custom document ID

# Returns:
- doc_id: str - Document identifier
- status: str - Upload status
```

#### `process_document`
Process an uploaded document with RAG-Anything.

```python
# Parameters:
- doc_id: str - Document identifier
- parser: Optional[str] - Parser to use (mineru/docling)
- parse_method: Optional[str] - Parse method (auto/ocr/txt)

# Returns:
- doc_id: str
- status: str
- stats: dict - Processing statistics
```

#### `batch_process_documents`
Process multiple documents in batch.

```python
# Parameters:
- file_paths: List[str] - List of file paths
- max_concurrent: Optional[int] - Max parallel processing

# Returns:
- results: List[dict] - Processing results
```

### Query Operations

#### `query_text`
Query the RAG system with text.

```python
# Parameters:
- query: str - Query text
- mode: str - Query mode (hybrid/local/global/naive)
- top_k: Optional[int] - Number of results

# Returns:
- answer: str - RAG answer
- sources: List[dict] - Source documents
```

#### `query_multimodal`
Query with multimodal content (images, tables, equations).

```python
# Parameters:
- query: str - Query text
- multimodal_content: List[dict] - Multimodal content
- mode: str - Query mode

# Returns:
- answer: str - RAG answer with multimodal understanding
```

### Management

#### `list_documents`
List all processed documents.

```python
# Returns:
- documents: List[dict] - Document list with metadata
```

#### `get_document_info`
Get detailed information about a document.

```python
# Parameters:
- doc_id: str - Document identifier

# Returns:
- doc_info: dict - Detailed document information
```

#### `delete_document`
Remove a document from the system.

```python
# Parameters:
- doc_id: str - Document identifier

# Returns:
- status: str - Deletion status
```

## 🔧 Advanced Configuration

### Custom RAG Configuration

```python
# config.json
{
  "rag_config": {
    "enable_image_processing": true,
    "enable_table_processing": true,
    "enable_equation_processing": true,
    "context_window": 2,
    "max_context_tokens": 3000
  },
  "parser_config": {
    "default_parser": "mineru",
    "default_parse_method": "auto"
  }
}
```

### LLM Provider Configuration

Supports multiple providers:
- OpenAI
- Azure OpenAI
- Anthropic (Claude)
- Local models (LM Studio, Ollama)

## 📖 Examples

### Example 1: Process and Query Documents

```python
# Using MCP client
import mcp

client = mcp.Client("rag-anything")

# Upload and process
result = await client.call_tool("upload_document", {
    "file_path": "./research_paper.pdf"
})
doc_id = result["doc_id"]

await client.call_tool("process_document", {
    "doc_id": doc_id
})

# Query
answer = await client.call_tool("query_text", {
    "query": "What are the main findings?",
    "mode": "hybrid"
})
print(answer["answer"])
```

### Example 2: Multimodal Query

```python
# Query with table data
result = await client.call_tool("query_multimodal", {
    "query": "Compare these metrics with document content",
    "multimodal_content": [{
        "type": "table",
        "table_data": "Method,Accuracy\nRAG,95.2%\nBaseline,87.3%",
        "table_caption": "Performance Comparison"
    }],
    "mode": "hybrid"
})
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Test specific functionality
pytest tests/test_tools.py -v
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🔗 Related Projects

- [RAG-Anything](https://github.com/HKUDS/RAG-Anything) - Core RAG framework
- [LightRAG](https://github.com/HKUDS/LightRAG) - Knowledge graph RAG
- [MCP](https://github.com/modelcontextprotocol) - Model Context Protocol

## ⭐ Star History

If you find this useful, please star the repo!
## 🚀 Deployment to Render.com

### Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **OpenAI API Key**: Get your key from [OpenAI Platform](https://platform.openai.com)
3. **Git Repository**: Push your code to GitHub/GitLab

### Option 1: Deploy with render.yaml (Recommended)

1. **Connect Repository**: Link your GitHub/GitLab repo to Render
2. **Set Environment Variables**: In Render dashboard, add:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - Other optional variables from `.env.example`
3. **Deploy**: Render will auto-detect `render.yaml` and deploy

### Option 2: Manual Deployment

1. **Create New Web Service** in Render Dashboard
2. **Configure Service**:
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: Standard (512 MB+ RAM recommended)
3. **Add Disk** (for persistent storage):
   - **Name**: `rag-storage`
   - **Mount Path**: `/app/rag_storage`
   - **Size**: 10 GB
4. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=your_key_here
   LLM_MODEL=gpt-4o-mini
   VISION_MODEL=gpt-4o
   EMBEDDING_MODEL=text-embedding-3-large
   ```
5. **Deploy**: Click "Create Web Service"

### Post-Deployment

Your MCP server will be available at:
```
https://your-app-name.onrender.com/mcp
```

Connect from your MCP client using HTTP transport:
```json
{
  "servers": {
    "rag-document-mcp": {
      "url": "https://your-app-name.onrender.com/mcp",
      "type": "http"
    }
  }
}
```

### Cost Estimation

- **Free Tier**: 750 hours/month (suitable for testing)
- **Starter**: $7/month (recommended for production)
- **Storage**: $0.25/GB/month
## 📧 Contact

For questions or support, please open an issue on GitHub.
