# Orthodontic Patient Chat Portal

A web-based messaging application for orthodontic patients to ask treatment questions, with persistent conversation history and a professor dashboard.

## Features

- **Patient login & registration** — secure JWT authentication
- **AI-powered chat** — uses Ollama (local LLM, free, no API key) with a smart rule-based fallback
- **Persistent memory** — all conversations stored in SQLite; full history sent to AI each message
- **Urgent message detection** — automatically flags pain/emergency keywords and provides clinic number
- **Professor dashboard** — view all patient threads, send direct replies
- **Mobile-responsive** chat UI

## Quick Start

```bash
chmod +x start.sh
./start.sh
```

Then open **http://localhost:3000**

## Optional: Enable Ollama AI (recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download Llama 3 (4GB, one-time)
ollama pull llama3
```

Without Ollama, the app uses a built-in rule-based engine covering common orthodontic topics.

## Accounts

| Role | Email | Password |
|------|-------|----------|
| Professor | professor@clinic.edu | professor123 |
| Patient | Register at /register | (you choose) |

## Architecture

```
React (port 3000)  →  FastAPI (port 8000)  →  SQLite DB
                                          →  Ollama (port 11434, optional)
```

## API Docs

Visit **http://localhost:8000/docs** for interactive API documentation.

## Project Structure

```
├── backend/
│   ├── main.py       # API routes
│   ├── models.py     # Database models
│   ├── auth.py       # JWT authentication
│   ├── ai.py         # Ollama + rule-based AI
│   └── database.py   # SQLite setup
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   ├── Chat.jsx       # Patient view
│       │   └── Dashboard.jsx  # Professor view
│       └── App.jsx
└── start.sh
```
