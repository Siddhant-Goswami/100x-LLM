# # Function Calling with OpenAI APIs

import os
import openai
import json
import requests
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

# set openai api key
openai.api_key = os.environ['OPENAI_API_KEY']


# ### Define Dummy Function

# Defines a dummy function to get the current stock price
def get_current_stock_price(stock_symbol):
    """Get the current stock price for a given stock symbol"""

    stock_data = yf.Ticker(stock_symbol).history(period="1d")

    # Print the stock's current price
    print(f"Current Price of {stock_symbol}: ", stock_data['Close'].iloc[-1])
    return json.dumps(stock_data['Close'].iloc[-1])


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
            "name": "get_current_stock_price",
            "description": "Get the current stock price for a given stock symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_symbol": {
                        "type": "string",
                        "description": "The stock symbol you are interested in, e.g. RELIANCE",
                    },
                },
                "required": ["stock_symbol"],
            },
        },   
    }
]


response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {
        "role": "user",
        "content": "What is the price of Techm.ns?"
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
print(get_current_stock_price(**args))

#  Put this into another LLM call and return the response in text format