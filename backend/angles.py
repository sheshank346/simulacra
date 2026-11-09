import json
from gaps import ai, MODEL

PROMPT = """Idea: {idea}

Complaints about existing products, numbered:
{gaps}

Propose {n} ways to make the idea different from these products.
Each must fix at least one numbered complaint. Do not invent complaints.
Reply as JSON: {{"angles": [{{"title": "...", "idea": "...", "fixes": [1, 2]}}]}}"""


def propose_angles(idea, gaps, n=3):
    if not gaps:
        return []
    listing = "\n".join(f"{i}. {g['gap']} ({g['product']})" for i, g in enumerate(gaps, 1))
    reply = ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(idea=idea, gaps=listing, n=n)}],
        response_format={"type": "json_object"},
    )
    try:
        items = json.loads(reply.choices[0].message.content)["angles"]
    except (ValueError, KeyError):
        return []
    angles = []
    for a in items:
        if not isinstance(a, dict):
            continue
        raw = a.get("fixes")
        raw = raw if isinstance(raw, list) else []
        fixes = [i for i in raw if isinstance(i, int) and 1 <= i <= len(gaps)]
        if fixes and a.get("title") and a.get("idea"):
            angles.append({"title": a["title"], "idea": a["idea"], "fixes": fixes})
    return angles