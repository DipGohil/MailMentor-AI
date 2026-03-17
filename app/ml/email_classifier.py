import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "app/ml/model.pkl"
VECTORIZER_PATH = "app/ml/vectorizer.pkl"


# Training data
TRAIN_DATA = [
    ("job opening data scientist apply now", "Job"),
    ("we are hiring software engineer", "Job"),
    ("interview scheduled tomorrow", "Job"),

    ("invoice attached for payment", "Finance"),
    ("your bank transaction successful", "Finance"),
    ("fund transfer completed", "Finance"),

    ("meeting scheduled at 5 pm", "Meeting"),
    ("calendar invite for discussion", "Meeting"),
    ("join zoom meeting tomorrow", "Meeting"),

    ("limited offer discount sale", "Promotion"),
    ("premium subscription offer", "Promotion"),

    ("otp verification code", "Security"),
    ("security alert login attempt", "Security"),

    ("hello how are you", "General"),
    ("just checking in", "General"),
]


def train_model():
    texts = [t[0] for t in TRAIN_DATA]
    labels = [t[1] for t in TRAIN_DATA]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression()
    model.fit(X, labels)

    # save
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print("ML model trained & saved")


def load_model():
    if not os.path.exists(MODEL_PATH):
        train_model()

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    return model, vectorizer


# Predict
model, vectorizer = load_model()

def predict_category(text: str):
    X = vectorizer.transform([text])
    return model.predict(X)[0]