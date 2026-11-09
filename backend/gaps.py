import json
import os
from dotenv import load_dotenv
from groq import Groq
from verify import verify_quote

load_dotenv()
ai = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

PROMPT = """Idea: {idea}
Product: {product}

Below is text from a web page. List complaints or missing features that
users or reviewers state about {product} specifically.

Rules:
- The "gap" must only restate what the quote says. Do not add anything.
- The "quote" must be copied word for word from the text.
- The quote must be a full sentence or clause of at least 6 words, written by a user or reviewer.
- Skip troubleshooting tips, general advice, and remarks about the whole category.
- Skip anything about a different product or an old version.
- If there are none, return an empty list.

Reply as JSON: {{"gaps": [{{"gap": "...", "quote": "..."}}]}}

Text:
{text}"""


def find_gaps(idea, page, product):
    text = page["text"][:4000]
    msg = PROMPT.format(idea=idea, product=product, text=text)
    reply = ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": msg}],
        response_format={"type": "json_object"},
    )
    try:
        items = json.loads(reply.choices[0].message.content)["gaps"]
    except (ValueError, KeyError):
        return []
    items = [g for g in items if isinstance(g, dict)]
    return [
        {**g, "url": page["url"]}
        for g in items
        if verify_quote(str(g.get("quote") or ""), text)
    ]