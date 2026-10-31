"""
ml_model.py

A small machine learning model that answers one question:
    "Is this learner struggling and likely to need help from a mentor?"

IMPORTANT (honest note): I do not have Cynbit Studio's real student data.
So the training data below is SAMPLE data that I generate with simple rules + random noise.
The model therefore shows the PIPELINE (features -> train -> evaluate -> predict).
In the real product, only the data source would change: use real attempt logs.

Why a Decision Tree?
  - Easy to explain (it is just a set of if/else questions).
  - Works with small data, no scaling needed.
  - We can print the rules, so a mentor can see WHY a learner was flagged.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

FEATURES = ["attempts", "minutes_spent", "pass_ratio", "hints_used", "mission_level"]


def make_sample_data(n_rows=600, seed=42):
    """Create sample learner sessions. Label 1 = needs help, 0 = doing fine."""
    rng = np.random.default_rng(seed)

    data = pd.DataFrame({
        "attempts": rng.integers(1, 12, n_rows),            # how many times they pressed Run
        "minutes_spent": rng.integers(1, 60, n_rows),       # time on this mission
        "pass_ratio": rng.random(n_rows).round(2),          # fraction of tests passing (0 to 1)
        "hints_used": rng.integers(0, 4, n_rows),           # 0 to 3 hints opened
        "mission_level": rng.integers(1, 4, n_rows),        # 1 easy, 3 hard
    })

    # A simple "struggle score": more attempts / time / hints and low pass ratio = struggling.
    score = (
        0.4 * data["attempts"]
        + 0.05 * data["minutes_spent"]
        + 1.0 * data["hints_used"]
        + 3.0 * (1 - data["pass_ratio"])
        + 0.5 * data["mission_level"]
    )
    score = score + rng.normal(0, 0.7, n_rows)   # noise, because real people are not perfectly predictable
    data["needs_help"] = (score > score.median()).astype(int)
    return data


def train_model(seed=42):
    """Train the decision tree. Returns (model, accuracy_on_test_data)."""
    data = make_sample_data(seed=seed)
    X = data[FEATURES]
    y = data["needs_help"]

    # keep 20% of the data aside to test the model on data it has never seen
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

    model = DecisionTreeClassifier(max_depth=3, random_state=seed)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    return model, accuracy


def predict_needs_help(model, attempts, minutes_spent, pass_ratio, hints_used, mission_level):
    """Return the probability (0 to 1) that the learner needs help."""
    row = pd.DataFrame([[attempts, minutes_spent, pass_ratio, hints_used, mission_level]], columns=FEATURES)
    return float(model.predict_proba(row)[0][1])


def explain_rules(model):
    """Print the tree as readable if/else rules."""
    return export_text(model, feature_names=FEATURES)


def recommend_next_step(probability, mission_level):
    """Turn the probability into a simple suggestion for the learner."""
    if probability >= 0.65:
        return "You seem to be struggling a bit. Try an easier mission first, or ask a mentor for help."
    if probability <= 0.35 and mission_level < 3:
        return "You are doing great! Try a harder mission next."
    return "Good progress. Keep practising this mission and use hints only when stuck."


if __name__ == "__main__":
    model, accuracy = train_model()
    print("Test accuracy:", round(accuracy, 3))
    print(explain_rules(model))
