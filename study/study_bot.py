import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# Load env variables
load_dotenv()

# OpenAI API key
api_key = os.getenv("API_KEY")

# OpenAI client
client = OpenAI(api_key=api_key)

# Streamlit page config
st.set_page_config(
    page_title="Study Buddy Bot",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Study Buddy Bot")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""


# Upload PDF
uploaded_file = st.file_uploader(
    "Upload PDF Notes",
    type=["pdf"]
)

# Extract PDF text
if uploaded_file is not None:

    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    st.session_state.uploaded_text = text

    st.success("✅ PDF uploaded successfully!")


# Display chat history
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
user_input = st.chat_input("Ask your question...")


if user_input:

    # Show user message
    st.chat_message("user").markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Prompt
    prompt = f"""
    You are a Study Buddy AI.

    Uploaded Notes:
    {st.session_state.uploaded_text}

    Student Question:
    {user_input}

    Tasks:
    - Explain concepts simply
    - Generate quizzes
    - Summarize notes
    - Create flashcards
    """

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI tutor."
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

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })
