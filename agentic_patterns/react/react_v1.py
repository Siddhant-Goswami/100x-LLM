def research_agent(topic, max_iterations=5):
    """
    Research agent that follows Think-Act-Observe loop for applied AI research.
    
    :param topic: The research topic to investigate
    :param max_iterations: Maximum number of iterations to prevent infinite loops
    :return: The final research report or a message indicating incomplete research
    """
    memory = ""
    
    for i in range(max_iterations):
        # Generate a thought and decide on an action
        thought, action, action_input = generate_thought_and_action(topic, memory)
        
        # Print the current iteration's details
        print(f"Iteration {i+1}:")
        print(f"Thought: {thought}")
        print(f"Action: {action}")
        print(f"Action Input: {action_input}")

        # Perform the chosen action and get the observation
        observation = perform_action(action, action_input)
        print(f"Observation: {observation}")
        print("---")

        # Update the memory with the current iteration's information
        memory += f"\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"

        # If a final report is reached, return it
        if action == "generate_research_report":
            return action_input

    # If no final report is found within max_iterations, return this message
    return "Research could not be completed within the given number of iterations."

def generate_thought_and_action(topic, memory):
    """
    Decision making for research actions based on current knowledge.
    
    :param topic: The research topic
    :param memory: The accumulated research memory
    :return: thought, action, action_input tuple
    """
    # Core research actions
    actions = [
        "search_academic_papers",
        "summarize_paper",
        "generate_research_report"
    ]
    
    # Simple logic: Progress through research phases
    if not memory:
        thought = f"Starting research on {topic}. Need to search for academic papers."
        action = "search_academic_papers"
        action_input = f"Find recent academic papers about {topic}"
    elif "search_academic_papers" in memory and "summarize_paper" not in memory:
        thought = "Found relevant papers. Now summarizing key papers."
        action = "summarize_paper"
        action_input = "Summarize the most relevant papers found"
    elif "summarize_paper" in memory and "generate_research_report" not in memory:
        thought = "Papers summarized. Generating final research report."
        action = "generate_research_report"
        action_input = "Generate comprehensive research report based on paper summaries"
    else:
        thought = "Research complete. Generating final report."
        action = "generate_research_report"
        action_input = "Generate comprehensive research report"
    
    return thought, action, action_input

def perform_action(action, action_input):
    """
    Execute research actions and return observations.
    
    :param action: The research action to perform
    :param action_input: The input for the action
    :return: The result of the action
    """
    if action == "search_academic_papers":
        return f"Found relevant academic papers about '{action_input}': [Paper citations]"
    elif action == "summarize_paper":
        return f"Summarized key papers: [Paper summaries]"
    elif action == "generate_research_report":
        return f"Generated comprehensive report for '{action_input}'"
    else:
        return f"Invalid action: {action}"

# Demo
topic = "Model Context Protocol"
report = research_agent(topic)
print(f"Final Report: {report}")
