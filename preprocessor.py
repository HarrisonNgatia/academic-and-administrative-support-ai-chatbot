import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
        tokens = text.split()
        filtered = [w for w in tokens if w not in self.stop_words]
        stemmed = [self.stemmer.stem(w) for w in filtered]
        return " ".join(stemmed)