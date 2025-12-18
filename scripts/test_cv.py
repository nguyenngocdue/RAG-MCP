import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import setup_logger
from lightrag.kg.shared_storage import initialize_pipeline_status
from pypdf import PdfReader
from io import BytesIO

setup_logger("lightrag", level="INFO")

WORKING_DIR = "./rag_storage"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

def extract_pdf_content(file_path: str) -> str:
    """Extract text from PDF"""
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    pdf_file = BytesIO(file_bytes)
    reader = PdfReader(pdf_file)
    
    if reader.is_encrypted:
        reader.decrypt("")
    
    content = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text.strip():
            content += page_text + "\n"
    
    return content

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

async def main():
    rag = None
    try:
        print("=== RAG CV PDF Test ===\n")
        
        # Initialize RAG
        print("1. Initializing RAG...")
        rag = await initialize_rag()
        print("✅ RAG initialized\n")
        
        # Extract and insert CV
        cv_path = "./data/CV_Nguyen_Ngoc_Due_BIM_Developer.pdf"
        print(f"2. Processing CV: {cv_path}")
        
        content = extract_pdf_content(cv_path)
        print(f"✅ Extracted {len(content)} characters\n")
        
        print("3. Inserting into RAG...")
        await rag.ainsert(content)
        print("✅ Inserted successfully\n")
        
        # Query
        print("4. Testing queries...\n")
        
        queries = [
            "Give me Overview of the CV.",
            "What is the work experience in the CV?",
            "What skills are mentioned?",
            "What programming languages and technologies are listed?",
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"Query {i}: {query}")
            result = await rag.aquery(
                query,
                param=QueryParam(mode="hybrid")
            )
            print(f"Answer: {result}...\n")
        
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if rag:
            await rag.finalize_storages()

if __name__ == "__main__":
    asyncio.run(main())
