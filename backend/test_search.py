import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
tv = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

for r in tv.search("app to split expenses among friends", max_results=5)["results"]:
    print(r["title"], "-", r["url"])
