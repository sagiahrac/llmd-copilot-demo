

import json
import pathlib
import sys
import time

import colorama
import yaml
from fastapi import Request
from httpx import Response


def log_request(request: Request, body: bytes) -> None:
    request_log = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body.decode("utf-8")
    }
    
    log_dir = pathlib.Path("logs/requests")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"request_{timestamp}.yaml"
    log_file.write_text(yaml.dump(request_log))

def print_request_messages(body: bytes) -> None:
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

def print_response_chunks(response: Response) -> None:
    responses = [r.lstrip('data: ') for r in response.iter_lines() if r]
    responses.pop()  # Remove the [DONE] line
    responses_json = [json.loads(r) for r in responses]

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