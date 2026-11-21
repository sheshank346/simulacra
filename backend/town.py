import html
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
from angles import propose_angles
from competitors import find_competitors
from dedupe import merge_duplicates
from gaps import find_gaps
from novelty import check_novelty
from reactions import react
from search import search

idea = " ".join(sys.argv[1:])
if len(idea.split()) < 3:
    sys.exit("Please describe the idea in at least 3 words.")

verdict = check_novelty({"title": idea, "idea": idea}, idea)
labels = {"same": "EXISTS", "similar": "SIMILAR IDEA EXISTS", "none": "NO CLOSE MATCH FOUND"}
print(labels[verdict["status"]])
if verdict["status"] != "none":
    print(f"{verdict['product']}: \"{verdict['quote']}\"\n{verdict['url']}")

gaps, seen = [], set()
for name in find_competitors(idea):
    for page in search(f"{name} reviews complaints", n=3):
        for g in find_gaps(idea, page, name):
            if g["quote"] not in seen:
                seen.add(g["quote"])
                gaps.append({**g, "product": name})
        time.sleep(6)
gaps = merge_duplicates(gaps)
print(f"{len(gaps)} verified complaints")

angles = propose_angles(idea, gaps)
if not angles:
    sys.exit("No angle could be proposed from the complaints found.")
angle = angles[0]
print("Angle:", angle["title"], "- fixes complaints", angle["fixes"])

people = react(idea, gaps, angle)
if not people:
    sys.exit("No people were generated. Try again.")

os.makedirs("data", exist_ok=True)
run = {"idea": idea, "verdict": verdict, "gaps": gaps, "angle": angle, "people": people}
json.dump(run, open("data/last_run.json", "w", encoding="utf-8"), indent=2)

template = open("backend/map_template.html", encoding="utf-8").read()
data = json.dumps(people).replace("</", "<\\/")
page = template.replace("__PEOPLE__", data).replace("__TITLE__", html.escape(angle["title"]))
open("data/map.html", "w", encoding="utf-8").write(page)
print(f"{len(people)} people written to data/map.html")
os.startfile(os.path.join("data", "map.html"))