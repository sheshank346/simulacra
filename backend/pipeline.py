import html
import json
import time

import reviews
from angles import propose_angles
from competitors import find_competitors
from dedupe import merge_duplicates
from novelty import check_novelty
from reactions import react
from reviews import find_gaps_deep
from search import search

PER_PRODUCT = 5


class PipelineError(Exception):
    pass


def run(idea, progress=print):
    idea = idea.strip()
    if len(idea.split()) < 3:
        raise PipelineError("Please describe the idea in at least 3 words.")

    progress("Checking whether the idea already exists")
    verdict = check_novelty({"title": idea, "idea": idea}, idea)

    progress("Finding competitors")
    gaps, seen = [], set()
    names = find_competitors(idea)
    best = verdict.get("product")
    if best and not any(best.lower() in n.lower() or n.lower() in best.lower() for n in names):
        names.insert(0, best)
    for name in names[:3]:
        progress(f"Reading reviews of {name}")
        for page in search(f"{name} reviews complaints", n=3):
            for g in find_gaps_deep(idea, page, name):
                if g["quote"] not in seen:
                    seen.add(g["quote"])
                    gaps.append({**g, "product": name})
            time.sleep(6)

    kept, count = [], {}
    for g in gaps:
        g["url"] = g["url"].replace("&amp%3B", "&").replace("&amp;", "&")
        if count.get(g["product"], 0) < PER_PRODUCT:
            count[g["product"]] = count.get(g["product"], 0) + 1
            kept.append(g)
    progress("Merging duplicate complaints")
    gaps = merge_duplicates(kept)

    progress("Proposing an angle")
    angles = propose_angles(idea, gaps)
    if not angles:
        return {"idea": idea, "verdict": verdict, "gaps": gaps, "angle": None,
                "people": [], "olostep_credits": reviews.credits}
    angle = max(angles, key=lambda x: len(x["fixes"]))

    progress("Simulating how people might react")
    people = react(idea, gaps, angle)
    if not people:
        raise PipelineError("No people were generated. Try again.")

    return {
        "idea": idea,
        "verdict": verdict,
        "gaps": gaps,
        "angle": angle,
        "people": people,
        "olostep_credits": reviews.credits,
    }


def build_page(result):
    template = open("backend/map_template.html", encoding="utf-8").read()
    people = json.dumps(result["people"]).replace("</", "<\\/")
    gaps = json.dumps(
        [{"gap": g["gap"], "product": g["product"]} for g in result["gaps"]]
    ).replace("</", "<\\/")
    title = html.escape(result["angle"]["title"])
    return template.replace("__GAPS__", gaps).replace("__PEOPLE__", people).replace("__TITLE__", title)