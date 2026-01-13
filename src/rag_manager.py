"""
RAG Manager - Core LightRAG wrapper for the MCP server
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import setup_logger
from pypdf import PdfReader
from io import BytesIO
from .config import Config

# Setup LightRAG logger
setup_logger("lightrag", level="INFO")

logger = logging.getLogger(__name__)


class RAGManager:
    """Manages LightRAG instance and operations"""

    def __init__(self, config: Config):
        self.config = config
        self.rag: Optional[LightRAG] = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize LightRAG instance"""
        async with self._lock:
            if self._initialized:
                return

            try:
                logger.info("Initializing LightRAG...")

                # Initialize LightRAG with standard functions
                llm_model_kwargs: Dict[str, Any] = {}
                llm_max_tokens = os.getenv("LLM_MAX_TOKENS")
                if llm_max_tokens:
                    try:
                        llm_model_kwargs["max_tokens"] = int(llm_max_tokens)
                    except ValueError:
                        logger.warning(
                            "Invalid LLM_MAX_TOKENS '%s'; ignoring.", llm_max_tokens
                        )

                self.rag = LightRAG(
                    working_dir=str(self.config.storage.rag_storage_dir),
                    llm_model_func=openai_complete_if_cache,
                    embedding_func=openai_embed,
                    llm_model_kwargs=llm_model_kwargs,
                )
                
                # IMPORTANT: Initialize storage backends
                await self.rag.initialize_storages()

                self._initialized = True
                logger.info("LightRAG initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize LightRAG: {e}")
                raise

    async def process_document(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        parser: Optional[str] = None,
        parse_method: str = "auto",
        doc_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a document with LightRAG"""
        if not self._initialized:
            await self.initialize()

        try:
            logger.info(f"Processing document: {file_path}")

            # Detect file type and extract content
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == ".pdf":
                # Extract text from PDF
                content = await self._extract_pdf_content(file_path)
            else:
                # Read as text file
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            # Validate content
            if not content or len(content.strip()) == 0:
                raise ValueError("File contains no content or only whitespace")

            # Insert into LightRAG
            await self.rag.ainsert(content)

            # Get document stats
            stats = {
                "file_path": file_path,
                "doc_id": doc_id or Path(file_path).stem,
                "status": "processed",
                "content_length": len(content),
                "file_type": file_extension,
            }

            logger.info(f"Document processed successfully: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            raise

    async def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            # Read PDF file
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            # Use pypdf to extract text
            pdf_file = BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if reader.is_encrypted:
                logger.warning(f"PDF {file_path} is encrypted, attempting to decrypt...")
                decrypt_result = reader.decrypt("")
                if decrypt_result == 0:
                    raise ValueError("PDF is encrypted and cannot be opened without password")
            
            # Extract text from all pages
            content = ""
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    content += page_text + "\n"
            
            if not content.strip():
                raise ValueError("No text content could be extracted from PDF")
            
            logger.info(f"Extracted {len(content)} characters from {len(reader.pages)} pages")
            return content
            
        except Exception as e:
            logger.error(f"Failed to extract PDF content: {e}")
            raise ValueError(f"Cannot extract content from PDF: {e}")

    async def query_text(
        self, query: str, mode: str = "hybrid", top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """Query RAG with text"""
        if not self._initialized:
            await self.initialize()

        try:
            logger.info(f"Text query: {query[:100]}... (mode: {mode})")

            # Execute query with LightRAG
            result = await self.rag.aquery(query, param=QueryParam(mode=mode))

            return {
                "query": query,
                "answer": result,
                "mode": mode,
            }

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    async def query_multimodal(
        self,
        query: str,
        multimodal_content: List[Dict[str, Any]],
        mode: str = "hybrid",
    ) -> Dict[str, Any]:
        """Query RAG with multimodal content (simplified - text only)"""
        if not self._initialized:
            await self.initialize()

        try:
            logger.info(f"Multimodal query: {query[:100]}...")

            # For now, just do text query with multimodal content as context
            context_text = "\n".join(
                [
                    f"{item.get('type', 'text')}: {item.get('text', item.get('table_data', ''))}"
                    for item in multimodal_content
                ]
            )
            full_query = f"{query}\n\nAdditional Context:\n{context_text}"

            result = await self.rag.aquery(full_query, param=QueryParam(mode=mode))

            return {
                "query": query,
                "answer": result,
                "mode": mode,
                "multimodal_content_count": len(multimodal_content),
            }

        except Exception as e:
            logger.error(f"Multimodal query failed: {e}")
            raise

    async def insert_content_list(
        self,
        content_list: List[Dict[str, Any]],
        file_path: str,
        doc_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Insert pre-parsed content list directly"""
        if not self._initialized:
            await self.initialize()

        try:
            logger.info(f"Inserting content list with {len(content_list)} items")

            # Combine all text content
            combined_text = "\n\n".join(
                [item.get("text", "") for item in content_list if item.get("text")]
            )

            # Insert into LightRAG
            await self.rag.ainsert(combined_text)

            return {
                "status": "inserted",
                "content_count": len(content_list),
                "doc_id": doc_id or Path(file_path).stem,
            }

        except Exception as e:
            logger.error(f"Content insertion failed: {e}")
            raise

    async def get_storage_info(self) -> Dict[str, Any]:
        """Get information about RAG storage"""
        if not self._initialized:
            await self.initialize()

        storage_dir = self.config.storage.rag_storage_dir

        # Count files in storage
        file_count = 0
        if storage_dir.exists():
            file_count = len(list(storage_dir.rglob("*.*")))

        return {
            "storage_dir": str(storage_dir),
            "initialized": self._initialized,
            "file_count": file_count,
        }

    async def shutdown(self):
        """Cleanup resources"""
        logger.info("Shutting down RAG manager")
        try:
            if self.rag and self._initialized:
                await self.rag.finalize_storages()
        except Exception as e:
            logger.error(f"Error finalizing storages: {e}")
        finally:
            self._initialized = False
            self.rag = None
