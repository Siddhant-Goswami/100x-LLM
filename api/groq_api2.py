import os
import requests

# Get the Groq API key from environment variables
groq_api_key = os.environ.get("GROQ_API_KEY")

# Define the URL for the Groq API endpoint
url = "https://api.groq.com/openai/v1/chat/completions"

# Set the headers for the API request
headers = {
    "Authorization": f"Bearer {groq_api_key}"
}

# Define the body for the API request
body = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {
            "role": "user",
            "content": "Tell me a very funny joke"
        }
    ]
}

# Send a POST request to the Groq API
response = requests.post(url, headers=headers, json=body)

# Check if the request was successful
if response.status_code == 200:
    # Print the full response from Groq
    print("Response from Groq:", response.json())
    print('\n')
    # Print the content of the first message choice
    print(response.json()['choices'][0]['message']['content'])
else:
    # Print the error message if the request failed
    print("Error:", response.status_code, response.text)