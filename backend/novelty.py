import json
import re
import time

import groq

from gaps import ai, MODEL
from search import search
from verify import verify_quote

QUERIES = """Product idea: {idea}
Feature: {feature}

Write 2 short web search queries (3 to 6 words each) to find existing products
that already offer this feature. Reply as JSON: {{"queries": ["...", "..."]}}"""

PROMPT = """Feature idea: {idea}

Below are numbered web pages. Does any page say a product offers this feature?
- "same": the product offers this feature as described.
- "similar": the product offers something related but different.
Give the product, a word-for-word quote from that page, and the page number.
The quote must be one unbroken passage copied from a single place on the page, with no ellipsis and no joined pieces.
For "similar", also say in one sentence how it differs.

Reply as JSON: {{"found": true, "match": "same", "product": "...", "quote": "...", "page": 1, "difference": ""}}
or {{"found": false}}

{pages}"""

SUPPORT = """Feature: {feature}

Quote from a web page about {product}:
"{quote}"

Does the quote itself say that {product} offers this feature?
- "yes": the quote clearly says it.
- "partly": the quote says something related, but not the whole feature.
- "no": the quote does not say it.
Reply as JSON: {{"answer": "yes"}}"""

tokens = 0


def ask(prompt):
    global tokens
    for wait in (15, 30, 60):
        try:
            reply = ai.chat.completions.create(
                model=MODEL,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            tokens += reply.usage.total_tokens
            return json.loads(reply.choices[0].message.content)
        except groq.RateLimitError:
            time.sleep(wait)
        except groq.BadRequestError:
            time.sleep(2)
    raise RuntimeError("model call failed after 3 tries")


def clean_quote(text):
    return re.sub(r"[*_#`]+", "", text).strip()


def supports(feature, product, quote):
    out = ask(SUPPORT.format(feature=feature, product=product, quote=quote))
    answer = str(out.get("answer", "")).lower() if isinstance(out, dict) else ""
    return answer if answer in ("yes", "partly", "no") else "partly"


def check_novelty(angle, idea):
    try:
        queries = ask(QUERIES.format(idea=idea, feature=angle["idea"])).get("queries")
    except (ValueError, AttributeError):
        queries = None
    if not isinstance(queries, list):
        queries = []
    queries = [q for q in queries if isinstance(q, str)][:2]
    queries.insert(0, f"{idea} {angle['title']}")

    pages, seen = [], set()
    for q in queries:
        for p in search(q, n=3):
            if p["url"] not in seen:
                seen.add(p["url"])
                pages.append(p)

    texts = [p["text"][:1500] for p in pages]
    listing = "\n\n".join(f"[{i}] {t}" for i, t in enumerate(texts, 1))
    reason, rejected = "ai_found_nothing", ""
    try:
        out = ask(PROMPT.format(idea=angle["idea"], pages=listing))
        if out.get("found"):
            quote = clean_quote(str(out.get("quote") or ""))
            product = str(out.get("product") or "")
            hits = [j for j, t in enumerate(texts) if verify_quote(quote, t)]
            if not hits:
                reason, rejected = "quote_rejected", f"page {out.get('page')}: {quote}"
            else:
                verdict = supports(angle["idea"], product, quote)
                if verdict == "no":
                    reason, rejected = "quote_does_not_support", quote
                else:
                    same = out.get("match") == "same" and verdict == "yes"
                    return {
                        "status": "same" if same else "similar",
                        "product": product,
                        "quote": quote,
                        "url": pages[hits[0]]["url"],
                        "difference": out.get("difference") or "",
                        "support": verdict,
                    }
    except (ValueError, KeyError, TypeError, AttributeError):
        reason = "bad_reply"
    return {"status": "none", "searched": len(pages), "reason": reason, "rejected": rejected}