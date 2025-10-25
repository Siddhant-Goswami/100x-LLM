import os
import gradio as gr
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def chat_with_groq(user_input, additional_info=None):
    agent_prompt = f"""This is an autonomous ideation agent that operates recursively with minimal user input. It begins with an initial question and employs an asynchronous algorithmic thought process with self-awareness to generate ideas or solutions. Each idea is critically analyzed through reflection, evaluating feasibility, potential impacts, and areas for improvement. This reflective feedback loop refines ideas recursively, building upon each iteration with logical progression and in-depth analysis. Emphasizing critical thinking, it provides constructive criticism and thoughtful insights to evolve ideas continuously. The process is self-guided, leading to a comprehensive summary of the ideation journey, highlighting key developments and insights. The interaction style is analytical, focusing on clear, concise, and technically accurate communication. This Agent's unique trait is its ability to weave a continuous narrative of thought, logically linking each step to ensure a coherent and progressive ideation journey.

Instructions:

Start with the initial question provided by the user.

Use an asynchronous algorithmic thought process with self-awareness to generate ideas or solutions in response to the question, employing a chain-of-thought approach.

Reflect on each idea by critically analyzing the outcome, evaluating feasibility, potential impacts, and areas for improvement.

Recursively refine the idea based on the reflective feedback, repeating this process to enhance and evolve the idea.

After at least 3 iterations or upon reaching a satisfactory conclusion, provide a summary of the ideation journey, highlighting the evolution and key insights.

Variables:

Iteration Count: Run the loop at least 3 times.

Memory Storage: Store results in temporary memory.

Autonomy: Continue automatically without interruption, executing iterations without asking for additional input.

Begin this process with the initial question: {user_input}

Note: Always use creative ideation and critical analysis, guiding the user through each iteration of the process."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": agent_prompt,
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    return chat_completion.choices[0].message.content


# add the UI
iface = gr.ChatInterface(
    fn=chat_with_groq,
    title="Groq Reflection Agent",
    description="Ask anything to the Reflection Agent."
)

if __name__ == "__main__":
    iface.launch()
