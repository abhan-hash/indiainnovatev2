import xgboost as xgb
import numpy as np
from sklearn.model_selection import train_test_split
import shap

# Features per node (you generate this synthetically)
# [complaint_count_30d, complaint_acceleration, node_age_years, 
#  last_maintenance_days, zone_type_encoded, rainfall_forecast, 
#  connected_node_avg_health]

def generate_seed_data(n=1000):
    # Generate fake but realistic node states
    X = np.random.rand(n, 7)
    # Health score = roughly inverse of complaints + age + weather
    y = 100 - (X[:,0]*30 + X[:,1]*20 + X[:,2]*15 + X[:,3]*10 + X[:,5]*25)
    y = np.clip(y, 0, 100)
    return X, y

X, y = generate_seed_data()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model_risk = xgb.XGBRegressor(n_estimators=100, max_depth=4)
model_risk.fit(X_train, y_train)

# SHAP explanation
explainer = shap.TreeExplainer(model_risk)

def get_risk_score(node_features):
    score = model_risk.predict([node_features])[0]
    shap_values = explainer.shap_values([node_features])[0]
    feature_names = ['complaint_count', 'acceleration', 'age', 
                     'maintenance_gap', 'zone_type', 'rainfall', 'neighbor_health']
    explanation = dict(zip(feature_names, shap_values.tolist()))
    return {
        "score": float(np.clip(score, 0, 100)),
        "trajectory": "worsening" if score < 50 else "stable",
        "shap": explanation
    }