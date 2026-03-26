from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def cluster_complaints(complaints):
    # complaints = list of {id, text, lat, lng, timestamp}
    texts = [c['text'] for c in complaints]
    embeddings = model.encode(texts)
    
    # Add GPS as features (scaled)
    gps = np.array([[c['lat']*100, c['lng']*100] for c in complaints])
    features = np.hstack([embeddings, gps])
    
    clustering = DBSCAN(eps=0.5, min_samples=3).fit(features)
    return clustering.labels_  # -1 = noise, 0,1,2... = cluster IDs