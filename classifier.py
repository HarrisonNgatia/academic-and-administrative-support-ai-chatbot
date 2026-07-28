import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

class IntentClassifier:
    def __init__(self, confidence_threshold=0.60):
        self.confidence_threshold = confidence_threshold
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
            ('clf', LinearSVC(C=1.0, max_iter=1000, random_state=42))
        ])

    def train(self, X_train: list, y_train: list):
        self.model.fit(X_train, y_train)

    def predict_with_confidence(self, text: str):
        decision_scores = self.model.decision_function([text])
        if decision_scores.ndim == 1:
            probabilities = 1 / (1 + np.exp(-decision_scores))
            max_score = float(probabilities[0])
            predicted_idx = int(decision_scores[0] > 0)
        else:
            exp_scores = np.exp(decision_scores - np.max(decision_scores))
            probabilities = exp_scores / exp_scores.sum(axis=1, keepdims=True)
            predicted_idx = np.argmax(probabilities[0])
            max_score = float(probabilities[0][predicted_idx])

        predicted_intent = self.model.classes_[predicted_idx]
        if max_score < self.confidence_threshold:
            return "general_fallback", max_score

        return predicted_intent, max_score