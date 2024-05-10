# # Function Calling with OpenAI APIs

import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()

# set openai api key
openai.api_key = os.environ['OPENAI_API_KEY']


# ### Define Dummy Function

# Defines a dummy function to get the current weather
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather = {
        "location": location,
        "temperature": "50",
        "unit": unit,
    }


    return json.dumps(weather)


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
                    "unit": {
                        "type": "string", 
                        "enum": ["celsius", "fahrenheit"]},
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
        "content": "What is the weather like in bengaluru?"
    }],
    temperature=0,
    max_tokens=300,
    tools=tools,
    tool_choice="auto"
)

openai_response = response.choices[0].message
print(openai_response)


# response.tool_calls[0].function.arguments

# We can now capture the arguments:


args = json.loads(openai_response.tool_calls[0].function.arguments)
print(args)

print("output")
print(get_current_weather(**args))