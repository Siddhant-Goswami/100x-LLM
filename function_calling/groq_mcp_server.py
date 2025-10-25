"""MCP Server for Groq Weather Function Calling using FastMCP"""

import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

from groq import Groq

# Initialize FastMCP server
mcp = FastMCP("groq-weather-server")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# 1. Define Function to fetch context

# Get the current weather
def get_current_weather(location: str) -> str:
    """Get the current weather in a given location"""
    weather = {
        "location": location,
        "temperature": "50",
    }
    return json.dumps(weather)


@mcp.tool()
def get_weather_with_groq(query: str) -> str:
    """
    Get weather information using Groq's LLM with function calling.

    Args:
        query: Natural language query about weather (e.g., "What is the weather like in Bengaluru?")

    Returns:
        Weather information as a string
    """
    # Define the tool for LLM
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

    # First API call to LLM
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        temperature=0,
        max_tokens=300,
        tools=tools,
        tool_choice="auto"
    )

    groq_response = response.choices[0].message

    # Check if tool was called
    if groq_response.tool_calls:
        # Extract arguments and call the function
        args = json.loads(groq_response.tool_calls[0].function.arguments)
        weather_data = get_current_weather(**args)

        # Second API call with function result
        second_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": query,
                },
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": groq_response.tool_calls
                },
                {
                    "role": "tool",
                    "content": weather_data,
                    "tool_call_id": groq_response.tool_calls[0].id
                }
            ],
            temperature=0,
            max_tokens=300,
        )

        return second_response.choices[0].message.content
    else:
        # No tool call, return direct response
        return groq_response.content


@mcp.tool()
def get_weather_direct(location: str) -> str:
    """
    Get weather information directly for a specific location.

    Args:
        location: The city and state, e.g. San Francisco, CA

    Returns:
        Weather information as JSON string
    """
    return get_current_weather(location)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
