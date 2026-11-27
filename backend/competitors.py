import json
from gaps import ai, MODEL
from search import search
from verify import contains

PROMPT = """Idea: {idea}

Search results:
{results}

List up to {n} real products that already do what this idea does.
Choose products whose main purpose is this idea. Skip companies from other industries, such as airlines or travel portals.
Use product names exactly as they appear in the results.
Reply as JSON: {{"products": ["...", "..."]}}"""


def find_competitors(idea, n=3):
    pages = search(idea, n=6) + search(f"best apps for {idea}", n=6)
    results = "\n".join(f"{p['title']}: {p['text'][:800]}" for p in pages)
    reply = ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(idea=idea, results=results, n=n)}],
        response_format={"type": "json_object"},
    )
    try:
        names = json.loads(reply.choices[0].message.content)["products"]
    except (ValueError, KeyError):
        return []
    return [x for x in names if isinstance(x, str) and contains(x, results)][:n]