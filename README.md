# 📸 Snap & Study — AI Vision Chatbot

Snap & Study is an AI Vision study assistant built with Streamlit and Gemini.

## What it does

- Accepts study images such as questions, diagrams, textbook pages, notes, and screenshots.
- Uses Gemini Vision to understand the image.
- Explains the content in simple student-friendly language.
- Supports follow-up chat about the same image/conversation.
- Creates a revision summary of the conversation.
- Emails the summary to the student's Gmail address.

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- Gmail SMTP

## Project Structure

```text
snap-study/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

## Run locally

1. Install Python 3.9+.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
5. Add your Gemini API key.
6. Add your Gmail address and Gmail App Password.
7. Run:

```bash
streamlit run app.py
```

## Gmail setup

Enable 2-Step Verification on the Gmail account used for sending.
Create a Gmail App Password and put that App Password in
`.streamlit/secrets.toml`.

Never commit the real `secrets.toml` file to GitHub.

## Deployment

Deploy the repository using Streamlit Community Cloud.
In the deployed app's Secrets settings, add the same three secret values
from your local `secrets.toml`.

## Core Flow

Image/Text Input → Gemini Vision + Chat → Explanation → Study Summary → Email
