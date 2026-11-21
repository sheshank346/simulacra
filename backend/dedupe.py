from novelty import ask

PROMPT = """Numbered complaints about existing products:
{gaps}

Which numbered complaints describe the same problem?
Reply as JSON: {{"groups": [[2, 3]]}} listing only groups of two or more.
If there are none, reply {{"groups": []}}"""


def merge_duplicates(gaps):
    if len(gaps) < 2:
        return gaps
    listing = "\n".join(f"{i}. [{g['product']}] {g['gap']}" for i, g in enumerate(gaps, 1))
    out = ask(PROMPT.format(gaps=listing))
    groups = out.get("groups") if isinstance(out, dict) else None
    drop = set()
    for group in groups if isinstance(groups, list) else []:
        if not isinstance(group, list):
            continue
        ids = sorted({i for i in group if isinstance(i, int) and 1 <= i <= len(gaps)})
        drop.update(ids[1:])
    return [g for i, g in enumerate(gaps, 1) if i not in drop]