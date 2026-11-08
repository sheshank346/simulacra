import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
ai = Groq(api_key=os.getenv("GROQ_API_KEY"))

r = ai.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Say hello in one short sentence."}],
)
print(r.choices[0].message.content)