# LLMD Demo

This project demonstrates a proxy server that forwards requests to a local inference gateway while providing custom error handling and request/response logging.

## Prerequisites

### 1. Download Visual Studio Code Insiders

Download and install VS Code Insiders from:
https://code.visualstudio.com/insiders/

### 2. Install Required VS Code Extensions

Install the following extensions:

**Python Extension:**
https://marketplace.visualstudio.com/items?itemName=ms-python.python

**GitHub Copilot Extensions:**
- https://marketplace.visualstudio.com/items?itemName=GitHub.copilot
- https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat

### 3. Install Taskfile

Install Task (a task runner / build tool) from:
https://taskfile.dev/

### 4. Install uv

Install uv (Python package manager) from:
https://github.com/astral-sh/uv

### 5. Install Python Tkinter

Install Python Tkinter using Homebrew:
```bash
brew install python-tk
```

### 6. Install Dependencies for Main App

Install dependencies for the main proxy application:
```bash
uv sync
```

### 7. Create Virtual Environment for Stopwatch App

Create a virtual environment in the clock directory for the stopwatch app:
```bash
cd clock
python3.14 -m venv ./.venv
python3.14 -m pip install fastapi uvicorn
```

### 8. OpenShift Authentication

Authenticate to the fusionv6 OpenShift cluster (specific instructions should be provided by your cluster administrator).

## Project Structure

- `port_forward.py` - Main proxy server that forwards requests to the inference gateway
- `errors.py` - Centralized error response handling
- `utils.py` - Utility functions for logging and request processing
- `.vscode/settings.json` - VS Code configuration with custom Copilot models

## Configuration

The project is configured to use custom AI models through GitHub Copilot:
- `pytorch-conference-demo` (RedHatAI/Qwen3-32B-NVFP4)

Both models are configured to use the local proxy at `http://localhost:8001/v1`.

## Keyboard Shortcuts

- `Cmd+Shift+I` - Open GitHub Copilot Chat

## Usage

1. Set up port forwarding to the inference gateway:
   ```bash
   task port-forward-inference-gateway
   ```
2. Run the proxy server:
   ```bash
   uv run port_forward.py
   ```
3. The proxy will listen on port 8001 and forward requests to the inference gateway
4. A stopwatch application will automatically start to track request timing

## API Endpoints

- `POST /v1/chat/completions` - Proxies chat completion requests to the inference gateway
- `* /v1/responses` - Returns error (Responses API not supported)
- `* /{path}` - Returns error for unimplemented paths

## Features

- Request/response logging with colored output
- Automatic stopwatch timing for requests
- Centralized error handling
- Support for all HTTP methods (GET, POST, PUT, DELETE, PATCH)
