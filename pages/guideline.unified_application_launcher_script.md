# Guideline: Unified Application Launcher Script

## 1. Principle

To streamline the local development of multi-service applications (e.g., backend and frontend), a single Python-based launcher script **MUST** be used as the primary entry point. This script replaces disparate startup files (like `.bat` or `.sh`) to provide a consistent, robust, and centrally managed development environment.

---

## 2. Core Responsibilities of the Launcher

The launcher script is responsible for the entire lifecycle of the local development session. Its key duties are:

-   **Dynamic Port Allocation**: It **MUST** automatically find and assign free TCP ports for services to prevent conflicts. Hardcoding ports is strictly forbidden.
-   **Service Synchronization**: It **MUST** communicate the dynamically allocated port of the backend to the frontend service. The recommended method is through **environment variables**.
-   **Unified Process Management**: It **MUST** start all services (e.g., Uvicorn for FastAPI, Streamlit) as managed subprocesses from a single terminal.
-   **Centralized Logging**: It **MUST** capture the `stdout` and `stderr` streams from all subprocesses and display them in an interleaved, prefixed format (e.g., `[BACKEND]`, `[FRONTEND]`).
-   **Graceful Shutdown**: It **MUST** handle `KeyboardInterrupt` (Ctrl+C) to cleanly terminate all child processes it has spawned.

---

## 3. Implementation Specification

### 3.1. Structure and Location

-   The script **MUST** be named `launcher.py`.
-   It **MUST** be located in the root directory of the project.
-   It **SHOULD** be self-contained, using only standard library dependencies (`subprocess`, `socket`, `os`, `threading`).

### 3.2. Required Functions & Code Examples

The script should be modular. Below are examples of the core functional components.

#### **Port Finding**
A function to identify and return an available port using the `socket` library.

```python
import socket

def find_free_port() -> int:
    """Finds and returns an available TCP port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # Bind to port 0 to let the OS choose a free port
        return s.getsockname()[1]
````

#### **Process Orchestration**

The main orchestration logic uses `subprocess.Popen` to start and manage the services.

```python
import os
import subprocess
import sys

def run_services():
    backend_port = find_free_port()
    print(f"Found free port for backend: {backend_port}")

    # Pass the dynamic port to the backend via command-line arguments
    backend_command = [
        "uv", "run", "uvicorn", "src.backend.main:app", 
        "--host", "127.0.0.1", "--port", str(backend_port)
    ]
    
    # Pass the full backend URL to the frontend via environment variables
    frontend_env = os.environ.copy()
    frontend_env["STREAMLIT_APP_BACKEND_URL"] = f"[http://127.0.0.1](http://127.0.0.1):{backend_port}"
    
    frontend_command = ["uv", "run", "streamlit", "run", "app.py"]

    try:
        # Start backend and frontend as non-blocking subprocesses
        backend_proc = subprocess.Popen(backend_command, cwd="backend")
        frontend_proc = subprocess.Popen(frontend_command, cwd="frontend", env=frontend_env)
        
        # Wait for the frontend process to exit (or for a Ctrl+C)
        frontend_proc.wait()

    except KeyboardInterrupt:
        print("\nShutting down services...")
    finally:
        # Ensure child processes are terminated
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Services stopped.")
```

### 3.3. Application-Side Requirements

#### **Frontend Configuration**

The Streamlit application **MUST** be modified to read the backend's URL from an environment variable. It should also have a sensible default for standalone execution.

```python
# frontend/app.py
import os
import streamlit as st
import requests

# Read the backend URL from the environment variable set by the launcher.
# Provide a default value for running the frontend by itself.
BACKEND_URL = os.getenv("STREAMLIT_APP_BACKEND_URL", "[http://127.0.0.1:8000](http://127.0.0.1:8000)")

st.title("Service Status")
st.write(f"Connecting to backend at: `{BACKEND_URL}`")

try:
    response = requests.get(f"{BACKEND_URL}/api/status")
    st.success("Successfully connected to backend!")
    st.json(response.json())
except requests.RequestException as e:
    st.error(f"Failed to connect to backend: {e}")
```

-----

## 4\. Example Usage

To start the entire application stack, a developer will execute a single command from the project root:

```bash
# First, ensure dependencies are installed (e.g., via uv sync)
# Then, run the launcher:
python launcher.py
```

-----

## 5\. Rationale & Benefits

This approach is mandated because it solves critical development workflow issues:

  - **Prevents "Port-in-Use" Errors**: Eliminates a common source of developer frustration.
  - **Simplifies Debugging**: Provides a single, consolidated view of logs from all services.
  - **Ensures Consistency**: Every developer on the team starts the application in the exact same way.
  - **Improves Developer Experience (DX)**: Replaces complex startup procedures with one command.

