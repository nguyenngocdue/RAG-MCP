"""
MCP Tools - Define all available tools for the MCP server
"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import aiofiles
import uuid
from .rag_manager import RAGManager
from .config import Config

logger = logging.getLogger(__name__)


class MCPTools:
    """MCP tool definitions and handlers"""

    def __init__(self, config: Config, rag_manager: RAGManager):
        self.config = config
        self.rag_manager = rag_manager
        self.uploaded_files: Dict[str, Dict[str, Any]] = {}

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions for MCP"""
        return [
            # Document Processing Tools
            {
                "name": "upload_document",
                "description": "Upload a document file to the server for processing. Supports PDF, Office documents (DOC/DOCX/PPT/PPTX/XLS/XLSX), images, and text files.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the document file to upload",
                        },
                        "doc_id": {
                            "type": "string",
                            "description": "Optional custom document ID. If not provided, will be auto-generated.",
                        },
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "process_document",
                "description": "Process an uploaded document with RAG-Anything. Extracts text, images, tables, and equations to build a searchable knowledge base.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document identifier from upload_document",
                        },
                        "parser": {
                            "type": "string",
                            "enum": ["mineru", "docling"],
                            "description": "Parser to use for document processing. Default: mineru",
                        },
                        "parse_method": {
                            "type": "string",
                            "enum": ["auto", "ocr", "txt"],
                            "description": "Parsing method. auto: automatic selection, ocr: force OCR, txt: text only. Default: auto",
                        },
                    },
                    "required": ["doc_id"],
                },
            },
            {
                "name": "batch_process_documents",
                "description": "Process multiple documents in batch for efficiency.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths to process",
                        },
                        "max_concurrent": {
                            "type": "integer",
                            "description": "Maximum number of files to process concurrently",
                        },
                    },
                    "required": ["file_paths"],
                },
            },
            # Query Tools
            {
                "name": "query_text",
                "description": "Query the RAG system with plain text. Retrieves relevant information from processed documents using intelligent search.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or query text",
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["hybrid", "local", "global", "naive"],
                            "description": "Query mode. hybrid: combines local and global search (recommended), local: entity-based search, global: community-based search, naive: vector search only. Default: hybrid",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top results to return",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "query_multimodal",
                "description": "Query with multimodal content such as images, tables, or equations. Allows you to ask questions about or compare content with the knowledge base.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or query text",
                        },
                        "multimodal_content": {
                            "type": "array",
                            "description": "List of multimodal content items (images, tables, equations)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["image", "table", "equation"],
                                    },
                                    "img_path": {"type": "string"},
                                    "image_caption": {"type": "array", "items": {"type": "string"}},
                                    "table_data": {"type": "string"},
                                    "table_caption": {"type": "string"},
                                    "latex": {"type": "string"},
                                    "equation_caption": {"type": "string"},
                                },
                            },
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["hybrid", "local", "global", "naive"],
                            "description": "Query mode. Default: hybrid",
                        },
                    },
                    "required": ["query", "multimodal_content"],
                },
            },
            # Management Tools
            {
                "name": "list_documents",
                "description": "List all uploaded and processed documents with their metadata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "get_document_info",
                "description": "Get detailed information about a specific document.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document identifier",
                        },
                    },
                    "required": ["doc_id"],
                },
            },
            {
                "name": "delete_document",
                "description": "Remove a document from the system (this does not remove it from the knowledge graph, only from the upload tracking).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document identifier to delete",
                        },
                    },
                    "required": ["doc_id"],
                },
            },
            {
                "name": "get_storage_info",
                "description": "Get information about the RAG storage and system status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            # Content Insertion Tools
            {
                "name": "insert_content_list",
                "description": "Insert pre-parsed content directly into the knowledge base. Useful when you have already extracted content from documents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content_list": {
                            "type": "array",
                            "description": "List of content items to insert",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "text": {"type": "string"},
                                    "img_path": {"type": "string"},
                                    "image_caption": {"type": "array"},
                                    "page_idx": {"type": "integer"},
                                },
                            },
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Reference file path for the content",
                        },
                        "doc_id": {
                            "type": "string",
                            "description": "Optional document ID",
                        },
                    },
                    "required": ["content_list", "file_path"],
                },
            },
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call from MCP client"""
        try:
            logger.info(f"Handling tool call: {name}")

            # Route to appropriate handler
            if name == "upload_document":
                return await self._upload_document(**arguments)
            elif name == "process_document":
                return await self._process_document(**arguments)
            elif name == "batch_process_documents":
                return await self._batch_process_documents(**arguments)
            elif name == "query_text":
                return await self._query_text(**arguments)
            elif name == "query_multimodal":
                return await self._query_multimodal(**arguments)
            elif name == "list_documents":
                return await self._list_documents()
            elif name == "get_document_info":
                return await self._get_document_info(**arguments)
            elif name == "delete_document":
                return await self._delete_document(**arguments)
            elif name == "get_storage_info":
                return await self._get_storage_info()
            elif name == "insert_content_list":
                return await self._insert_content_list(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e), "success": False}

    # Tool Handlers

    async def _upload_document(
        self, file_path: str, doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload document handler"""
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.storage.max_file_size:
            raise ValueError(
                f"File too large: {file_size_mb:.2f}MB (max: {self.config.storage.max_file_size}MB)"
            )

        # Generate doc_id if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        # Copy file to uploads directory
        upload_path = self.config.storage.upload_dir / f"{doc_id}_{file_path_obj.name}"
        
        async with aiofiles.open(file_path, "rb") as src:
            content = await src.read()
            async with aiofiles.open(upload_path, "wb") as dst:
                await dst.write(content)

        # Track uploaded file
        self.uploaded_files[doc_id] = {
            "doc_id": doc_id,
            "original_path": str(file_path),
            "upload_path": str(upload_path),
            "file_name": file_path_obj.name,
            "file_size_mb": file_size_mb,
            "status": "uploaded",
        }

        logger.info(f"Document uploaded: {doc_id}")

        return {
            "success": True,
            "doc_id": doc_id,
            "file_name": file_path_obj.name,
            "file_size_mb": round(file_size_mb, 2),
            "status": "uploaded",
        }

    async def _process_document(
        self,
        doc_id: str,
        parser: Optional[str] = None,
        parse_method: str = "auto",
    ) -> Dict[str, Any]:
        """Process document handler"""
        if doc_id not in self.uploaded_files:
            raise ValueError(f"Document not found: {doc_id}")

        file_info = self.uploaded_files[doc_id]
        file_path = file_info["upload_path"]

        # Process with RAG
        result = await self.rag_manager.process_document(
            file_path=file_path,
            parser=parser,
            parse_method=parse_method,
            doc_id=doc_id,
        )

        # Update status
        file_info["status"] = "processed"
        file_info["processing_result"] = result

        return {
            "success": True,
            "doc_id": doc_id,
            "status": "processed",
            "details": result,
        }

    async def _batch_process_documents(
        self, file_paths: List[str], max_concurrent: Optional[int] = None
    ) -> Dict[str, Any]:
        """Batch process documents handler"""
        if max_concurrent is None:
            max_concurrent = self.config.server.max_concurrent_files

        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_one(file_path: str):
            async with semaphore:
                try:
                    # Upload
                    upload_result = await self._upload_document(file_path)
                    doc_id = upload_result["doc_id"]

                    # Process
                    process_result = await self._process_document(doc_id)

                    return {
                        "file_path": file_path,
                        "success": True,
                        "doc_id": doc_id,
                        "result": process_result,
                    }
                except Exception as e:
                    return {
                        "file_path": file_path,
                        "success": False,
                        "error": str(e),
                    }

        # Process all files
        tasks = [process_one(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        return {
            "success": True,
            "total": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results,
        }

    async def _query_text(
        self, query: str, mode: str = "hybrid", top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """Text query handler"""
        result = await self.rag_manager.query_text(query=query, mode=mode, top_k=top_k)
        return {"success": True, **result}

    async def _query_multimodal(
        self, query: str, multimodal_content: List[Dict[str, Any]], mode: str = "hybrid"
    ) -> Dict[str, Any]:
        """Multimodal query handler"""
        result = await self.rag_manager.query_multimodal(
            query=query, multimodal_content=multimodal_content, mode=mode
        )
        return {"success": True, **result}

    async def _list_documents(self) -> Dict[str, Any]:
        """List documents handler"""
        documents = list(self.uploaded_files.values())
        return {
            "success": True,
            "count": len(documents),
            "documents": documents,
        }

    async def _get_document_info(self, doc_id: str) -> Dict[str, Any]:
        """Get document info handler"""
        if doc_id not in self.uploaded_files:
            raise ValueError(f"Document not found: {doc_id}")

        return {"success": True, "document": self.uploaded_files[doc_id]}

    async def _delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete document handler"""
        if doc_id not in self.uploaded_files:
            raise ValueError(f"Document not found: {doc_id}")

        file_info = self.uploaded_files[doc_id]

        # Delete uploaded file
        upload_path = Path(file_info["upload_path"])
        if upload_path.exists():
            upload_path.unlink()

        # Remove from tracking
        del self.uploaded_files[doc_id]

        return {
            "success": True,
            "doc_id": doc_id,
            "status": "deleted",
        }

    async def _get_storage_info(self) -> Dict[str, Any]:
        """Get storage info handler"""
        info = await self.rag_manager.get_storage_info()
        info["uploaded_documents"] = len(self.uploaded_files)
        info["success"] = True
        return info

    async def _insert_content_list(
        self, content_list: List[Dict[str, Any]], file_path: str, doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Insert content list handler"""
        result = await self.rag_manager.insert_content_list(
            content_list=content_list, file_path=file_path, doc_id=doc_id
        )
        return {"success": True, **result}
