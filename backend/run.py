import sys
import time
sys.stdout.reconfigure(encoding="utf-8")
from angles import propose_angles
from competitors import find_competitors
from gaps import find_gaps
from novelty import check_novelty
from search import search

idea = " ".join(sys.argv[1:])
gaps, seen = [], set()

for name in find_competitors(idea):
    for page in search(f"{name} reviews complaints", n=3):
        for g in find_gaps(idea, page, name):
            if g["quote"] not in seen:
                seen.add(g["quote"])
                gaps.append({**g, "product": name})
        time.sleep(6)

for i, g in enumerate(gaps, 1):
    print(f"{i}. [{g['product']}] {g['gap']}\n   \"{g['quote']}\"")

for a in propose_angles(idea, gaps):
    print(f"\n{a['title']}: {a['idea']}")
    print("  fixes complaints:", ", ".join(str(i) for i in a["fixes"]))
    n = check_novelty(a, idea)
    if n["status"] == "none":
        print(f"  no existing product found in {n['searched']} pages")
    else:
        word = "already offered by" if n["status"] == "same" else "similar to"
        print(f"  {word} {n['product']}: \"{n['quote']}\"\n  {n['url']}")
        if n["difference"]:
            print(f"  difference: {n['difference']}")
    time.sleep(6)