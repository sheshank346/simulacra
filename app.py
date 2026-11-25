import glob
import html
import json

import streamlit as st

LABELS = {"same": "EXISTS", "similar": "SIMILAR IDEA EXISTS", "none": "NO CLOSE MATCH FOUND"}


def safe(text):
    return str(text).replace("$", "\\$")


st.set_page_config(page_title="Simulacra", layout="wide")
st.title("Simulacra")
st.caption("Does this idea already exist, what do users complain about, and how might people react?")
st.info("These are saved runs from real searches, not a live run.")

runs = {}
for path in sorted(glob.glob("examples/*.json")):
    run = json.load(open(path, encoding="utf-8"))
    runs[run["idea"]] = run

run = runs[st.selectbox("Idea", list(runs))]
v = run["verdict"]

st.subheader(LABELS[v["status"]])
if v["status"] == "none":
    st.write("No close match found. This does not prove the idea is new.")
else:
    st.write(safe(f'{v["product"]}: "{v["quote"]}"'))
    st.write(v["url"])

st.subheader("Verified complaints")
for i, g in enumerate(run["gaps"], 1):
    st.markdown(safe(f'{i}. **{g["product"]}**: {g["gap"]}  \n"{g["quote"]}" ([source]({g["url"]}))'))

angle = run["angle"]
st.subheader("Suggested angle")
st.write(safe(f'**{angle["title"]}**: {angle["idea"]}'))
st.write("Fixes complaints:", ", ".join(str(n) for n in angle["fixes"]))

st.subheader("How people might react")
template = open("backend/map_template.html", encoding="utf-8").read()
people = json.dumps(run["people"]).replace("</", "<\\/")
gaps = json.dumps([{"gap": g["gap"], "product": g["product"]} for g in run["gaps"]]).replace("</", "<\\/")
page = template.replace("__GAPS__", gaps).replace("__PEOPLE__", people).replace("__TITLE__", html.escape(angle["title"]))
st.iframe(page, height=950)