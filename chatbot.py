import os
import json
from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = """You are a helpful, friendly AI assistant. You are conversational, concise, and direct.
You remember the context of the current conversation and refer back to it when relevant."""

def load_history(path="history.json"):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def save_history(history, path="history.json"):
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

def chat(history, user_input):
    history.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history
    )
    assistant_msg = response.content[0].text
    history.append({"role": "assistant", "content": assistant_msg})
    return assistant_msg, history

def run():
    print("\n🤖  AI Friday Chatbot")
    print("─" * 40)
    print("Type 'quit' to exit | 'clear' to reset | 'save' to save history\n")

    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "clear":
            history = []
            print("✓ Conversation cleared.\n")
            continue
        if user_input.lower() == "save":
            save_history(history)
            print("✓ History saved to history.json\n")
            continue

        response, history = chat(history, user_input)
        print(f"\nAI: {response}\n")

if __name__ == "__main__":
    run()
