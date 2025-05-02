import requests
import json

# Webhook URL - adjust this if your server is running on a different URL
WEBHOOK_URL = "http://localhost:8000/webhook/eleven-labs"

# Test data
test_data = {
    "agenda": "Project discussion and planning",
    "email": "test@example.com",
    "time": "2023-12-15 14:30",  # Format: YYYY-MM-DD HH:MM
    "timezone": "America/New_York",  # Valid timezone identifier
    "short_bio": "Experienced software developer specializing in AI and machine learning"
}

def test_webhook():
    try:
        # Send POST request to the webhook
        response = requests.post(
            WEBHOOK_URL,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding response: {e}")

if __name__ == "__main__":
    print("Sending test request to webhook...")
    test_webhook() 