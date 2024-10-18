import os
import json
from groq import Groq

def react_agent(question, max_iterations=5):
    """
    Main function that implements the React Agent loop.
    It iterates through thinking, acting, and observing until it reaches a final answer or max iterations.
    
    :param question: The input question to be answered
    :param max_iterations: Maximum number of iterations to prevent infinite loops
    :return: The final answer or a message indicating no answer was found
    """
    context = ""
    for i in range(max_iterations):
        # Generate a thought and decide on an action
        thought, action, action_input = generate_thought_and_action(question, context)
        
        # Print the current iteration's details
        print(f"Iteration {i+1}:")
        print(f"Thought: {thought}")
        print(f"Action: {action}")
        print(f"Action Input: {action_input}")

        # Perform the chosen action and get the observation
        observation = perform_action(action, action_input)
        print(f"Observation: {observation}")
        print("---")

        # Update the context with the current iteration's information
        context = context + f"\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"

        # If a final answer is reached, return it
        if action == "Final Answer":
            return action_input

    # If no final answer is found within max_iterations, return this message
    return "I couldn't find a definitive answer within the given number of iterations."



def generate_thought_and_action(question, context):
    """
    Generates a thought and decides on an action using the Groq API.
    
    :param question: The input question
    :param context: The current context of the conversation
    :return: thought, action, action_input
    """
    # Construct the prompt for the AI model
    prompt = f"""
    
    Question: {question}
    Context: {context}

    Think about the question and decide on an action. You must either use the search tool or give a Final Answer.

    To use the search tool, format your response like this:
    Thought: [Your reasoning here]
    Action: search
    Action Input: [Your search query]

    To give a final answer, format your response like this:
    Thought: [Your reasoning here]
    Final Answer: [Your final answer here]

    Remember, you must either use the search tool or provide a Final Answer."""

    # Define the available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    # Make an API call to Groq to generate the next thought and action
    # Initialize the Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-groq-70b-8192-tool-use-preview",
        max_tokens=150,
        tools=tools,
        tool_choice="auto"
    )

    # Extract the generated message
    message = response.choices[0].message
    content = message.content.strip() if message.content else ""

    # Parse the response to extract thought, action, and action input
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        action = tool_call.function.name
        action_input = json.loads(tool_call.function.arguments)["query"]
        thought = content if content else "Using search tool to find information."
        return thought, action, action_input
    elif "Final Answer:" in content:
        thought, final_answer = content.split("Final Answer:", 1)
        return thought.strip(), "Final Answer", final_answer.strip()
    else:
        # Fallback: treat the entire content as a thought and continue with a search
        return content, "search", f"Information about {question}"

def perform_action(action, action_input):
    """
    Executes the chosen action (either search or final answer).
    
    :param action: The action to perform ('search' or 'Final Answer')
    :param action_input: The input for the action (search query or final answer)
    :return: The result of the action (search results or the final answer)
    """
    if action == "search":
        return web_search(action_input)
    elif action == "Final Answer":
        return action_input
    else:
        return f"Invalid action: {action}. Performing a search instead."

def web_search(action_input):
    # do the web search using serp api with given action_input
    return "Search results"

question = "What is the population of India?"
answer = react_agent(question)
print(f"Final Answer: {answer}")
