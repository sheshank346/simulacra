import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pipeline import PipelineError, build_page, run

LABELS = {"same": "EXISTS", "similar": "SIMILAR IDEA EXISTS", "none": "NO CLOSE MATCH FOUND"}

try:
    result = run(" ".join(sys.argv[1:]))
except PipelineError as e:
    sys.exit(str(e))

v = result["verdict"]
print(LABELS[v["status"]])
if v["status"] != "none":
    print(f"{v['product']}: \"{v['quote']}\"\n{v['url']}")
print(f"{len(result['gaps'])} verified complaints")
print("Olostep credits used:", result["olostep_credits"])
if result["angle"] is None:
    sys.exit("No angle could be proposed from the complaints found.")
print("Angle:", result["angle"]["title"], "- fixes complaints", result["angle"]["fixes"])

os.makedirs("data", exist_ok=True)
json.dump(result, open("data/last_run.json", "w", encoding="utf-8"), indent=2)
open("data/map.html", "w", encoding="utf-8").write(build_page(result))
print(f"{len(result['people'])} people written to data/map.html")
os.startfile(os.path.join("data", "map.html"))