import glob
import html
import json
import os
import sys
import time

import streamlit as st

sys.path.insert(0, "backend")
for key in ("TAVILY_API_KEY", "GROQ_API_KEY", "OLOSTEP_API_KEY", "GROQ_MODEL"):
    try:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
    except Exception:
        pass

LABELS = {"same": "EXISTS", "similar": "SIMILAR IDEA EXISTS", "none": "NO CLOSE MATCH FOUND"}
DAILY_RUNS = 3
BLOCKED = ["make a bomb", "build a bomb", "write ransomware", "build malware",
           "phishing page", "hack into", "counterfeit money", "stalk someone"]


def safe(text):
    return str(text).replace("$", "\\$")


@st.cache_resource
def store():
    return {"day": "", "runs": 0, "results": {}}


def runs_left():
    s = store()
    today = time.strftime("%Y-%m-%d")
    if s["day"] != today:
        s["day"], s["runs"] = today, 0
    return DAILY_RUNS - s["runs"]


def problem_with(idea):
    if len(idea.split()) < 3:
        return "Please describe the idea in at least 3 words."
    if len(idea) > 300:
        return "Please keep the idea under 300 characters."
    if any(b in idea.lower() for b in BLOCKED):
        return "This tool does not check ideas meant to cause harm."
    return None


def page_for(run):
    template = open("backend/map_template.html", encoding="utf-8").read()
    people = json.dumps(run["people"]).replace("</", "<\\/")
    gaps = json.dumps([{"gap": g["gap"], "product": g["product"]} for g in run["gaps"]]).replace("</", "<\\/")
    title = html.escape(run["angle"]["title"])
    return template.replace("__GAPS__", gaps).replace("__PEOPLE__", people).replace("__TITLE__", title)


def show(run, where):
    v = run["verdict"]
    st.subheader(LABELS[v["status"]])
    if v["status"] == "none":
        st.write("No close match found. This does not prove the idea is new.")
        if v.get("reason") == "quote_rejected":
            st.caption("A possible match was found, but its quote could not be verified, so it is not shown.")
    else:
        st.write(safe(f'{v["product"]}: "{v["quote"]}"'))
        st.write(v["url"])
    st.subheader("Verified complaints")
    for i, g in enumerate(run["gaps"], 1):
        st.markdown(safe(f'{i}. **{g["product"]}**: {g["gap"]}  \n"{g["quote"]}" ([source]({g["url"]}))'))
    angle = run["angle"]
    if angle is None:
        st.warning(f'Only {len(run["gaps"])} verified complaints were found, which was not enough to suggest an angle.')
        return
    st.subheader("Suggested angle")
    st.write(safe(f'**{angle["title"]}**: {angle["idea"]}'))
    st.write("Fixes complaints:", ", ".join(str(n) for n in angle["fixes"]))
    st.subheader("How people might react")
    st.iframe(page_for(run), height=950)
    st.download_button("Download this result", json.dumps(run, indent=2),
                       file_name="simulacra-run.json", key="dl-" + where, on_click="ignore")


st.set_page_config(page_title="Simulacra", layout="wide")
st.title("Simulacra")
st.caption("Does this idea already exist, what do users complain about, and how might people react?")

live, saved = st.tabs(["Try your idea", "Saved examples"])

with live:
    idea = st.text_input("Describe your idea", placeholder="an app to ...").strip()
    region = st.text_input("Where? (optional)", value="India").strip()
    slot = st.empty()
    if st.button("Run"):
        full = f"{idea} in {region}" if region else idea
        key = full.lower()
        problem = problem_with(idea)
        if problem:
            st.error(problem)
        elif key in store()["results"]:
            st.info("Someone already ran this idea today, so this is the saved result.")
            show(store()["results"][key], "live")
        elif runs_left() <= 0:
            st.warning("The daily limit of live runs has been reached. See the saved examples tab.")
        else:
            store()["runs"] += 1
            try:
                import pipeline

                with st.status("Starting", expanded=True) as status:
                    result = pipeline.run(full, progress=lambda m: (status.update(label=m), st.write(m)))
                    status.update(label="Done", state="complete")
                store()["results"][key] = result
                show(result, "live")
            except Exception as e:
                if e.__class__.__name__ == "PipelineError":
                    st.error(str(e))
                else:
                    st.error("The live run failed, possibly because a daily limit was reached. Please try the saved examples.")
    slot.caption(f"Live runs left today: {max(runs_left(), 0)}. A run takes about 2 minutes.")

with saved:
    st.info("These are saved runs from real searches, not a live run.")
    runs = {}
    for path in sorted(glob.glob("examples/*.json")):
        run = json.load(open(path, encoding="utf-8"))
        runs[run["idea"]] = run
    show(runs[st.selectbox("Idea", list(runs))], "saved")