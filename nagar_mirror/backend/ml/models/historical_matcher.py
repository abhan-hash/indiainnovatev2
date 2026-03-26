# When a new cluster is found, compute its fingerprint vector
def compute_cluster_fingerprint(cluster_complaints):
    texts = [c['text'] for c in cluster_complaints]
    embeddings = model.encode(texts)
    return embeddings.mean(axis=0)  # Average = cluster fingerprint