"""FastAPI main application entry point for AgentUniverse backend."""

# Import the app from the api module
from backend.api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
