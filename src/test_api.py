from dotenv import load_dotenv
import anthropic

load_dotenv()  # reads .env and loads the key
client = anthropic.Anthropic()  # finds the key automatically

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello in one short sentence."}],
)
print(response.content[0].text)