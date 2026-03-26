from sklearn.linear_model import LogisticRegression
import numpy as np

# Features: [current_health_score, health_trend_7d, rainfall_forecast, 
#            days_to_monsoon, complaint_velocity, historical_seasonal_risk]
# Label: 1 if complaint surge happened within 7 days, 0 otherwise

# Generate synthetic training data
def generate_prediction_data(n=500):
    X = np.random.rand(n, 6)
    # Surge likely when health low + rainfall high + seasonal risk high
    prob = 1 / (1 + np.exp(-(X[:,0]*-3 + X[:,2]*2 + X[:,4]*2 + X[:,5]*1.5)))
    y = (prob > 0.5 + np.random.normal(0, 0.1, n)).astype(int)
    return X, y

model_predict = LogisticRegression()
model_predict.fit(*generate_prediction_data())

def get_failure_probability(node_features):
    prob = model_predict.predict_proba([node_features])[0][1]
    return float(prob)