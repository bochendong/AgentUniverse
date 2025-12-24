"""File upload API routes."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.tools.utils import save_uploaded_file, ensure_upload_dir
import os

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the server."""
    try:
        # Ensure upload directory exists
        ensure_upload_dir()
        
        # Read file content
        file_content = await file.read()
        
        # Save file
        stored_path = save_uploaded_file(file.filename, file_content)
        
        return {
            "filename": os.path.basename(stored_path),
            "path": stored_path,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
