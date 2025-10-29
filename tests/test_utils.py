import json
import colorama

from proxy.utils import print_request_messages


def test_print_request_messages(capsys):
    """Test printing messages with different roles and appropriate colors."""
    body = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "What's the weather like?"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you with weather information."
            }
        ]
    }).encode()
    
    print_request_messages(body)
    
    captured = capsys.readouterr()
    
    # Check that all messages are printed with appropriate colors
    assert colorama.Fore.RED in captured.out  # system message
    assert colorama.Fore.YELLOW in captured.out  # user message
    assert colorama.Fore.BLUE in captured.out  # assistant message
    
    # Check content is present
    assert "You are a helpful assistant." in captured.out
    assert "What's the weather like?" in captured.out
    assert "I'd be happy to help you with weather information." in captured.out