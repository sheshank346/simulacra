# Evaluation results



## First full run (Nov 2026)



Model: openai/gpt-oss-20b (Groq free tier)

Test set: 20 well-known ideas, all of which exist (eval/ideas.json)



Result: 16 of 20 matched.

* 4 ideas had no verified match: language learning, freelance marketplace,

&#x20; home-service hiring, YouTube summarizer.

* Tokens used: about 84,000 for the whole set, roughly 4,200 per idea.
* No errors during the run.



## Reading the matches by hand



I read the 16 matched quotes against the feature each idea describes.

* 12 clearly support the feature (for example Zocdoc, Grubhub, Adobe Scan).
* 4 are weaker: YouTube Music (a short-video feed added to a music app),

&#x20; Houfy (quote does not say short-term stays), Codecademy (quote says

&#x20; "interactive learning" but not coding), Dapta (quote does not say it

&#x20; answers customer questions).



The verifier only proves that a quote appears on the page. It does not prove

the quote supports the claim, so a match can still be weak.



## Rejected quotes



* "Summarize YouTube videos with AI" is a valid match, but it has 5 words and

&#x20; the verifier requires 6, so it was dropped.

* A TaskRabbit quote about home repairs did not verify against the page text.

&#x20; It would have been "similar" at best.



## Earlier run on gpt-oss-120b



Stopped after 7 of 20 ideas because Groq's daily limit of 200,000 tokens was

used up. 5 of those 7 matched. Not comparable with the run above.



## What this does not measure



* All 20 ideas exist, so this says nothing about false matches. An agent that

&#x20; always answered "exists" would also score 20 of 20.

* Results change between runs. The same idea gave a match in one run and no

&#x20; match in another, even with temperature 0.

* Only one run on one model. The 20b score was higher than the 120b score on

&#x20; the first 7 ideas, and I do not know why.



## Next



* Add 10 to 20 obscure ideas that I checked by hand and could not find.
* Measure how often the agent claims a match for those.
* Repeat each idea several times to measure how stable the answers are.



## Second full run (after fixes)



Model: openai/gpt-oss-20b (Groq free tier), same 20 ideas as the first run.



Changes since the first run:

- search results are cached on disk, so repeated queries are free

- the model must give one unbroken quote with no "..."

- the quote is checked against every fetched page, not the page number the model names

- one retry when the model returns malformed JSON



Result: 19 of 20 matched (first run: 16 of 20).

- The only miss is the language-learning app. It found nothing on both runs.

- Tokens: roughly 95,000 across two sessions. The run stopped on a malformed-JSON

&#x20; error at idea 10 and was resumed.



Reading the matches (labels made with help from an AI assistant, not independently confirmed):

- 15 clearly supported, 4 weak.

- Weak: Zigazoo (quote says nothing about an endless feed), Google Pay (source is a

&#x20; video description), Sharetribe (a tool for building marketplaces, not a freelance

&#x20; marketplace), BookWellNow (booking software, not a hiring platform).

- Three ideas newly matched in this run. One is clearly supported (YouTube

&#x20; summarizer) and two are weak (freelance marketplace, home-service hiring), so part

&#x20; of the increase is weak matches.

- Weak share: 4 of 16 in the first run, 4 of 19 now. No clear change.



Caveats:

- A gap of 3 matches is within run-to-run noise. The same ideas flipped between

&#x20; runs earlier.

- Several things changed at once, so I cannot say which change helped.

- The verifier shows that a quote appears on a page. It does not show that the quote

&#x20; supports the feature, and several sources are video pages, not product pages.



Next:

- Add a second check that the quote actually supports the feature.

- Prefer product pages over video pages.

- Repeat runs with live searches to measure how stable the answers are.

