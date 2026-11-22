import os
import time

from dotenv import load_dotenv

from gaps import find_gaps

load_dotenv()
STORES = ("apps.apple.com", "play.google.com")
CHUNK, MAX_CHUNKS = 4000, 3
credits = 0


def full_text(page):
    global credits
    key = os.getenv("OLOSTEP_API_KEY")
    if not key or not any(s in page["url"] for s in STORES):
        return page["text"]
    try:
        from olostep import Olostep

        res = Olostep(api_key=key).scrapes.create(url_to_scrape=page["url"], formats=["markdown"])
        credits += res.credits_consumed or 1
        return res.markdown_content or page["text"]
    except Exception:
        return page["text"]


def find_gaps_deep(idea, page, product):
    text = full_text(page)
    found = []
    for i in range(0, min(len(text), CHUNK * MAX_CHUNKS), CHUNK):
        found += find_gaps(idea, {"text": text[i:i + CHUNK], "url": page["url"]}, product)
        time.sleep(6)
    return found