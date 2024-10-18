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
    thought = ""
    action = ""
    action_input = ""
    # write a logic to get thought action and action input from LLM 
    return thought, action, action_input

def perform_action(action, action_input):
    observation = ""
     # write a logic to perform action and get the observation
    return observation


question = "What is the population of India?"
answer = react_agent(question)
print(f"Final Answer: {answer}")
