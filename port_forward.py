from fastapi import FastAPI, Request, Response
import httpx
import json
import sys
import colorama
import yaml

TARGET_URL = "http://localhost:8000"  # inference gateway
LISTEN_PORT = 8001
TARGET_PORT = 8000

app = FastAPI()

@app.api_route("/v1/responses", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_responses(request: Request):
    print(f"Error: llm-d is not supporting The Responses API")
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
        body = await request.body()
        body_json = json.loads(body)
        for message in body_json["messages"]:
            if message.get("role") == "assistant":
                print(colorama.Fore.BLUE + yaml.dump(message) + colorama.Style.RESET_ALL)
            elif message.get("role") == "system":
                print(colorama.Fore.RED + yaml.dump(message) + colorama.Style.RESET_ALL)
            elif message.get("role") == "user":
                print(colorama.Fore.YELLOW + yaml.dump(message) + colorama.Style.RESET_ALL)
            else:
                print(yaml.dump(message))

        
        json.loads(body)  # Validate JSON
        
        resp = await client.request(
            request.method,
            f"{app.state.target_url}/v1/chat/completions",
            content=body,
            headers=dict(request.headers),
            timeout=None,
        )

        print(f"\n\033[1;33m--- Response: {resp.status_code} ---\033[0m")

        responses = [r.lstrip('data: ') for r in resp.iter_lines() if r]
        responses.pop()  # Remove the [DONE] line
        responses_json = [json.loads(r) for r in responses]

        # color the output tokens
        print(colorama.Fore.GREEN)
        for r in responses_json:
            try:
                if r['choices']:
                    token = r['choices'][0]['delta']['content']
                print(token, end='', flush=True)
            except (IndexError, KeyError):
                print("\n\nERROR: Unexpected response format", file=sys.stderr)
                print(yaml.dump(r))
        print(colorama.Style.RESET_ALL)
        
        print(f"\n\033[1;33m--- End of Response ---\033[0m")
        
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
