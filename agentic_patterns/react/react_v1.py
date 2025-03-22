def react_agent(question, max_iterations=5):
    """
    ReAct agent that can decide between searching and answering.
    
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
        context += f"\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"

        # If a final answer is reached, return it
        if action == "Final Answer":
            return action_input

    # If no final answer is found within max_iterations, return this message
    return "I couldn't find a definitive answer within the given number of iterations."

def generate_thought_and_action(question, context):
    """
    Simplified decision making - alternates between search and final answer.
    
    :param question: The question being answered
    :param context: The accumulated context so far
    :return: thought, action, action_input tuple
    """
    # Simple logic: If we have some context, provide an answer; otherwise search
    if context:
        thought = "I now have enough information to answer the question."
        action = "Final Answer"
        action_input = f"The answer to '{question}' is based on the information I've gathered."
    else:
        thought = f"I need to search for information about {question}"
        action = "search"
        action_input = question
    
    return thought, action, action_input

def perform_action(action, action_input):
    """
    Simplified action execution with mock responses.
    
    :param action: The action to perform ('search' or 'Final Answer')
    :param action_input: The input for the action
    :return: The result of the action
    """
    if action == "search":
        # Mock search results
        return f"Found the following information about '{action_input}': [Example search results]"
    elif action == "Final Answer":
        return action_input
    else:
        return f"Invalid action: {action}"

# Demo
question = "What is the population of India?"
answer = react_agent(question)
print(f"Final Answer: {answer}")
