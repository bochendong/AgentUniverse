"""Session database operations using SQLite."""

import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.database.agent_db import get_db_path, init_db


def init_session_db(db_path: Optional[str] = None) -> None:
    """Initialize the database with sessions and conversations tables."""
    db_path = get_db_path(db_path)
    
    # Initialize agent DB first (creates directory if needed)
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
        ON conversations(session_id)
    """)
    
    conn.commit()
    conn.close()


def create_session(title: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new session.
    
    Args:
        title: Optional session title
        db_path: Optional database path
        
    Returns:
        Dictionary with session information
    """
    import uuid
    
    session_id = str(uuid.uuid4())
    db_path = get_db_path(db_path)
    init_session_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO sessions (id, title)
        VALUES (?, ?)
    """, (session_id, title))
    
    conn.commit()
    conn.close()
    
    return {
        'id': session_id,
        'title': title or f"Session {session_id[:8]}",
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }


def get_session(session_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a session by ID.
    
    Args:
        session_id: Session ID
        db_path: Optional database path
        
    Returns:
        Session dictionary or None if not found
    """
    db_path = get_db_path(db_path)
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'updated_at': row[3]
        }
    
    return None


def list_sessions(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all sessions.
    
    Args:
        db_path: Optional database path
        
    Returns:
        List of session dictionaries
    """
    db_path = get_db_path(db_path)
    
    # Initialize session DB (creates tables if they don't exist)
    init_session_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if sessions table exists (in case of older database)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='sessions'
    """)
    if not cursor.fetchone():
        # Table doesn't exist, create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    cursor.execute("SELECT id, title, created_at, updated_at FROM sessions ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    sessions = []
    for row in rows:
        sessions.append({
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'updated_at': row[3]
        })
    
    return sessions


def delete_session(session_id: str, db_path: Optional[str] = None) -> bool:
    """
    Delete a session and all its conversations.
    
    Args:
        session_id: Session ID
        db_path: Optional database path
        
    Returns:
        True if deleted, False if not found
    """
    db_path = get_db_path(db_path)
    
    if not os.path.exists(db_path):
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def add_conversation(
    session_id: str,
    role: str,
    content: str,
    db_path: Optional[str] = None
) -> None:
    """
    Add a conversation to a session.
    
    Args:
        session_id: Session ID
        role: Message role (user/assistant)
        content: Message content
        db_path: Optional database path
    """
    db_path = get_db_path(db_path)
    init_session_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO conversations (session_id, role, content)
        VALUES (?, ?, ?)
    """, (session_id, role, content))
    
    # Update session updated_at timestamp
    cursor.execute("""
        UPDATE sessions 
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (session_id,))
    
    conn.commit()
    conn.close()


def get_conversations(session_id: str, db_path: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Get all conversations for a session.
    
    Args:
        session_id: Session ID
        db_path: Optional database path
        
    Returns:
        List of conversation dictionaries
    """
    db_path = get_db_path(db_path)
    
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT role, content 
        FROM conversations 
        WHERE session_id = ? 
        ORDER BY created_at ASC
    """, (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conversations.append({
            'role': row[0],
            'content': row[1]
        })
    
    return conversations
