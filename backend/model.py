import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier

# ------------------ REPRODUCIBILITY ------------------
random.seed(42)
np.random.seed(42)

# ------------------ MAPPINGS ------------------

branch_map = {
    "Computer Science": 1,
    "Electronics": 2,
    "Mechanical": 3,
    "Civil": 4,
    "Commerce": 5,
    "Arts": 6,
    "Science": 7
}

year_map = {1: 1, 2: 2, 3: 3, 4: 4}

# Career IDs must match database.py exactly.
# 1 Software Engineer
# 2 Doctor
# 3 Data Scientist
# 4 Cybersecurity Analyst
# 5 Blockchain Developer
# 6 Robotics Engineer
# 7 Aerospace Engineer
# 8 Game Developer
# 9 UI/UX Designer
# 10 Cloud Engineer
# 11 Product Manager
# 12 Lawyer
# 13 Biotech Engineer
# 14 Energy Engineer

# ------------------ BASE DATASET ------------------

X_base = np.array([
    [1, 1, 9.0, 1],
    [1, 2, 8.8, 6],
    [1, 3, 8.6, 14],

    [7, 1, 9.2, 2],
    [7, 2, 8.7, 18],

    [1, 2, 8.8, 15],
    [7, 2, 8.9, 6],

    [1, 2, 8.4, 7],
    [2, 3, 8.1, 7],

    [5, 2, 8.2, 8],
    [1, 3, 8.0, 8],

    [3, 2, 8.0, 9],
    [2, 3, 8.2, 19],

    [3, 2, 8.3, 10],
    [4, 3, 8.0, 10],

    [1, 2, 8.1, 12],
    [6, 2, 7.9, 12],

    [6, 1, 8.0, 13],
    [6, 2, 8.3, 4],

    [1, 2, 8.6, 14],
    [1, 3, 8.4, 20],

    [5, 3, 8.5, 16],
    [5, 2, 8.2, 5],

    [6, 2, 8.0, 17],
    [6, 3, 8.3, 17],

    [7, 2, 8.9, 18],
    [7, 3, 9.0, 2],

    [3, 2, 8.1, 11],
    [4, 3, 8.0, 20],
])

y_base = np.array([
    1, 1, 1,
    2, 2,
    3, 3,
    4, 4,
    5, 5,
    6, 6,
    7, 7,
    8, 8,
    9, 9,
    10, 10,
    11, 11,
    12, 12,
    13, 13,
    14, 14
])


def generate_synthetic_data(n=350):
    data = []
    labels = []

    for _ in range(n):
        branch = random.randint(1, 7)
        year = random.randint(1, 4)
        cgpa = round(random.uniform(6.0, 9.9), 1)
        interest = random.randint(1, 20)

        if interest == 2:
            career = 2
        elif interest == 6:
            career = 3 if cgpa >= 8.2 else 1
        elif interest == 7:
            career = 4
        elif interest == 8:
            career = 5
        elif interest == 9 or interest == 19:
            career = 6
        elif interest == 10:
            career = 7
        elif interest == 12:
            career = 8
        elif interest == 4 or interest == 13:
            career = 9
        elif interest == 14 or interest == 20:
            career = 10
        elif interest == 16 or interest == 5:
            career = 11
        elif interest == 17:
            career = 12
        elif interest == 18:
            career = 13
        elif interest == 15:
            career = 3
        elif interest == 1:
            career = 1 if branch == 1 and cgpa >= 8.3 else 10
        else:
            career = random.randint(1, 14)

        data.append([branch, year, cgpa, interest])
        labels.append(career)

    return np.array(data), np.array(labels)


X_syn, y_syn = generate_synthetic_data(350)
X = np.vstack([X_base, X_syn])
y = np.concatenate([y_base, y_syn])


def add_features(X):
    branch_interest = (X[:, 0] * X[:, 3]).reshape(-1, 1)
    year_interest = (X[:, 1] * X[:, 3]).reshape(-1, 1)
    cgpa_interest = (X[:, 2] * X[:, 3]).reshape(-1, 1)
    return np.hstack([X, branch_interest, year_interest, cgpa_interest])


X = add_features(X)

# ------------------ MODEL TRAINING ------------------

model = RandomForestClassifier(
    n_estimators=220,
    max_depth=14,
    random_state=42,
    class_weight="balanced_subsample"
)

model.fit(X, y)


# ------------------ RULE ENGINE ------------------

def rule_engine(branch, cgpa, interest_id):
    if branch == "Computer Science":
        if interest_id in {7}:
            return 4
        if interest_id in {8}:
            return 5
        if interest_id in {14, 20}:
            return 10
        if interest_id in {15, 6}:
            return 3 if cgpa >= 8.2 else 1
        if interest_id in {13, 4}:
            return 9
        if interest_id in {16, 5}:
            return 11
        if interest_id == 1 and cgpa >= 8.3:
            return 1

    if interest_id == 2:
        return 2
    if interest_id == 9:
        return 6
    if interest_id == 10:
        return 7
    if interest_id == 12:
        return 8
    if interest_id == 11:
        return 14
    if interest_id == 17:
        return 12
    if interest_id == 18:
        return 13
    if interest_id == 19:
        return 6

    return None


# ------------------ HELPERS ------------------

def _soften_probabilities(probs, uniform_mix=0.15):
    """
    Prevents hard 100% outputs from a single-class vote.
    """
    probs = np.asarray(probs, dtype=float)
    probs = np.clip(probs, 0.0, None)

    total = probs.sum()
    if total <= 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs = probs / total

    uniform = np.ones_like(probs) / len(probs)
    probs = (1.0 - uniform_mix) * probs + uniform_mix * uniform
    probs = probs / probs.sum()
    return probs


def _apply_rule_boost(probs, classes, rule_pred, boost=0.18, penalty=0.01):
    """
    Boost the rule-predicted class without overriding the model.
    """
    probs = probs.copy()
    if rule_pred is None:
        return probs

    rule_idx = np.where(classes == rule_pred)[0]
    if len(rule_idx) == 0:
        return probs

    idx = rule_idx[0]
    probs[idx] += boost

    for i in range(len(probs)):
        if i != idx:
            probs[i] = max(0.0, probs[i] - penalty)

    probs = _soften_probabilities(probs, uniform_mix=0.08)
    return probs


# ------------------ PREDICTION FUNCTION ------------------

def predict_career(student):
    branch = student.branch
    cgpa = float(student.cgpa)
    interest = int(student.interest_id)
    year = int(student.year)

    base_features = [
        branch_map.get(branch, 1),
        year_map.get(year, 1),
        cgpa,
        interest
    ]

    interaction_features = [
        base_features[0] * base_features[3],
        base_features[1] * base_features[3],
        base_features[2] * base_features[3]
    ]

    features = [base_features + interaction_features]

    probs = model.predict_proba(features)[0]
    classes = model.classes_

    # Base ML probabilities, softened so they never become absurdly confident.
    probs = _soften_probabilities(probs, uniform_mix=0.15)

    # Domain rule boost.
    rule_pred = rule_engine(branch, cgpa, interest)
    probs = _apply_rule_boost(probs, classes, rule_pred, boost=0.20, penalty=0.01)

    # Ensure the rule-predicted career appears in top 3 if it exists.
    top_indices = np.argsort(probs)[-3:][::-1].tolist()

    if rule_pred is not None:
        rule_idx = np.where(classes == rule_pred)[0]
        if len(rule_idx):
            r = rule_idx[0]
            if r not in top_indices:
                top_indices[-1] = r
                top_indices = sorted(top_indices, key=lambda i: probs[i], reverse=True)

    top3_ids = classes[top_indices]
    top3_conf = [round(float(probs[i]) * 100, 2) for i in top_indices]

    # Safety: keep output realistic and readable.
    top3_conf = [min(max(c, 0.0), 95.0) for c in top3_conf]

    return top3_ids.tolist(), top3_conf


def predict_career_with_explainability(student):
    """
    Optional helper if you want to show which features influenced the model.
    """
    top3_ids, top3_conf = predict_career(student)
    importance = model.feature_importances_.tolist()
    return {
        "top3_ids": top3_ids,
        "confidences": top3_conf,
        "feature_importance": importance
    }