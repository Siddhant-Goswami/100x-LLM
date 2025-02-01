# # Function Calling with OpenAI APIs

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


# 1. Define Function to fetch context

# Get the current weather
def get_current_weather(location):
    """Get the current weather in a given location using OpenWeatherMap API"""
    # OpenWeatherMap API configuration
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    try:
        # Use the Current Weather API endpoint instead of OneCall
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}"
        
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Extract relevant weather information
        weather = {
            "location": location,
            "temperature": weather_data['main']['temp'],
            "feels_like": weather_data['main']['feels_like'],
            "humidity": weather_data['main']['humidity'],
            "pressure": weather_data['main']['pressure'],
            "wind_speed": weather_data['wind']['speed'],
            "description": weather_data['weather'][0]['description'],
            "icon": weather_data['weather'][0]['icon']
        }
        
        return json.dumps(weather)
        
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"API Error: {str(e)}"})


# ### Define Functions
# 
# As demonstrated in the OpenAI documentation, here is a simple example of how to define the functions that are going to be part of the request. 
# 
# The descriptions are important because these are passed directly to the LLM and the LLM will use the description to determine whether to use the functions or how to use/call.



# Define a function for LLM to use as a tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },   
    }
]



response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "role": "user",
            "content": "What is the weather like in wakanda?",
        }
    ],
    temperature=0,
    max_tokens=300,
    tools=tools,
    tool_choice="auto"
)

# print(response.choices[0].message.content)



groq_response = response.choices[0].message
print(groq_response)


# response.tool_calls[0].function.arguments

# We can now capture the arguments:


args = json.loads(groq_response.tool_calls[0].function.arguments)
print(args)

print("output")
print(get_current_weather(**args))

#  Put this into another LLM call and return the response in text format