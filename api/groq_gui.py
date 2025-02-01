import gradio as gr
from groq_sdk2 import get_groq_response

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