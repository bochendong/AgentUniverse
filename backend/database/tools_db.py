"""Tools database management - stores metadata about function tools."""

import sqlite3
import json
import os
from typing import Optional, Dict, Any, List

# Use the same DB directory as agent_db
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
DEFAULT_DB_PATH = os.path.join(DB_DIR, "agent_data.db")


def get_db_path(db_path: Optional[str] = None) -> str:
    """Get database path, using the same path as agent_db."""
    if db_path:
        return db_path
    # Ensure the db directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    return DEFAULT_DB_PATH


def init_tools_db(db_path: Optional[str] = None) -> None:
    """Initialize tools database table."""
    db_path = get_db_path(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tools table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            task TEXT,
            agent_type TEXT,
            input_params TEXT,
            output_type TEXT,
            output_description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add output_description column if it doesn't exist (migration)
    try:
        cursor.execute("ALTER TABLE tools ADD COLUMN output_description TEXT")
    except sqlite3.OperationalError:
        # Column already exists, ignore
        pass
    
    # Add tool_type column if it doesn't exist (migration)
    try:
        cursor.execute("ALTER TABLE tools ADD COLUMN tool_type TEXT DEFAULT 'function'")
    except sqlite3.OperationalError:
        # Column already exists, ignore
        pass
    
    # Add agent_class_name column if it doesn't exist (migration)
    try:
        cursor.execute("ALTER TABLE tools ADD COLUMN agent_class_name TEXT")
    except sqlite3.OperationalError:
        # Column already exists, ignore
        pass
    
    conn.commit()
    conn.close()


def save_tool(
    tool_id: str,
    name: str,
    description: str,
    task: str,
    agent_type: str,
    input_params: Dict[str, Any],
    output_type: str,
    output_description: Optional[str] = None,
    tool_type: str = "function",
    agent_class_name: Optional[str] = None,
    db_path: Optional[str] = None
) -> bool:
    """Save or update a tool in the database.
    
    Args:
        tool_id: Unique tool identifier
        name: Tool name
        description: Tool description
        task: Task description
        agent_type: Agent type that uses this tool
        input_params: Input parameters dictionary
        output_type: Output type
        output_description: Output description (optional)
        tool_type: Type of tool - "function" or "agent_as_tool" (default: "function")
        agent_class_name: For agent_as_tool type, the class name of the agent (optional)
        db_path: Database path (optional)
    """
    db_path = get_db_path(db_path)
    init_tools_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    input_params_json = json.dumps(input_params, ensure_ascii=False)
    
    cursor.execute("""
        INSERT OR REPLACE INTO tools 
        (id, name, description, task, agent_type, input_params, output_type, output_description, tool_type, agent_class_name, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (tool_id, name, description, task, agent_type, input_params_json, output_type, output_description, tool_type, agent_class_name))
    
    conn.commit()
    conn.close()
    return True


def get_tool(tool_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a tool by ID."""
    db_path = get_db_path(db_path)
    init_tools_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'task': row[3],
            'agent_type': row[4],
            'input_params': json.loads(row[5]) if row[5] else {},
            'output_type': row[6],
            'output_description': row[7],
            'created_at': row[8],
            'updated_at': row[9],
        }
        # Add new fields if they exist (for backward compatibility)
        if len(row) > 10:
            result['tool_type'] = row[10] if row[10] else 'function'
        else:
            result['tool_type'] = 'function'
        if len(row) > 11:
            result['agent_class_name'] = row[11]
        else:
            result['agent_class_name'] = None
        return result
    return None


def get_all_tools(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all tools."""
    db_path = get_db_path(db_path)
    init_tools_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tools ORDER BY agent_type, name")
    rows = cursor.fetchall()
    conn.close()
    
    tools = []
    for row in rows:
        tool = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'task': row[3],
            'agent_type': row[4],
            'input_params': json.loads(row[5]) if row[5] else {},
            'output_type': row[6],
            'output_description': row[7],
            'created_at': row[8],
            'updated_at': row[9],
        }
        # Add new fields if they exist (for backward compatibility)
        if len(row) > 10:
            tool['tool_type'] = row[10] if row[10] else 'function'
        else:
            tool['tool_type'] = 'function'
        if len(row) > 11:
            tool['agent_class_name'] = row[11]
        else:
            tool['agent_class_name'] = None
        tools.append(tool)
    
    return tools


def get_tools_by_names(tool_names: List[str], db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get multiple tools by their names."""
    if not tool_names:
        return []
    
    db_path = get_db_path(db_path)
    init_tools_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create placeholders for SQL IN clause
    placeholders = ','.join('?' * len(tool_names))
    cursor.execute(f"SELECT * FROM tools WHERE name IN ({placeholders})", tool_names)
    rows = cursor.fetchall()
    conn.close()
    
    tools = []
    for row in rows:
        tool = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'task': row[3],
            'agent_type': row[4],
            'input_params': json.loads(row[5]) if row[5] else {},
            'output_type': row[6],
            'output_description': row[7],
            'created_at': row[8],
            'updated_at': row[9],
        }
        # Add new fields if they exist (for backward compatibility)
        if len(row) > 10:
            tool['tool_type'] = row[10] if row[10] else 'function'
        else:
            tool['tool_type'] = 'function'
        if len(row) > 11:
            tool['agent_class_name'] = row[11]
        else:
            tool['agent_class_name'] = None
        tools.append(tool)
    
    return tools


def get_tools_by_ids(tool_ids: List[str], db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get multiple tools by their IDs."""
    if not tool_ids:
        return []
    
    db_path = get_db_path(db_path)
    init_tools_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create placeholders for SQL IN clause
    placeholders = ','.join('?' * len(tool_ids))
    cursor.execute(f"SELECT * FROM tools WHERE id IN ({placeholders})", tool_ids)
    rows = cursor.fetchall()
    conn.close()
    
    tools = []
    for row in rows:
        tool = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'task': row[3],
            'agent_type': row[4],
            'input_params': json.loads(row[5]) if row[5] else {},
            'output_type': row[6],
            'output_description': row[7],
            'created_at': row[8],
            'updated_at': row[9],
        }
        # Add new fields if they exist (for backward compatibility)
        if len(row) > 10:
            tool['tool_type'] = row[10] if row[10] else 'function'
        else:
            tool['tool_type'] = 'function'
        if len(row) > 11:
            tool['agent_class_name'] = row[11]
        else:
            tool['agent_class_name'] = None
        tools.append(tool)
    
    return tools


def delete_tool(tool_id: str, db_path: Optional[str] = None) -> bool:
    """Delete a tool from the database."""
    db_path = get_db_path(db_path)
    init_tools_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tools WHERE id = ?", (tool_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted
