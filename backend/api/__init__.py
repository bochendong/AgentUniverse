"""API routes module - organizes all API endpoints."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.tools.tool_discovery import init_tool_system
from backend.api.utils import get_top_level_agent
import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    # Load .env from project root
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[Startup] Loaded .env file from {env_path}")
    else:
        print(f"[Startup] No .env file found at {env_path}, using system environment variables")
except ImportError:
    print("[Startup] python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"[Startup] Warning: Failed to load .env file: {e}")

# Import all route modules
from backend.api import (
    top_level_agent,
    sessions,
    agents,
    notebooks,
    tools,
    upload,
)

# Create FastAPI app
app = FastAPI(title="AgentUniverse API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tool system at startup
@app.on_event("startup")
async def startup_event():
    """Initialize tool system on application startup."""
    try:
        # Setup logging first
        from backend.utils.logging_config import setup_logging
        log_path = setup_logging()
        print(f"[Startup] Logging configured. Log directory: {log_path}")
        
        init_tool_system()
        print("[Startup] Tool system initialized successfully")
        
        # Verify TopLevelAgent tools are correctly created
        print("[Startup] Verifying TopLevelAgent tools...")
        try:
            agent = get_top_level_agent()
            if agent.tools:
                tool_names = [getattr(t, '_tool_id', 'unknown') for t in agent.tools]
                print(f"[Startup] TopLevelAgent has {len(agent.tools)} tools: {tool_names}")
                
                # Check for required tools
                required_tools = ['send_message', 'generate_outline']
                missing = [t for t in required_tools if t not in tool_names]
                if missing:
                    print(f"[Startup] ⚠️  WARNING: Missing tools: {missing}")
                else:
                    print(f"[Startup] ✅ All required tools are present")
            else:
                print(f"[Startup] ⚠️  WARNING: TopLevelAgent has no tools!")
        except Exception as e:
            print(f"[Startup] ⚠️  Warning: Failed to verify TopLevelAgent tools: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"[Startup] Warning: Failed to initialize tool system: {e}")

# Register all route modules
app.include_router(top_level_agent.router)
app.include_router(sessions.router)
app.include_router(agents.router)
app.include_router(notebooks.router)
app.include_router(tools.router)
app.include_router(upload.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AgentUniverse API", "version": "1.0.0"}
