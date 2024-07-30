import os
import gradio as gr
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def chat_with_groq(user_input, additional_info=None):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content


# add the UI
iface = gr.ChatInterface(
    fn=chat_with_groq,
    title="Groq Chatbot",
    description="Ask anything to the Groq-powered chatbot."
)

if __name__ == "__main__":
    iface.launch(share=True)