# AI Friday Chatbot 🤖

Your personal AI chatbot powered by Claude. Two ways to run it:

---

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key at: https://console.anthropic.com

---

## Option 1 — Terminal chatbot

```bash
python chatbot.py
```

**Commands:**
- `clear` — reset the conversation
- `save`  — save chat history to history.json
- `quit`  — exit

---

## Option 2 — Web UI chatbot

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

Features:
- Clean dark UI
- Full conversation memory per session
- Clear chat button
- Keyboard shortcuts (Enter to send, Shift+Enter for newline)

---

## Customise your bot

Edit the `SYSTEM_PROMPT` in either file to give your AI a personality or specific role:

```python
SYSTEM_PROMPT = """You are a sarcastic movie critic who only recommends films from the 80s."""
```

---

## File structure

```
chatbot/
├── chatbot.py       # Terminal version
├── app.py           # Web UI version (Flask)
├── requirements.txt
└── README.md
```
