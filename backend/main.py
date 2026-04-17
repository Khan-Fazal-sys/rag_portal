from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
from typing import List
from document_processor import DocumentProcessor
from rag_chain import RAGChain

app = FastAPI(title="Document Portal API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
doc_processor = DocumentProcessor()
rag_chain = RAGChain()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document based on type
        if file.filename.endswith('.pdf'):
            documents = await doc_processor.process_pdf(file_path)
        elif file.filename.endswith('.txt'):
            documents = await doc_processor.process_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Add to vector store
        rag_chain.add_documents(documents)
        
        return JSONResponse({
            "status": "success",
            "message": f"Processed {len(documents)} chunks from {file.filename}"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_document(query: dict):
    """Ask a question about uploaded documents"""
    try:
        question = query.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        result = rag_chain.query(question)
        return JSONResponse({
            "answer": result["answer"],
            "sources": result["sources"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)