import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from dataset import init_db, save_chat, get_history

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("API_KEY")

# OpenAI client
client = OpenAI(api_key=api_key)

# Initialize database
init_db()

# Store uploaded notes
uploaded_text = ""


# Extract PDF text
def extract_pdf_text(pdf_file):
    global uploaded_text

    if pdf_file is None:
        return "Please upload a PDF."

    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    uploaded_text = text

    return "✅ PDF uploaded successfully!"


# Chatbot function
def study_buddy(user_input, history):
    global uploaded_text

    if not user_input:
        return history, history

    prompt = f"""
    You are a smart Study Buddy AI.

    Uploaded Notes:
    {uploaded_text}

    Student Question:
    {user_input}

    Your tasks:
    - Explain concepts simply
    - Generate quizzes
    - Create flashcards
    - Summarize notes
    - Answer from uploaded notes
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful study assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        bot_reply = response.choices[0].message.content

    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # Save to DB
    save_chat(user_input, bot_reply)

    history.append((user_input, bot_reply))

    return history, history


# Load previous chats
def load_history():
    rows = get_history()
    return [(u, b) for u, b in rows]


# Gradio UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown(
        """
        # 📚 Study Buddy Bot
        Upload notes and ask questions from your PDF.
        """
    )

    chatbot = gr.Chatbot(
        value=load_history(),
        height=500
    )

    state = gr.State(load_history())

    with gr.Row():
        file_upload = gr.File(label="📄 Upload PDF")
        upload_btn = gr.Button("Upload")

    upload_status = gr.Textbox(label="Status")

    upload_btn.click(
        fn=extract_pdf_text,
        inputs=file_upload,
        outputs=upload_status
    )

    user_msg = gr.Textbox(
        label="Ask Question",
        placeholder="Generate quiz from chapter 2..."
    )

    send_btn = gr.Button("Send")

    send_btn.click(
        fn=study_buddy,
        inputs=[user_msg, state],
        outputs=[chatbot, state]
    )

# Run app
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True
)
