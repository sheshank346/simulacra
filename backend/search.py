import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search(query, n=5):
    res = client.search(query, max_results=n, include_raw_content=True)
    pages = []
    for r in res["results"]:
        text = r.get("raw_content") or r.get("content") or ""
        pages.append({"title": r["title"], "url": r["url"], "text": text})
    return pages