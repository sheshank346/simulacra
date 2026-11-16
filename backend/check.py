import sys

sys.stdout.reconfigure(encoding="utf-8")
from novelty import check_novelty

idea = " ".join(sys.argv[1:])
r = check_novelty({"title": idea, "idea": idea}, idea)

labels = {
    "same": "EXISTS",
    "similar": "SIMILAR IDEA EXISTS",
    "none": "NO CLOSE MATCH FOUND",
}
print(labels[r["status"]])
if r["status"] == "none":
    print(f"Searched {r['searched']} pages. This does not prove the idea is new.")
else:
    print(f"{r['product']}: \"{r['quote']}\"")
    print(r["url"])
    if r["difference"]:
        print("How it differs:", r["difference"])