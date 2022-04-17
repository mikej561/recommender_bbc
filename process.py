import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def preprocess(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def get_tfidf(data):
    tfidf_vectorizer = TfidfVectorizer(preprocessor=preprocess, lowercase=True, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(data)
    return tfidf
    
def get_labels(data, num):
    kmeans = KMeans(n_clusters=num).fit(data)
    return kmeans