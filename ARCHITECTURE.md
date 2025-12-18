# Quy trình hoạt động của RAG-Anything MCP Server

## 📋 Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP CLIENT                                │
│              (Claude Desktop / VS Code)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ MCP Protocol (stdio)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SERVER (server.py)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Handler: list_tools() → Liệt kê tools                   │  │
│  │  Handler: call_tool()  → Gọi tool và xử lý               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TOOLS LAYER (tools.py)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • upload_document()     - Upload file                    │  │
│  │  • process_document()    - Process & insert vào RAG      │  │
│  │  • query_text()          - Query RAG                      │  │
│  │  • list_documents()      - Quản lý documents             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  RAG MANAGER (rag_manager.py)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • initialize()           - Khởi tạo LightRAG            │  │
│  │  • process_document()     - Extract PDF → insert RAG     │  │
│  │  • query_text()           - Query với LightRAG           │  │
│  │  • _extract_pdf_content() - Extract text từ PDF          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      LIGHTRAG LIBRARY                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • ainsert()              - Insert text vào knowledge graph│ │
│  │  • aquery()               - Query từ knowledge graph      │  │
│  │  • initialize_storages()  - Khởi tạo storage              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        STORAGE                                   │
│  • rag_storage/                                                  │
│    - graph_chunk_entity_relation.graphml (Knowledge Graph)      │
│    - vdb_entities.json (Vector DB - entities)                   │
│    - vdb_chunks.json (Vector DB - text chunks)                  │
│    - kv_store_*.json (Key-value stores)                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Quy trình xử lý khi user upload PDF

### Bước 1: User request từ Claude/VS Code
```
User: "Upload file CV_Nguyen_Ngoc_Due_Developer_Dynamo.pdf và query thông tin"
```

### Bước 2: MCP Client gọi tool `upload_document`
```json
{
  "tool": "upload_document",
  "arguments": {
    "file_path": "/path/to/CV_Nguyen_Ngoc_Due_Developer_Dynamo.pdf"
  }
}
```

**Flow trong code:**
1. **server.py** → `call_tool()` handler nhận request
2. **tools.py** → `_upload_document()` được gọi
   ```python
   async def _upload_document(self, file_path: str, doc_id: str = None):
       # Copy file vào uploads/
       # Tạo doc_id
       # Lưu metadata
       return {"doc_id": "...", "file_path": "...", "status": "uploaded"}
   ```

### Bước 3: Client gọi tool `process_document`
```json
{
  "tool": "process_document",
  "arguments": {
    "doc_id": "cv_nguyen_ngoc_due"
  }
}
```

**Flow trong code:**
1. **tools.py** → `_process_document()` 
   ```python
   async def _process_document(self, doc_id: str, ...):
       # Lấy file_path từ doc_id
       # Gọi rag_manager.process_document()
   ```

2. **rag_manager.py** → `process_document()`
   ```python
   async def process_document(self, file_path: str, ...):
       # Detect file type (.pdf)
       content = await self._extract_pdf_content(file_path)  # ← Extract PDF
       await self.rag.ainsert(content)  # ← Insert vào LightRAG
   ```

3. **rag_manager.py** → `_extract_pdf_content()`
   ```python
   async def _extract_pdf_content(self, file_path: str) -> str:
       # Đọc PDF với pypdf
       reader = PdfReader(file_path)
       # Extract text từ tất cả pages
       content = "..."
       return content
   ```

4. **LightRAG** → `ainsert(content)`
   - Chia text thành chunks
   - Extract entities (người, địa điểm, tổ chức...)
   - Extract relationships giữa entities
   - Build knowledge graph
   - Embed text chunks + entities
   - Lưu vào storage (graphml + json files)

### Bước 4: Client gọi tool `query_text`
```json
{
  "tool": "query_text",
  "arguments": {
    "query": "Kinh nghiệm làm việc của Nguyễn Ngọc Duệ là gì?"
  }
}
```

**Flow trong code:**
1. **tools.py** → `_query_text()`
2. **rag_manager.py** → `query_text()`
   ```python
   async def query_text(self, query: str, mode: str = "hybrid"):
       result = await self.rag.aquery(query, param=QueryParam(mode=mode))
       return {"query": query, "answer": result}
   ```

3. **LightRAG** → `aquery()`
   - Extract keywords từ query
   - Search trong knowledge graph (entities + relations)
   - Vector search trong text chunks
   - Kết hợp results (hybrid mode)
   - Generate answer với LLM (GPT-4o-mini)
   - Return answer

### Bước 5: Return kết quả cho user
```
Answer: Nguyễn Ngọc Duệ có hơn 3 năm kinh nghiệm...
```

## 🚀 Khởi động server

### Cách 1: Standalone test (như test_cv.py)
```python
# Chạy trực tiếp không qua MCP protocol
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

async def main():
    rag = LightRAG(...)
    await rag.initialize_storages()
    await rag.ainsert(content)
    result = await rag.aquery(query)

asyncio.run(main())
```

### Cách 2: MCP Server (production)
```bash
# 1. Claude Desktop/VS Code đọc mcp.json
# 2. Execute: python src/server.py
# 3. Server chạy và lắng nghe qua stdio
# 4. Client gửi MCP protocol messages
# 5. Server xử lý và trả về results
```

## 📁 Cấu trúc files quan trọng

```
twin-editor-rag/
├── src/
│   ├── server.py       ← Entry point, MCP protocol handler
│   ├── tools.py        ← Tool definitions & handlers
│   ├── rag_manager.py  ← LightRAG wrapper + PDF extraction
│   └── config.py       ← Configuration (API keys, models...)
├── data/
│   └── CV_*.pdf        ← Input documents
├── uploads/            ← Uploaded files storage
├── rag_storage/        ← LightRAG storage (knowledge graph + vectors)
│   ├── graph_chunk_entity_relation.graphml
│   ├── vdb_entities.json
│   ├── vdb_chunks.json
│   └── kv_store_*.json
├── mcp.json           ← MCP server config
└── test_cv.py         ← Standalone test script
```

## 🔑 Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-...          # Bắt buộc
LLM_MODEL=gpt-4o-mini          # Model cho extraction & query
EMBEDDING_MODEL=text-embedding-3-small
RAG_STORAGE_DIR=./rag_storage
UPLOAD_DIR=./uploads
```

## 💡 Tóm lại

1. **User → Claude** yêu cầu upload & query PDF
2. **Claude → MCP Server** gọi tools qua MCP protocol
3. **MCP Server** delegate to appropriate handlers
4. **RAG Manager** extract PDF → insert vào LightRAG
5. **LightRAG** build knowledge graph & vector database
6. **Query** → Search graph + vectors → Generate answer
7. **Return** answer về cho user qua Claude
