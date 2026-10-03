import streamlit as st
from google import genai
from google.genai import types
import smtplib
from email.mime.text import MIMEText

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

MODEL_NAME = "gemini-3.5-flash-lite"

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📸",
    layout="centered",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def send_email(to_address, subject, body):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], use_container_width=True)


def add_message(role, kind, content):
    st.session_state.messages.append(
        {"role": role, "kind": kind, "content": content}
    )
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


# Step 1: onboarding
if "onboarded" not in st.session_state:
    st.title("📸 Snap & Study")
    st.caption("Snap a problem. Understand it. Save the explanation.")

    st.info(
        "Upload a problem, diagram, page of notes, or study material. "
        "Gemini will explain it in simple language and you can email the explanation to yourself."
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your name", placeholder="Enter your name")
        email = st.text_input(
            "Email address for saved explanations",
            placeholder="you@example.com",
        )
        submitted = st.form_submit_button("Start Learning 🚀", use_container_width=True)

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please fill in both your name and email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# Step 2: header and save action
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📸 Snap & Study")
    st.caption(f"Learning with {st.session_state.name}")

with button_col:
    st.markdown("### 📧 Email Summary")

    recipient_email = st.text_input(
        "Enter your email",
        value=st.session_state.email,
        placeholder="you@example.com",
        label_visibility="collapsed",
    )

    send_disabled = (
        len(st.session_state.messages) <= 1
        or not recipient_email.strip()
    )

    if st.button(
        "📧 Send Summary",
        disabled=send_disabled,
        use_container_width=True,
    ):
        with st.spinner("Preparing your study summary..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        try:
            send_email(
                recipient_email.strip(),
                "Snap & Study - Your Study Summary",
                summary,
            )
            st.success("Summary emailed successfully! 📬")
        except Exception as error:
            st.error(f"Couldn't send the email: {error}")
            
# Step 3: conversation history
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

# Step 4: vision + chat input
user_input = st.chat_input(
    "Ask a question or attach a study image...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = (user_input.text or "").strip()

    # Text-only follow-up question
    if photo is None and text:
        add_message("user", "text", text)

        with st.spinner("Thinking..."):
            answer = ask_gemini(text)

        add_message("assistant", "text", answer)

    # Image + optional question
    elif photo is not None:
        photo_bytes = photo.getvalue()

        add_message("user", "image", photo_bytes)

        parts = [
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        ]

        if text:
            parts.append(text)
        else:
            parts.append(
                "Explain this study material in simple language. "
                "Identify the key concept, explain it step by step, "
                "and give one simple example."
            )

        with st.spinner("Reading and explaining..."):
            answer = ask_gemini(parts)

        add_message("assistant", "text", answer)

    # Safety fallback
    else:
        st.warning("Please type a question or attach an image.")

