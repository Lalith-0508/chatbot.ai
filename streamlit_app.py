"""
Web UI version of the AI Friday Chatbot.
Run: python app.py  →  open http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify, session
from anthropic import Anthropic
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
client = Anthropic()

SYSTEM_PROMPT = """You are a helpful, friendly AI assistant. You are conversational, concise, and direct.
You remember the context of the current conversation and refer back to it when relevant."""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Friday</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0d0d0f;
    --surface: #18181c;
    --border: #2a2a32;
    --accent: #7c6aff;
    --accent-dim: #3d3580;
    --text: #e8e6f0;
    --muted: #6b697a;
    --user-bg: #1f1e2e;
    --ai-bg: #18181c;
    --radius: 14px;
    --font-mono: 'DM Mono', monospace;
    --font-display: 'Syne', sans-serif;
  }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 14px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  header {
    width: 100%;
    max-width: 720px;
    padding: 24px 20px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--border);
  }
  .logo {
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 800;
    color: #fff;
  }
  h1 {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.02em;
  }
  .badge {
    margin-left: auto;
    font-size: 11px;
    color: var(--accent);
    border: 1px solid var(--accent-dim);
    border-radius: 20px;
    padding: 3px 10px;
    font-weight: 500;
    letter-spacing: 0.04em;
  }
  #chat {
    width: 100%;
    max-width: 720px;
    flex: 1;
    overflow-y: auto;
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
  }
  .msg {
    display: flex;
    flex-direction: column;
    max-width: 85%;
    gap: 4px;
    animation: pop 0.18s ease;
  }
  @keyframes pop {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .msg.user { align-self: flex-end; align-items: flex-end; }
  .msg.ai   { align-self: flex-start; align-items: flex-start; }
  .bubble {
    padding: 12px 16px;
    border-radius: var(--radius);
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .msg.user .bubble {
    background: var(--user-bg);
    border: 1px solid var(--accent-dim);
    color: var(--text);
    border-bottom-right-radius: 4px;
  }
  .msg.ai .bubble {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    color: var(--text);
    border-bottom-left-radius: 4px;
  }
  .label {
    font-size: 11px;
    color: var(--muted);
    padding: 0 4px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .typing .bubble { color: var(--muted); font-style: italic; }
  footer {
    width: 100%;
    max-width: 720px;
    padding: 16px 20px 24px;
    border-top: 1px solid var(--border);
  }
  .input-row {
    display: flex;
    gap: 10px;
    align-items: flex-end;
  }
  textarea {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 14px;
    padding: 12px 16px;
    resize: none;
    line-height: 1.6;
    min-height: 48px;
    max-height: 160px;
    outline: none;
    transition: border-color 0.15s;
  }
  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: var(--muted); }
  button {
    background: var(--accent);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 700;
    padding: 12px 20px;
    cursor: pointer;
    transition: opacity 0.15s, transform 0.1s;
    white-space: nowrap;
    height: 48px;
  }
  button:hover { opacity: 0.85; }
  button:active { transform: scale(0.97); }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  .clear-btn {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    font-size: 12px;
    padding: 6px 14px;
    height: auto;
    border-radius: 8px;
    margin-top: 10px;
    font-family: var(--font-mono);
    font-weight: 400;
  }
  .clear-btn:hover { border-color: var(--muted); color: var(--text); opacity: 1; }
  .hint { font-size: 11px; color: var(--muted); margin-top: 8px; }
  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 8px;
    color: var(--muted);
    font-size: 13px;
  }
  .empty-state .big { font-size: 32px; margin-bottom: 4px; }
</style>
</head>
<body>
<header>
  <div class="logo">A</div>
  <h1>AI Friday</h1>
  <span class="badge">ONLINE</span>
</header>

<div id="chat">
  <div class="empty-state" id="empty">
    <div class="big">🤖</div>
    <div>Start a conversation below</div>
  </div>
</div>

<footer>
  <div class="input-row">
    <textarea id="input" rows="1" placeholder="Message AI Friday..." autofocus></textarea>
    <button id="send-btn" onclick="sendMsg()">Send</button>
  </div>
  <div style="display:flex; align-items:center; justify-content:space-between;">
    <span class="hint">Enter to send · Shift+Enter for newline</span>
    <button class="clear-btn" onclick="clearChat()">Clear chat</button>
  </div>
</footer>

<script>
const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const emptyEl = document.getElementById('empty');

inputEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); }
});
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + 'px';
});

function addMsg(role, text) {
  emptyEl.style.display = 'none';
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.innerHTML = `<span class="label">${role === 'user' ? 'You' : 'AI Friday'}</span>
    <div class="bubble">${text.replace(/</g,'&lt;')}</div>`;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

async function sendMsg() {
  const text = inputEl.value.trim();
  if (!text) return;
  inputEl.value = '';
  inputEl.style.height = 'auto';
  sendBtn.disabled = true;
  addMsg('user', text);
  const typing = addMsg('ai', '...');
  typing.classList.add('typing');
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    chatEl.removeChild(typing);
    addMsg('ai', data.response);
  } catch {
    chatEl.removeChild(typing);
    addMsg('ai', '⚠️ Something went wrong. Try again.');
  }
  sendBtn.disabled = false;
  inputEl.focus();
}

async function clearChat() {
  await fetch('/clear', {method: 'POST'});
  chatEl.innerHTML = '';
  chatEl.appendChild(emptyEl);
  emptyEl.style.display = '';
}
</script>
</body>
</html>"""

@app.route("/")
def index():
    if "history" not in session:
        session["history"] = []
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "empty"}), 400

    history = session.get("history", [])
    history.append({"role": "user", "content": user_msg})

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    session["history"] = history
    return jsonify({"response": reply})

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("\n🤖  AI Friday Web Chatbot")
    print("─" * 40)
    print("Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
