"""
app.py  -  Cynbit Studio Code Coach (proof of concept)

Run with:   streamlit run app.py
"""

import time

import streamlit as st

from src.evaluator import evaluate
from src.missions import MISSIONS, get_mission
from src.ml_model import explain_rules, predict_needs_help, recommend_next_step, train_model

st.set_page_config(page_title="Cynbit Studio Code Coach", page_icon="💻")


# Train the model only once (Streamlit re-runs this file on every click, so we cache it).
@st.cache_resource
def load_model():
    return train_model()


model, model_accuracy = load_model()


def get_progress(mission_id):
    """Keep each mission's progress (attempts, hints, start time...) in session_state."""
    if "progress" not in st.session_state:
        st.session_state["progress"] = {}
    if mission_id not in st.session_state["progress"]:
        st.session_state["progress"][mission_id] = {
            "attempts": 0,
            "hints_used": 0,
            "start_time": time.time(),
            "last_result": None,
        }
    return st.session_state["progress"][mission_id]


# ---------- Sidebar: choose a mission ----------
st.sidebar.title("Missions")
titles = [m["title"] + "  (level " + str(m["level"]) + ")" for m in MISSIONS]
choice = st.sidebar.radio("Pick a mission", titles)
mission = MISSIONS[titles.index(choice)]
progress = get_progress(mission["id"])

st.sidebar.markdown("---")
st.sidebar.caption("Proof of concept for the Cynbit AI/ML Intern assessment. "
                   "Learner-risk model accuracy on sample data: " + str(round(model_accuracy * 100)) + "%")

# ---------- Main area ----------
st.title("Cynbit Studio Code Coach")
st.subheader(mission["title"])
st.write(mission["description"])

code = st.text_area("Write your code here", value=mission["starter"], height=220, key="code_" + mission["id"])

if st.button("Run my code", type="primary"):
    progress["attempts"] += 1
    progress["last_result"] = evaluate(code, get_mission(mission["id"]))

result = progress["last_result"]

# ---------- Show feedback ----------
if result is not None:
    st.markdown("### Result")

    if result["status"] == "syntax_error":
        st.error(result["message"])
    elif result["status"] in ("timeout", "error"):
        st.error(result["message"])
    else:
        st.write("Tests passed: **" + str(result["passed"]) + " / " + str(result["total"]) + "**")
        if result["passed"] == result["total"]:
            st.success("All tests passed. Well done!")
            st.balloons()
        for test in result["results"]:
            icon = "✅" if test["passed"] else "❌"
            line = icon + " input: " + str(test["args"]) + "  expected: " + str(test["expected"])
            if not test["passed"]:
                line += "  but got: " + str(test["got"])
            st.write(line)

    for tip in result.get("tips", []):
        st.info("Tip: " + tip)

# ---------- Hints ----------
st.markdown("### Need a hint?")
if st.button("Give me a hint"):
    progress["hints_used"] = min(progress["hints_used"] + 1, len(mission["hints"]))

for number in range(progress["hints_used"]):
    st.write("Hint " + str(number + 1) + ": " + mission["hints"][number])

# ---------- ML part: is the learner struggling? ----------
if progress["attempts"] > 0 and result is not None:
    st.markdown("### Your progress check")
    minutes = min(int((time.time() - progress["start_time"]) / 60) + 1, 59)
    pass_ratio = result["passed"] / result["total"]

    probability = predict_needs_help(
        model,
        attempts=min(progress["attempts"], 11),
        minutes_spent=minutes,
        pass_ratio=pass_ratio,
        hints_used=progress["hints_used"],
        mission_level=mission["level"],
    )
    st.write("Chance that you need extra help: **" + str(round(probability * 100)) + "%**")
    st.progress(probability)
    st.write(recommend_next_step(probability, mission["level"]))

    with st.expander("How did the model decide? (for mentors)"):
        st.code(explain_rules(model))
        st.caption("The model is a small decision tree trained on SAMPLE data, "
                   "because real Cynbit Studio data is not public.")
