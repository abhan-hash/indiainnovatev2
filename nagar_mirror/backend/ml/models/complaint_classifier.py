from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Your training data - just a list of complaints + labels
training_texts = [
    "naali band hai paani aa raha hai",
    "pothole on road near school",
    "bijli nahi hai 3 din se",
    "kachra nahi utha 5 din se",
    # add ~50 more per category
]
training_labels = ["drainage", "roads", "electricity", "waste", ...]

# Generate embeddings
embeddings = model.encode(training_texts)

# Train a simple classifier on top
classifier = LogisticRegression()
classifier.fit(embeddings, training_labels)

# Inference
def classify_complaint(text):
    embedding = model.encode([text])
    label = classifier.predict(embedding)[0]
    confidence = classifier.predict_proba(embedding).max()
    return {"type": label, "confidence": float(confidence)}