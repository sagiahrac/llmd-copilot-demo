import json
import random
import time
import os
import urllib.request

def generate_random_text(length):
    """Generate random text of specified length."""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !@#$%^&*()_+-=[]{}|;:,.<>?/~`'
    return 'hi! ' + ''.join(random.choice(chars) for _ in range(length))

def send_request(prompt, request_id):
    """Send a single request to the chat completions endpoint."""
    model = os.getenv('MODEL', 'ibm-granite/granite-3.1-8b-instruct')
    url = "http://localhost:8001/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    start_time = time.time()
    
    try:
        with urllib.request.urlopen(req) as response:
            response_time = time.time() - start_time
            if response.status == 200:
                print(f"Request {request_id}: SUCCESS - {response_time:.2f}s")
                return True
            else:
                print(f"Request {request_id}: ERROR {response.status}")
                return False
    except Exception as e:
        response_time = time.time() - start_time
        print(f"Request {request_id}: FAILED - {e}")
        return False

def main():
    """Send multiple requests with random text."""
    num_requests = 20
    delay = 1.0  # seconds between requests
    
    print(f"🚀 Sending {num_requests} requests with random text (~1000 chars each)")
    print(f"📍 Target: http://localhost:8001/v1/chat/completions")
    print("=" * 50)
    
    successful = 0
    
    for i in range(num_requests):
        print(f"Sending request {i+1}/{num_requests}...")
        
        # Generate random text
        prompt = generate_random_text(length=500)
        
        # Send request
        if send_request(prompt, i+1):
            successful += 1
        
        # Wait between requests (except last one)
        if i < num_requests - 1:
            time.sleep(delay)
    
    print("\n" + "=" * 50)
    print(f"✅ Completed: {successful}/{num_requests} successful")

if __name__ == "__main__":
    main()