# RAG-Anything MCP Server - Quick Setup Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd /home/nguyenngocdue/sj-project/twin-editor-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or: venv\Scripts\activate  # On Windows

# Install package
pip install -e .
```

### 2. Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Set your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Test the Server

```bash
# Run basic tests
python tests/test_basic.py
```

### 4. Start the Server

```bash
# Start MCP server
python src/server.py
```

## 🔌 Connect from Applications

### VS Code

Add to your VS Code `settings.json`:

```json
{
  "mcp.servers": {
    "rag-anything": {
      "command": "python",
      "args": ["/home/nguyenngocdue/sj-project/twin-editor-rag/src/server.py"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-anything": {
      "command": "python",
      "args": ["/home/nguyenngocdue/sj-project/twin-editor-rag/src/server.py"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

## 📖 Usage Examples

### Upload and Process a Document

```python
# From any MCP client:

# 1. Upload
result = await client.call_tool("upload_document", {
    "file_path": "./research_paper.pdf"
})

# 2. Process
await client.call_tool("process_document", {
    "doc_id": result["doc_id"]
})

# 3. Query
answer = await client.call_tool("query_text", {
    "query": "What are the main findings?",
    "mode": "hybrid"
})
```

### Multimodal Query

```python
# Query with table data
result = await client.call_tool("query_multimodal", {
    "query": "Compare these metrics",
    "multimodal_content": [{
        "type": "table",
        "table_data": "Method,Score\nRAG,95.2%\nBaseline,87.3%"
    }],
    "mode": "hybrid"
})
```

## 🛠️ Available Tools

1. **upload_document** - Upload files (PDF, Office, images)
2. **process_document** - Process with RAG-Anything
3. **batch_process_documents** - Process multiple files
4. **query_text** - Text queries
5. **query_multimodal** - Multimodal queries (images/tables/equations)
6. **list_documents** - List all documents
7. **get_document_info** - Get document details
8. **delete_document** - Remove documents
9. **get_storage_info** - Storage status
10. **insert_content_list** - Direct content insertion

## 📚 More Examples

Run the examples:

```bash
# View client examples
python examples/client_example.py

# View configuration examples
python examples/mcp_client_config.py
```

## 🐛 Troubleshooting

**Server won't start?**
- Check API key in `.env`
- Verify Python >= 3.10
- Check logs in `rag_mcp_server.log`

**Upload fails?**
- Check file size (max 100MB by default)
- Verify file path is correct
- Check upload directory permissions

**Query returns empty?**
- Process documents first
- Check if documents were processed successfully
- Try different query modes

## 🎯 Next Steps

1. ✅ Test with your own documents
2. ✅ Integrate with your favorite MCP client
3. ✅ Explore multimodal queries
4. ✅ Customize configuration for your needs

For detailed documentation, see [README.md](README.md)
