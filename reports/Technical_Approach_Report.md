# Technical Approach Report: Cynbit Studio Code Coach

Author: Diamond Tyagi. This explains how the proof of concept is built and how it would grow.

## 1. Goal

Give a learner quick, consistent feedback on a coding mission, and warn a mentor early when a learner is likely to struggle.

## 2. Architecture

```
Learner (Streamlit page: app.py)
        │ code
        ▼
 evaluator.py
   1. syntax check      (ast.parse)
   2. structure check   (ast: missing function, print vs return, nested loops)
   3. run tests         (separate Python process, 5 second limit)
        │ passed / total, failed cases, tips
        ▼
 app.py shows result + hints (missions.py)
        │ attempts, minutes, pass ratio, hints used, level
        ▼
 ml_model.py  (decision tree) → "chance you need extra help" → suggestion
```

Folder: `src/missions.py` (problems, tests, hints), `src/evaluator.py`, `src/ml_model.py`, `app.py`, `tests/`.

## 3. Components

### 3.1 Evaluator
- **Syntax check** uses `ast.parse`, so a typo gives a clear message with the line number instead of a crash.
- **Structure check** reads the code as a tree (`ast`) without running it. It finds: missing function name, `print` used without `return`, and a loop inside a loop on level 2 and 3 missions.
- **Test runner** starts a new Python process with `subprocess.run(..., timeout=5)`. The student's code runs there, so an infinite loop or a crash cannot freeze the app. Results come back as JSON. The student's own `print` output is discarded so it cannot break the JSON.

### 3.2 Hints
Each mission has 3 hints from vague to specific. The learner opens them one by one. The number of hints used is also a feature for the ML model.

### 3.3 ML model: "does this learner need help?"
- **Features:** attempts, minutes spent, share of tests passing, hints used, mission level.
- **Label:** 1 = needs help, 0 = fine.
- **Model:** `DecisionTreeClassifier(max_depth=3)` from scikit-learn.
- **Output:** a probability. Above 65% the app suggests an easier mission or a mentor, below 35% on a non-final level it suggests a harder mission.

## 4. Model choices and why

| Option | Why not (for now) |
|--------|-------------------|
| LLM judging every submission | Costs money on every run, can give different answers for the same code, slower. Tests already give a reliable pass or fail. |
| Logistic regression | Also fine and simple. I chose the tree because its rules can be shown to a mentor as plain if/else. |
| Random forest / gradient boosting | Often more accurate, but only worth it once there is real data. With sample data, accuracy would not mean anything. |
| **Decision tree (chosen)** | Easy to explain, needs no feature scaling, works on small data, and shows its rules. |

## 5. Data pipeline

**In this proof of concept (sample data).** I do not have real Studio logs, so `make_sample_data()` creates 600 sample sessions. A "struggle score" is built from the features plus random noise, and the top half becomes label 1. The data is split 80/20 for training and testing. The held-out accuracy is about 83%.

> This 83% only shows the code works. It is NOT a real-world accuracy, because the label was created from the same features by a rule I wrote.

**In production.**
1. Studio logs an event on every Run: learner id (pseudonymised), mission, timestamp, tests passed, hints used.
2. A scheduled job turns events into one row per learner per mission (the same 5 features).
3. The label comes from real outcomes, for example "did not finish within 7 days" or "asked a mentor".
4. Train, compare with a baseline (for example "more than 5 attempts"), and check precision and recall.
5. Serve the model inside the Studio backend (FastAPI is a good fit), and retrain monthly.
6. Track experiments and model versions with MLflow.

## 6. Where an LLM would fit (design only, not in the PoC)

Only after tests fail, to explain the failure in friendly words. Inputs: mission text, the student's code, and the failed test cases. It must not receive the model solution.

Prompt outline:

```
You are a patient Python mentor for beginners.
Mission: {description}
Student code: {code}
Failed tests: {failed_cases}
Rules:
- Do not write the full solution.
- Explain the likely mistake in 2 or 3 short sentences.
- Give one small next step.
- Reply as JSON: {"mistake": "...", "next_step": "..."}
```

Safeguards: send only failed cases (fewer tokens), cache answers for identical code and test results, cap the length, and validate the JSON before showing it.

## 7. Testing

`pytest` runs 7 tests: a correct answer passes, a wrong answer fails, a syntax error is reported, an infinite loop times out, the nested-loop tip appears, the print-without-return tip appears, and the model gives a higher risk to a struggling learner than to a learner who is doing fine.

## 8. Execution plan

| Phase | Work | Output |
|-------|------|--------|
| Week 1 | Add event logging to Studio, agree the definition of "struggling" with mentors | Event table |
| Week 2 to 3 | Move the evaluator behind an API in a sandbox (container, no network, memory limit) | Safe test-runner service |
| Week 4 | Train the model on real logs, compare with a baseline | Evaluation notebook |
| Week 5 | Add the LLM explanation layer with the safeguards above | Better hints |
| Week 6 | Pilot with one BitElevate batch, measure the KPIs from the Opportunity Report | Go or no-go decision |

## 9. Limitations

- Sample data, so the model's numbers are not real.
- Local process isolation is not a real security sandbox.
- Only 4 missions and only Python.
- Tests cannot judge style or readability.

## 10. How to run

See the README: `pip install -r requirements.txt`, then `streamlit run app.py`. Run `pytest` for the tests.
