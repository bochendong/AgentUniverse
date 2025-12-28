"""File upload API routes."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.tools.utils import save_uploaded_file, ensure_upload_dir
from backend.tools.agent_as_tools.section_creators.utils import get_file_content
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


@router.get("/file-content")
async def get_file_content_endpoint(file_path: str):
    """Get file content by file path."""
    try:
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path parameter is required")
        
        # 解析文件路径（支持相对路径和仅文件名）
        from backend.tools.agent_as_tools.section_creators.utils import _resolve_file_path
        resolved_path = _resolve_file_path(file_path)
        
        if not os.path.exists(resolved_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path} (解析后: {resolved_path})")
        
        if not os.path.isfile(resolved_path):
            raise HTTPException(status_code=400, detail=f"Path is not a file: {file_path} (解析后: {resolved_path})")
        
        # Get file extension
        file_ext = os.path.splitext(resolved_path)[1].lower()
        file_name = os.path.basename(resolved_path)
        
        # Read file content based on type
        if file_ext == '.pdf':
            # For PDF, return a message indicating it's a PDF
            return {
                "filename": file_name,
                "file_path": resolved_path,
                "content": "[PDF文件内容，请使用PDF阅读器查看]",
                "file_type": "pdf",
                "message": "PDF文件内容需要特殊处理，无法直接显示文本内容。"
            }
        else:
            # For text-based files, read content (get_file_content内部会再次解析路径，但使用resolved_path更高效)
            try:
                content = get_file_content(resolved_path)
                return {
                    "filename": file_name,
                    "file_path": resolved_path,
                    "content": content,
                    "file_type": file_ext.replace('.', ''),
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file content: {str(e)}")
