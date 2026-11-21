import re

from novelty import ask

STANCES = ("support", "oppose", "undecided")

PROMPT = """Idea: {idea}

Complaints found about existing products, numbered:
{gaps}

Proposal A: the idea as it is.
Proposal B: the idea changed like this: {title}. {angle}
Proposal B fixes only complaints: {fixes}

Invent {n} people in 3 groups of people who would really use this idea or be directly affected by it, with interests that conflict. Do not use investors, advisors or administrators as a group unless the idea is about them.
Do not use these names: {avoid}.
Each person reacts to both proposals and has one concrete constraint (budget, habit, trust, or time).
Base reasons on the numbered complaints and do not invent new complaints.
Write each reason as one plain first-person sentence in their own voice, without the words Proposal or complaint.
A person may change their view only because of a complaint that Proposal B fixes.
At least 4 people must still oppose or be undecided after Proposal B, for reasons it does not fix.

Reply as JSON: {{"people": [{{"name": "...", "group": "...", "profile": "...",
"before": "support", "before_reason": "...", "after": "support", "after_reason": "...", "cites": [1]}}]}}
Stances are support, oppose or undecided."""


def tidy(text):
    return re.sub(r"\s*\(\d+(?:,\s*\d+)*\)", "", str(text)).strip()


def _react_once(idea, gaps, angle, n=12, avoid="none"):
    listing = "\n".join(f"{i}. {g['gap']} ({g['product']})" for i, g in enumerate(gaps, 1))
    fixes = angle.get("fixes", [])
    out = ask(PROMPT.format(idea=idea, gaps=listing, title=angle["title"],
                            angle=angle["idea"], fixes=fixes, n=n, avoid=avoid))
    items = out.get("people") if isinstance(out, dict) else None
    people = []
    for p in items if isinstance(items, list) else []:
        if not isinstance(p, dict) or p.get("before") not in STANCES or p.get("after") not in STANCES:
            continue
        cites = p.get("cites") if isinstance(p.get("cites"), list) else []
        cites = [c for c in cites if isinstance(c, int) and 1 <= c <= len(gaps)]
        after = p["after"]
        if after != p["before"] and not set(cites) & set(fixes):
            after = p["before"]
        people.append({
            "name": str(p.get("name", "")),
            "group": str(p.get("group", "")),
            "profile": str(p.get("profile", "")),
            "before": p["before"],
            "before_reason": tidy(p.get("before_reason", "")),
            "after": after,
            "after_reason": tidy(p.get("after_reason", "")),
            "cites": cites,
        })
    return people

def react(idea, gaps, angle, n=12):
    people, names = [], set()
    for _ in range(3):
        avoid = ", ".join(sorted(names)) or "none"
        for p in _react_once(idea, gaps, angle, n - len(people), avoid):
            if p["name"] and p["name"] not in names:
                names.add(p["name"])
                people.append(p)
        if len(people) >= n:
            break
    print(f"kept {len(people)} of {n} people")
    return people[:n]
