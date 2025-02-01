import os
import gradio as gr
from groq import Groq

def get_groq_response(prompt):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a witty and humorous AI assistant. Feel free to use puns, jokes, and playful language in your responses while still being helpful.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

def chat_with_groq(message):
    try:
        response = get_groq_response(message)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
demo = gr.Interface(
    fn=chat_with_groq,
    inputs=gr.Textbox(lines=4, placeholder="Enter your message here..."),
    outputs=gr.Textbox(label="Groq Response"),
    title="Groq Chat Interface",
    description="Chat with Groq's LLama3 model",
)

if __name__ == "__main__":
    demo.launch()