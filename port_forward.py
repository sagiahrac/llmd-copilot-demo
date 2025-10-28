import json
import subprocess

import httpx
from fastapi import FastAPI, Request, Response

import utils

TARGET_URL = "http://localhost:8000"  # inference gateway
LISTEN_PORT = 8001
TARGET_PORT = 8000

PYTHON_TK_PATH = "clock/.venv/bin/python3.14"
STOPWATCH_APP_PATH = "clock/app.py"

app = FastAPI()
subprocess.Popen([PYTHON_TK_PATH, STOPWATCH_APP_PATH])

@app.api_route("/v1/responses", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_responses(request: Request):
    print("Error: llm-d is not supporting The Responses API")
    error_response = {
        "error": {
            "message": "llm-d is not supporting The Responses API",
            "type": "not_supported_error",
            "code": "responses_api_not_supported"
        }
    }
    return Response(
        content=json.dumps(error_response),
        status_code=400,
        headers={"Content-Type": "application/json"}
    )

@app.api_route("/v1/chat/completions", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_chat_completions(request: Request):
    print(f"\n\033[1;33m--- Request: {request.method} /v1/chat/completions ---\033[0m")

    async with httpx.AsyncClient() as client:
        await client.get("http://127.0.0.1:9000/reset")
        await client.get("http://127.0.0.1:9000/start")

        body = await request.body()

        utils.log_request(request, body)
        utils.print_request_messages(body)
        
        resp = await client.request(
            request.method,
            f"{app.state.target_url}/v1/chat/completions",
            content=body,
            headers=dict(request.headers),
            timeout=None,
        )

        await client.get("http://127.0.0.1:9000/stop")

        elapsed = resp.elapsed.total_seconds()  # total round-trip time
        
        print(f"\n\033[1;33m--- Response: {resp.status_code} ---\033[0m")

        utils.print_response_chunks(resp)
        
        print("\n\033[1;33m--- End of Response ---\033[0m")
        
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def unimplemented_paths(request: Request, path: str):
    print(f"Error: Path /{path} is unimplemented")
    error_response = {
        "error": {
            "message": f"Path /{path} is unimplemented",
            "type": "unimplemented_error",
            "code": "path_not_implemented"
        }
    }
    return Response(
        content=json.dumps(error_response),
        status_code=501,
        headers={"Content-Type": "application/json"}
    )

if __name__ == "__main__":
    import uvicorn

    app.state.target_url = f"http://localhost:{TARGET_PORT}"

    print(f"Starting proxy on port {LISTEN_PORT}, forwarding to {app.state.target_url}")
    print("Transforming 'messages' -> 'prompt' in JSON requests")

    uvicorn.run(app, host="0.0.0.0", port=LISTEN_PORT)
