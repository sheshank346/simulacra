import hashlib
import json
import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
CACHE = "data/search_cache"


def search(query, n=5):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.md5(f"{query}|{n}".encode()).hexdigest()
    path = f"{CACHE}/{key}.json"
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    res = client.search(query, max_results=n, include_raw_content=True)
    pages = []
    for r in res["results"]:
        text = r.get("raw_content") or r.get("content") or ""
        pages.append({"title": r["title"], "url": r["url"], "text": text})
    json.dump(pages, open(path, "w", encoding="utf-8"))
    return pages