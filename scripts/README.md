# Startup and Stop Scripts

This directory contains scripts to start and stop the frontend and backend servers.

## Scripts

### `start_backend.sh`
Starts the FastAPI backend server on `http://localhost:8000`.

**Features:**
- Automatically creates and activates a Python virtual environment if needed
- Installs/updates dependencies from `requirements.txt`
- Searches for backend API file (`main.py`, `app.py`, or `server.py` in `backend/` directory)
- Starts uvicorn server with auto-reload enabled

**Usage:**
```bash
./scripts/start_backend.sh
```

### `stop_backend.sh`
Stops the FastAPI backend server running on port 8000.

**Features:**
- Finds and stops processes using port 8000
- Gracefully terminates uvicorn processes
- Force kills if necessary

**Usage:**
```bash
./scripts/stop_backend.sh
```

### `start_frontend.sh`
Starts the Vite frontend development server on `http://localhost:3001`.

**Features:**
- Checks and installs npm dependencies if needed
- Creates `.env` file with default API URL if missing
- Starts Vite dev server with proxy configuration

**Usage:**
```bash
./scripts/start_frontend.sh
```

### `stop_frontend.sh`
Stops the Vite frontend development server running on port 3001.

**Features:**
- Finds and stops processes using port 3001
- Gracefully terminates Vite/node processes
- Force kills if necessary

**Usage:**
```bash
./scripts/stop_frontend.sh
```

### `start_all.sh`
Starts both backend and frontend servers in the background.

**Usage:**
```bash
./scripts/start_all.sh
```

### `stop_all.sh`
Stops both backend and frontend servers.

**Usage:**
```bash
./scripts/stop_all.sh
```

## Quick Start

### Starting Services

1. **Start Both Services:**
   ```bash
   ./scripts/start_all.sh
   ```

   Or start them separately:

2. **Start Backend:**
   ```bash
   ./scripts/start_backend.sh
   ```

3. **Start Frontend (in a new terminal):**
   ```bash
   ./scripts/start_frontend.sh
   ```

4. **Access the application:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8000

### Stopping Services

1. **Stop Both Services:**
   ```bash
   ./scripts/stop_all.sh
   ```

   Or stop them separately:

2. **Stop Backend:**
   ```bash
   ./scripts/stop_backend.sh
   ```

3. **Stop Frontend:**
   ```bash
   ./scripts/stop_frontend.sh
   ```

## Configuration

### Backend
- Default port: `8000`
- API file location: `backend/main.py` (or `app.py` or `server.py`)
- Virtual environment: `venv/` or `.venv/` in project root

### Frontend
- Default port: `3001`
- API URL: Set via `VITE_API_URL` environment variable in `frontend/.env`
- Proxy configuration: Automatically proxies `/api/*` requests to backend

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

### Backend
Set environment variables as needed for your backend configuration.
