from dataset import init_db,save_chat,get_history
import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from dataset import init_db, save_chat, get_history

# Load .env file
load_dotenv()

# Get API key securely
api_key = os.getenv("API_KEY")

# OpenAI Client
client = OpenAI(api_key="api_key")

# Initialize database
init_db()

uploaded_text = ""


# Extract text from PDF
def extract_pdf_text(pdf_file):
    global uploaded_text

    if pdf_file is None:
        return "Please upload a PDF file."

    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    uploaded_text = text

    return "PDF uploaded successfully!"


# Chatbot Function
def study_buddy(user_input, history):
    global uploaded_text

    prompt = f"""
    You are an intelligent Study Buddy Bot.

    Uploaded Notes:
    {uploaded_text}

    User Question:
    {user_input}

    Your tasks:
    - Explain topics simply
    - Generate quizzes
    - Create flashcards
    - Summarize notes
    - Answer from uploaded notes
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI study assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    bot_reply = response.choices[0].message.content

    # Save history to database
    save_chat(user_input, bot_reply)

    history.append((user_input, bot_reply))

    return history, history


# Load old chat history
def load_history():
    rows = get_history()
    return [(u, b) for u, b in rows]


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 📚 Study Buddy Bot")

    chatbot = gr.Chatbot(value=load_history(), height=500)

    state = gr.State(load_history())

    with gr.Row():
        file_upload = gr.File(label="Upload PDF Notes")
        upload_btn = gr.Button("Upload")

    upload_status = gr.Textbox(label="Upload Status")

    upload_btn.click(
        fn=extract_pdf_text,
        inputs=file_upload,
        outputs=upload_status
    )

    user_msg = gr.Textbox(
        label="Ask a question",
        placeholder="Generate quiz from chapter 2..."
    )

    send_btn = gr.Button("Send")

    send_btn.click(
        fn=study_buddy,
        inputs=[user_msg, state],
        outputs=[chatbot, state]
    )

demo.launch(share=True)
