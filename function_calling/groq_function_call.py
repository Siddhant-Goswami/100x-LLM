# # Function Calling with OpenAI APIs

import os
import json
from dotenv import load_dotenv

load_dotenv()

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


# 2. Define Function to fetch context

# Get the current weather
def get_current_weather(location):
    """Get the current weather in a given location"""
    weather = {
        "location": location,
        "temperature": "50",
    }


    return json.dumps(weather)


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


#LLM
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "What is the weather like in Bengaluru?",
        }
    ],
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