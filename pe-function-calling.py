#!/usr/bin/env python
# coding: utf-8

# # Function Calling with OpenAI APIs

# In[1]:


import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()

# set openai api key
openai.api_key = os.environ['OPENAI_API_KEY']


# ### Define a Get Completion Function

# In[2]:


def get_completion(messages, model="gpt-3.5-turbo-1106", temperature=0, max_tokens=300, tools=None, tool_choice=None):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        tools=tools,
        tool_choice=tool_choice
    )
    return response.choices[0].message


# ### Define Dummy Function

# In[3]:


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

# In[4]:


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


# In[5]:


# define a list of messages

messages = [
    {
        "role": "user",
        "content": "What is the weather like in London?"
    }
]


# In[6]:


response = get_completion(messages, tools=tools)
print(response)


# response.tool_calls[0].function.arguments

# We can now capture the arguments:

# In[7]:


args = json.loads(response.tool_calls[0].function.arguments)


# In[8]:


get_current_weather(**args)


# ### Controlling Function Calling Behavior

# Let's say we were interested in designing this `function_calling` functionality in the context of an LLM-powered conversational agent. Your solution should then know what function to call or if it needs to be called at all. Let's try a simple example of a greeting message:

# In[9]:


messages = [
    {
        "role": "user",
        "content": "Hello! How are you?",
    }
]


# In[10]:


get_completion(messages, tools=tools)


# You can specify the behavior you want from function calling, which is desired to control the behavior of your system. By default, the model decide on its own whether to call a function and which function to call. This is achieved by setting `tool_choice: "auto"` which is the default setting.  

# In[11]:


get_completion(messages, tools=tools, tool_choice="auto")


# Setting `tool_choice: "none"` forces the model to not use any of the functions provided. 

# In[12]:


get_completion(messages, tools=tools, tool_choice="none")


# In[13]:


messages = [
    {
        "role": "user",
        "content": "What's the weather like in London?",
    }
]
get_completion(messages, tools=tools, tool_choice="none")


# You can also force the model to choose a function if that's the behavior you want in your application. Example:

# In[14]:


messages = [
    {
        "role": "user",
        "content": "What's the weather like in London?",
    }
]
get_completion(messages, tools=tools, tool_choice={"type": "function", "function": {"name": "get_current_weather"}})


# The OpenAI APIs also support parallel function calling that can call multiple functions in one turn. 

# In[15]:


messages = [
    {
        "role": "user",
        "content": "What's the weather like in London and Belmopan in the coming days?",
    }
]
get_completion(messages, tools=tools)


# You can see in the response above that the response contains information from the function calls for the two locations queried. 

# ### Function Calling Response for Model Feedback
# 
# You might also be interested in developing an agent that passes back the result obtained after calling your APIs with the inputs generated from function calling. Let's look at an example next:
# 

# In[16]:


messages = []
messages.append({"role": "user", "content": "What's the weather like in Boston!"})
assistant_message = get_completion(messages, tools=tools, tool_choice="auto")
assistant_message = json.loads(assistant_message.model_dump_json())
assistant_message["content"] = str(assistant_message["tool_calls"][0]["function"])

#a temporary patch but this should be handled differently
# remove "function_call" from assistant message
del assistant_message["function_call"]


# In[17]:


messages.append(assistant_message)


# We then append the results of the  `get_current_weather` function and pass it back to the model using a `tool` role.

# In[18]:


# get the weather information to pass back to the model
weather = get_current_weather(messages[1]["tool_calls"][0]["function"]["arguments"])

messages.append({"role": "tool",
                 "tool_call_id": assistant_message["tool_calls"][0]["id"],
                 "name": assistant_message["tool_calls"][0]["function"]["name"],
                 "content": weather})


# In[19]:


final_response = get_completion(messages, tools=tools)


# In[20]:


final_response

