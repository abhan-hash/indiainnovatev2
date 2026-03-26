import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# Prompt 1: Voice extraction
def extract_complaint_from_voice(transcript, lat, lng):
    prompt = f"""
    Extract complaint information from this citizen's spoken complaint.
    Transcript: "{transcript}"
    GPS: {lat}, {lng}
    
    Return ONLY a JSON object with these fields:
    - type: one of [drainage, roads, electricity, waste, health, encroachment, safety, civic]
    - subtype: specific complaint (e.g. "blocked drain")
    - duration: how long the problem has existed (e.g. "1 week")
    - severity: 1-5 integer
    - description: clean English summary
    """
    response = model_gemini.generate_content(prompt)
    return response.text  # parse as JSON

# Prompt 2: Moral Alert narrative
def generate_moral_alert(complaint, grief_score, affected_population):
    prompt = f"""
    Write a firm, human moral alert for a municipal supervisor.
    Problem: {complaint['type']} at {complaint['location']}
    Unresolved for: {complaint['days_open']} days
    Grief Score: {grief_score} (critical threshold crossed)
    Affected: ~{affected_population} people
    Near: {complaint['sensitive_zone']}
    
    Write 3 sentences. Be specific. Be human. Not a system alert — a moral call to action.
    """
    return model_gemini.generate_content(prompt).text

# Prompt 3: Morning brief
def generate_morning_brief(critical_nodes, monitoring_nodes, resolved_yesterday):
    prompt = f"""
    Write a morning health brief for a municipal officer. Professional, scannable.
    
    IMMEDIATE ATTENTION nodes: {critical_nodes}
    MONITORING nodes: {monitoring_nodes}  
    RESOLVED yesterday: {resolved_yesterday}
    
    Format: Three sections with headers. Each item one sentence. Total under 200 words.
    """
    return model_gemini.generate_content(prompt).text