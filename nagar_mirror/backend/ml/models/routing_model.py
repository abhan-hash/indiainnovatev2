import xgboost as xgb
# Features: [complaint_type_encoded, ward_id, hour_of_day, day_of_week,
#            grief_score, officer_current_load, officer_past_success_rate_this_type]
# Label: officer_id (the one who got best outcome)

# For demo: seed data where Officer Sharma (id=1) always does best on drain complaints in Ward 7

model_routing = xgb.XGBClassifier(n_estimators=50)
# train on seeded outcome data

def recommend_officer(complaint_features, available_officer_ids):
    probs = model_routing.predict_proba([complaint_features])[0]
    # Filter to only available officers
    best = max(available_officer_ids, key=lambda oid: probs[oid] if oid < len(probs) else 0)
    return {"officer_id": best, "confidence": float(probs[best])}