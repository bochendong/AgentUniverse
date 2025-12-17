"""File storage utilities for handling uploaded files."""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional


# 定义文件存储目录
UPLOAD_DIR = Path("uploads")


def ensure_upload_dir():
    """确保上传目录存在"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def save_uploaded_file(file_path: str, file_content: Optional[bytes] = None) -> str:
    """
    保存上传的文件到存储目录
    
    Args:
        file_path: 原始文件路径或文件名
        file_content: 文件内容（字节），如果为None则从file_path读取
    
    Returns:
        保存后的文件完整路径
    """
    ensure_upload_dir()
    
    # 获取文件名
    original_filename = os.path.basename(file_path)
    file_ext = os.path.splitext(original_filename)[1]
    
    # 生成唯一文件名（避免冲突）
    unique_id = str(uuid.uuid4())[:8]
    stored_filename = f"{unique_id}_{original_filename}"
    stored_path = UPLOAD_DIR / stored_filename
    
    # 保存文件
    if file_content is not None:
        # 如果提供了文件内容，直接写入
        with open(stored_path, 'wb') as f:
            f.write(file_content)
    else:
        # 如果提供了文件路径，复制文件
        if os.path.exists(file_path):
            shutil.copy2(file_path, stored_path)
        else:
            raise FileNotFoundError(f"源文件不存在: {file_path}")
    
    return str(stored_path.absolute())


