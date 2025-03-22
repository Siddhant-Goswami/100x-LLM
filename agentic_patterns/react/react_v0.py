def react_agent(question, max_iterations=3):
    """
    A minimal ReAct agent that follows the Think-Act-Observe loop.
    
    :param question: Question to be answered
    :param max_iterations: Maximum number of iterations
    :return: The final answer
    """
    context = ""
    
    for i in range(max_iterations):
        print(f"Iteration {i+1}:")
        
        # Think: Determine what to do next
        thought = f"I need to find information about {question}"
        print(f"Thought: {thought}")
        
        # Act: Choose an action (simplified - always search in this version)
        action = "search"
        action_input = question
        print(f"Action: {action}")
        print(f"Action Input: {action_input}")
        
        # Observe: Get results from the action
        observation = "This is a placeholder for search results."
        print(f"Observation: {observation}")
        print("---")
        
        # Update context with new information
        context += f"\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"
    
    # In this simple version, just return a placeholder answer
    return f"Based on my research, the answer to '{question}' is [placeholder]"

# Demo
question = "What is the population of India?"
answer = react_agent(question)
print(f"Final Answer: {answer}")
