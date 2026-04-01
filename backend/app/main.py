from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional
import json

from .config import Config
from .models import ProcessRequest, PipelineResponse, SourceType
from .services import Pipeline
from .utils import FileHandler

# Validate configuration
Config.validate()

# Create FastAPI app
app = FastAPI(
    title="Autonomous Content Factory",
    description="AI-powered content generation pipeline with multi-agent system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs(Config.OUTPUTS_DIR, exist_ok=True)
os.makedirs(Config.LOGS_DIR, exist_ok=True)
os.makedirs("uploads", exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Autonomous Content Factory",
        "version": "1.0.0"
    }


@app.post("/api/process", response_model=PipelineResponse)
async def process_content(
    source_type: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Main endpoint to process content through the AI agent pipeline
    
    Args:
        source_type: Type of source (text, url, file)
        content: Text content or URL (for text/url source types)
        file: Uploaded file (for file source type)
        
    Returns:
        PipelineResponse with all results and logs
    """
    try:
        # Validate source type
        if source_type not in ["text", "url", "file"]:
            raise HTTPException(status_code=400, detail="Invalid source_type. Must be 'text', 'url', or 'file'")
        
        # Extract content based on source type
        if source_type == "text":
            if not content:
                raise HTTPException(status_code=400, detail="Content is required for text source type")
            source_content = content
            
        elif source_type == "url":
            if not content:
                raise HTTPException(status_code=400, detail="URL is required for url source type")
            try:
                source_content = FileHandler.fetch_url_content(content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
            
        elif source_type == "file":
            if not file:
                raise HTTPException(status_code=400, detail="File is required for file source type")
            try:
                # Read file content
                file_bytes = await file.read()
                source_content = file_bytes.decode('utf-8')
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        # Run the pipeline
        pipeline = Pipeline()
        result = pipeline.execute(source_content)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/outputs/{filename}")
async def get_output(filename: str):
    """
    Retrieve a generated output file
    
    Args:
        filename: Name of the output file
        
    Returns:
        File content as JSON
    """
    file_path = os.path.join(Config.OUTPUTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read output file: {str(e)}")


@app.get("/api/outputs")
async def list_outputs():
    """
    List all generated output files
    
    Returns:
        List of output filenames with metadata
    """
    try:
        outputs = []
        for filename in os.listdir(Config.OUTPUTS_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(Config.OUTPUTS_DIR, filename)
                stat = os.stat(file_path)
                outputs.append({
                    "filename": filename,
                    "created": stat.st_ctime,
                    "size": stat.st_size
                })
        
        # Sort by creation time (newest first)
        outputs.sort(key=lambda x: x['created'], reverse=True)
        
        return {"outputs": outputs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list outputs: {str(e)}")


@app.get("/api/health")
async def health_check():
    """
    Detailed health check
    """
    return {
        "status": "healthy",
        "anthropic_api_configured": bool(Config.ANTHROPIC_API_KEY),
        "model": Config.CLAUDE_MODEL,
        "outputs_dir_exists": os.path.exists(Config.OUTPUTS_DIR),
        "logs_dir_exists": os.path.exists(Config.LOGS_DIR)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)