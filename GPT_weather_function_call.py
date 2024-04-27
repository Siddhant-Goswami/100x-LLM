# # Function Calling with OpenAI APIs

import os
import openai
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# set openai api key
openai.api_key = os.environ['OPENAI_API_KEY']
OPENWEATHER_API_KEY = os.environ['OPENWEATHER_API_KEY']


# ### Define Dummy Function

# Defines a dummy function to get the current weather
def get_current_weather(location):
    """Get the current weather in a given location"""

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={OPENWEATHER_API_KEY}&q={location}"

    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['main']
        temperature = data['main']['temp'] - 273.15  # Convert Kelvin to Celsius
        return json.dumps({
            "city": location,
            "weather": weather,
            "temperature": round(temperature, 2)
        })
    else:
        return json.dumps({"city": location, "weather": "Data Fetch Error", "temperature": "N/A"})



# ### Define Functions
# 
# As demonstrated in the OpenAI documentation, here is a simple example of how to define the functions that are going to be part of the request. 
# 
# The descriptions are important because these are passed directly to the LLM and the LLM will use the description to determine whether to use the functions or how to use/call.



# define a function as tools
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
                    },
                },
                "required": ["location"],
            },
        },   
    }
]


response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {
        "role": "user",
        "content": "What is the weather like in Bengaluru?"
    }],
    temperature=0,
    max_tokens=300,
    tools=tools,
    tool_choice="auto"
)

openai_response = response.choices[0].message


# response.tool_calls[0].function.arguments

# We can now capture the arguments:


args = json.loads(openai_response.tool_calls[0].function.arguments)
print(args)

print("output")
print(get_current_weather(**args))

# Task: Put this into another LLM call and return the response in text format