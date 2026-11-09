import json
import os
import sys
import time

sys.path.insert(0, "backend")
sys.stdout.reconfigure(encoding="utf-8")
import novelty
from gaps import MODEL
from novelty import check_novelty

PATH = f"eval/progress-{MODEL.split('/')[-1]}.json"
ideas = json.load(open("eval/ideas.json", encoding="utf-8"))
done = json.load(open(PATH, encoding="utf-8")) if os.path.exists(PATH) else {}
print("model:", MODEL)

for item in ideas:
    text = item["idea"]
    if text in done:
        continue
    try:
        r = check_novelty({"title": text, "idea": text}, text)
    except Exception as e:
        print("error, stopping:", str(e)[:150])
        break
    done[text] = {"expected": item["expected"], **r}
    json.dump(done, open(PATH, "w", encoding="utf-8"), indent=2)
    print(r["status"], r.get("reason", ""), "-", text, f"[{novelty.tokens} tokens]")
    time.sleep(10)

rows = list(done.values())
print(f"checked {len(rows)} of {len(ideas)}")
print(f"found a match: {sum(r['status'] in ('same', 'similar') for r in rows)}")