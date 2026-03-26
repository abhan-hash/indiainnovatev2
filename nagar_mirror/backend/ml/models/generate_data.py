"""
NagarMirror — Synthetic Data Generator
Area: Connaught Place, New Delhi
Run: python generate_data.py
Output: /data/*.json
"""

import json, random, math, uuid, hashlib
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
Path("data").mkdir(exist_ok=True)

# ─────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────

# Connaught Place bounding box
CP_CENTER = (28.6315, 77.2167)

# Named locations with real approximate coords
CP_LOCATIONS = {
    "A Block CP":            (28.6328, 77.2198),
    "B Block CP":            (28.6335, 77.2182),
    "C Block CP":            (28.6340, 77.2160),
    "D Block CP":            (28.6330, 77.2143),
    "E Block CP":            (28.6315, 77.2137),
    "F Block CP":            (28.6300, 77.2143),
    "G Block CP":            (28.6292, 77.2160),
    "H Block CP":            (28.6295, 77.2182),
    "Palika Bazaar":         (28.6317, 77.2173),
    "Central Park CP":       (28.6319, 77.2166),
    "Rajiv Chowk Metro":     (28.6328, 77.2197),
    "Patel Chowk Metro":     (28.6271, 77.2162),
    "Janpath Market":        (28.6270, 77.2189),
    "Connaught Lane":        (28.6348, 77.2155),
    "Outer Circle N":        (28.6360, 77.2165),
    "Outer Circle E":        (28.6330, 77.2215),
    "Outer Circle S":        (28.6275, 77.2167),
    "Outer Circle W":        (28.6305, 77.2120),
    "Baba Kharak Singh Marg":(28.6285, 77.2130),
    "Sansad Marg":           (28.6370, 77.2100),
    "Kasturba Gandhi Marg":  (28.6298, 77.2235),
    "Barakhamba Road":       (28.6340, 77.2230),
    "Tolstoy Marg":          (28.6288, 77.2212),
    "Shaheed Bhagat Singh Marg": (28.6325, 77.2145),
}

WARD_ZONES = {
    "inner_circle":  {"income_proxy": "high",   "sensitivity": 1.5, "population_density": 12000},
    "middle_ring":   {"income_proxy": "medium",  "sensitivity": 1.2, "population_density": 8000},
    "outer_roads":   {"income_proxy": "medium",  "sensitivity": 1.3, "population_density": 15000},
    "service_lanes": {"income_proxy": "low",     "sensitivity": 2.0, "population_density": 22000},
}

def jitter(lat, lng, radius_m=80):
    """Add small random offset to coordinates."""
    dlat = random.uniform(-radius_m, radius_m) / 111000
    dlng = random.uniform(-radius_m, radius_m) / (111000 * math.cos(math.radians(lat)))
    return round(lat + dlat, 6), round(lng + dlng, 6)

def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def ts(dt):
    return dt.isoformat()

NOW      = datetime(2026, 3, 20, 10, 0, 0)
THREE_MO = NOW - timedelta(days=90)
SIX_MO   = NOW - timedelta(days=180)
FOUR_YR  = NOW - timedelta(days=4 * 365)


# ─────────────────────────────────────────
# 1. INFRASTRUCTURE NODES (120 nodes)
# ─────────────────────────────────────────

NODE_TYPES = {
    "drain":       {"count": 22, "age_range": (5, 35),  "base_health": (45, 85)},
    "road":        {"count": 25, "age_range": (2, 20),  "base_health": (50, 90)},
    "transformer": {"count": 18, "age_range": (8, 25),  "base_health": (55, 88)},
    "water_main":  {"count": 15, "age_range": (10, 40), "base_health": (40, 80)},
    "street_light":{"count": 12, "age_range": (1, 12),  "base_health": (60, 95)},
    "public_toilet":{"count": 8,  "age_range": (3, 15),  "base_health": (30, 70)},
    "garbage_zone":{"count": 10, "age_range": (1, 8),   "base_health": (35, 75)},
    "park":        {"count": 5,  "age_range": (10, 50), "base_health": (55, 85)},
    "sewer_main":  {"count": 5,  "age_range": (15, 45), "base_health": (35, 72)},
}

ZONE_ASSIGN = list(WARD_ZONES.keys())

location_names = list(CP_LOCATIONS.items())

nodes = []
node_id_counter = 1

for ntype, cfg in NODE_TYPES.items():
    for i in range(cfg["count"]):
        loc_name, (base_lat, base_lng) = random.choice(location_names)
        lat, lng = jitter(base_lat, base_lng, radius_m=120)
        age = random.randint(*cfg["age_range"])
        health = random.randint(*cfg["base_health"])
        zone = random.choice(ZONE_ASSIGN)
        maintenance_days_ago = random.randint(10, 400)

        # A few nodes deliberately degraded for demo story
        if ntype == "drain" and i < 4:
            health = random.randint(18, 38)   # critical drains
        if ntype == "road" and i < 3:
            health = random.randint(25, 45)   # bad roads near bad drains
        if ntype == "transformer" and i < 2:
            health = random.randint(30, 50)

        nodes.append({
            "id":                   f"NODE-{node_id_counter:03d}",
            "type":                 ntype,
            "name":                 f"{ntype.replace('_',' ').title()} {loc_name} #{i+1}",
            "lat":                  lat,
            "lng":                  lng,
            "health_score":         health,
            "age_years":            age,
            "zone_type":            zone,
            "location_name":        loc_name,
            "last_maintenance_date": ts(NOW - timedelta(days=maintenance_days_ago)),
            "complaint_count":      random.randint(0, 18),
            "ward_id":              "WARD-CP-01",
        })
        node_id_counter += 1

# ─── mark demo nodes ───
# For the main demo story: drain → road → transformer cascade near Rajiv Chowk
drain_demo    = next(n for n in nodes if n["type"] == "drain"       and n["id"] == "NODE-001")
road_demo     = next(n for n in nodes if n["type"] == "road"        and n["id"] == "NODE-024")
trafo_demo    = next(n for n in nodes if n["type"] == "transformer" and n["id"] == "NODE-048")

drain_demo.update({"health_score": 22, "name": "Storm Drain — Rajiv Chowk N",
                   "lat": 28.6341, "lng": 77.2195, "complaint_count": 14,
                   "last_maintenance_date": ts(NOW - timedelta(days=310))})
road_demo.update( {"health_score": 38, "name": "Road Segment — Outer Circle NE",
                   "lat": 28.6352, "lng": 77.2208})
trafo_demo.update({"health_score": 51, "name": "Transformer — Barakhamba Rd Junction",
                   "lat": 28.6345, "lng": 77.2228})


# ─────────────────────────────────────────
# 2. GRAPH EDGES (160 edges)
# ─────────────────────────────────────────

drain_ids  = [n["id"] for n in nodes if n["type"] == "drain"]
road_ids   = [n["id"] for n in nodes if n["type"] == "road"]
trafo_ids  = [n["id"] for n in nodes if n["type"] == "transformer"]
water_ids  = [n["id"] for n in nodes if n["type"] == "water_main"]
sewer_ids  = [n["id"] for n in nodes if n["type"] == "sewer_main"]

edges = []
edge_id = 1

def make_edge(src, tgt, etype, weight, desc):
    global edge_id
    edges.append({
        "id":     f"EDGE-{edge_id:03d}",
        "source": src,
        "target": tgt,
        "type":   etype,
        "weight": weight,
        "description": desc,
    })
    edge_id += 1

# Demo cascade chain (explicit, high weight)
make_edge("NODE-001", "NODE-024", "physical_flow",      0.82, "Drain overflow saturates road subgrade")
make_edge("NODE-024", "NODE-048", "risk_propagation",   0.55, "Road subsidence exposes transformer cable conduit")
make_edge("NODE-001", "NODE-024", "service_dependency", 0.70, "Road drainage depends on this storm drain")

# Drain → Road connections (drains feed into nearby roads)
for d in drain_ids[:18]:
    road = random.choice(road_ids)
    if d != "NODE-001":  # already done above
        make_edge(d, road, "physical_flow", round(random.uniform(0.4, 0.85), 2),
                  "Drain overflow risk to adjacent road")

# Road → Transformer (road subsidence near underground cables)
for r in road_ids[:15]:
    t = random.choice(trafo_ids)
    make_edge(r, t, "risk_propagation", round(random.uniform(0.2, 0.6), 2),
              "Road damage near underground electrical infrastructure")

# Water main → Sewer (pressure differential causes backflow)
for w in water_ids[:10]:
    s = random.choice(sewer_ids)
    make_edge(w, s, "service_dependency", round(random.uniform(0.3, 0.7), 2),
              "Water main break increases sewer pressure")

# Sewer → Drain (overflow chain)
for s in sewer_ids:
    d = random.choice(drain_ids)
    make_edge(s, d, "physical_flow", round(random.uniform(0.5, 0.9), 2),
              "Sewer overflow backs up into storm drain")

# Transformer → Street light (power supply)
light_ids = [n["id"] for n in nodes if n["type"] == "street_light"]
for t in trafo_ids[:12]:
    l = random.choice(light_ids)
    make_edge(t, l, "service_dependency", round(random.uniform(0.7, 0.95), 2),
              "Street lights powered by this transformer")

# Fill remaining to reach ~160
road_pairs = [(random.choice(road_ids), random.choice(road_ids)) for _ in range(30)]
for src, tgt in road_pairs:
    if src != tgt and len(edges) < 160:
        make_edge(src, tgt, "physical_flow", round(random.uniform(0.2, 0.5), 2),
                  "Adjacent road segments share drainage")

edges = edges[:160]  # cap at 160


# ─────────────────────────────────────────
# 3. OFFICERS (10 officers)
# ─────────────────────────────────────────

OFFICER_NAMES = [
    ("Ramesh Sharma",    "drainage",    "WARD-CP-01", 0.91, 4.1),
    ("Priya Verma",      "roads",       "WARD-CP-01", 0.87, 5.2),
    ("Deepak Nair",      "electricity", "WARD-CP-01", 0.83, 6.8),
    ("Sunita Yadav",     "waste",       "WARD-CP-01", 0.79, 5.5),
    ("Anil Gupta",       "drainage",    "WARD-CP-01", 0.61, 11.2),
    ("Kavita Singh",     "health",      "WARD-CP-01", 0.85, 4.9),
    ("Mohit Chauhan",    "roads",       "WARD-CP-01", 0.68, 9.1),
    ("Rekha Pillai",     "encroachment","WARD-CP-01", 0.88, 3.7),
    ("Suresh Tiwari",    "safety",      "WARD-CP-01", 0.92, 3.2),
    ("Neha Bose",        "civic",       "WARD-CP-01", 0.76, 6.3),
]

officers = []
for i, (name, specialty, ward, conf_rate, avg_days) in enumerate(OFFICER_NAMES, 1):
    parts = name.split()
    officers.append({
        "id":                    f"OFF-{i:03d}",
        "name":                  name,
        "email":                 f"{parts[0].lower()}.{parts[1].lower()}@mcd.delhi.gov.in",
        "role":                  "supervisor" if i == 1 else "officer",
        "specialty":             specialty,
        "ward_id":               ward,
        "join_date":             ts(NOW - timedelta(days=random.randint(180, 1800))),
        "citizen_confirmation_rate": conf_rate,
        "avg_resolution_days":   avg_days,
        "complaints_resolved":   random.randint(40, 280),
        "prevention_credits":    random.randint(0, 18),
        "active":                True,
    })

# ─── Routing outcomes (for Model 7 training) ───
COMPLAINT_TYPES = ["drainage", "roads", "electricity", "waste",
                   "health", "encroachment", "safety", "civic"]

routing_outcomes = []
for _ in range(600):
    ctype     = random.choice(COMPLAINT_TYPES)
    officer   = random.choice(officers)
    # Sharma is demonstrably best for drainage in CP
    if ctype == "drainage":
        officer = officers[0] if random.random() < 0.55 else random.choice(officers)
    res_days  = max(1, round(random.gauss(officer["avg_resolution_days"], 2.0), 1))
    confirmed = random.random() < officer["citizen_confirmation_rate"]
    routing_outcomes.append({
        "complaint_type":       ctype,
        "officer_id":           officer["id"],
        "ward_id":              "WARD-CP-01",
        "zone_type":            random.choice(ZONE_ASSIGN),
        "season":               random.choice(["winter","spring","monsoon","post_monsoon"]),
        "hour_of_day":          random.randint(6, 22),
        "resolution_days":      res_days,
        "citizen_confirmed":    confirmed,
        "recurred_90d":         random.random() < 0.12,
        "outcome_score":        round((1/res_days)*40 + (0.6 if confirmed else 0)*60, 2),
    })


# ─────────────────────────────────────────
# 4. COMPLAINT HISTORY (900 complaints, 3 months)
# ─────────────────────────────────────────

COMPLAINT_TEMPLATES = {
    "drainage": [
        ("naali band hai, paani sadak pe aa raha hai", "Blocked drain, water spilling onto road", 4),
        ("gutter overflow ho raha hai bachon ke school ke paas", "Gutter overflow near children's school", 5),
        ("drain se bahut buri smell aa rahi hai", "Foul smell from drain near market", 3),
        ("manhole ka dhakna toot gaya hai, khatra hai", "Broken manhole cover, safety hazard", 5),
        ("baarish ke baad paani nahi nikal raha", "Waterlogging after rain not draining", 4),
        ("sewer line blocked near Palika Bazaar exit", "Sewer blockage causing overflow", 4),
        ("open drain without cover near pedestrian path", "Uncovered drain near footpath", 4),
    ],
    "roads": [
        ("sadak pe bada gadhha hai, accident ho sakta hai", "Large pothole on road, accident risk", 4),
        ("road ki surface bilkul toot gayi hai", "Road surface completely broken", 4),
        ("footpath pe tiles uki hui hain log gir rahe hain", "Loose footpath tiles causing falls", 3),
        ("divider toot gaya hai inner circle mein", "Broken road divider in inner circle", 3),
        ("road pe raat ko light nahi, andhere mein gadhhe hain", "Dark road with potholes, no lighting", 4),
        ("barricades without markings blocking half road", "Unmarked barricades on road", 3),
        ("road mein pipe tod ke khoda hai, bhar nahi kiya", "Road dug for pipe work, not refilled", 5),
    ],
    "electricity": [
        ("street light nahi jal rahi 1 hafte se", "Street light not working for 1 week", 3),
        ("bijli ka taar neeche latkaa hua hai, bahut khatarnak", "Live wire hanging low, very dangerous", 5),
        ("transformer ki awaaz aa rahi hai, jhatak maar raha hai", "Transformer sparking and making noise", 5),
        ("power outage since morning near B Block", "Power outage B Block area", 4),
        ("electric pole damaged after truck collision", "Damaged electric pole", 4),
        ("street lights are on during daytime wasting electricity", "Street lights on during day", 2),
    ],
    "waste": [
        ("dustbin 4 din se nahi uthaya gaya", "Garbage bin not collected for 4 days", 3),
        ("kachra sadak ke beech mein pada hua hai", "Garbage dumped in middle of road", 4),
        ("park mein illegal dumping ho raha hai raat ko", "Illegal dumping in park at night", 4),
        ("garbage not collected from service lane for a week", "Missed garbage collection", 3),
        ("overflowing dustbin near metro exit creating stench", "Overflowing bin near metro", 3),
        ("construction debris dumped on footpath near F Block", "Illegal debris dumping", 3),
    ],
    "health": [
        ("machhar bahut hain, dengue ka darr hai", "Mosquito menace, dengue risk", 4),
        ("paani rukahua hai, kaafi din se nikaaala nahi", "Stagnant water not cleared for days", 4),
        ("khaane wala bahut ganda hai, log beemar pad rahe hain", "Unhygienic food vendor, people falling ill", 4),
        ("sewer overflow contaminating drinking water source", "Sewage contamination near water source", 5),
        ("hospital waste dumped in open near service lane", "Hospital waste dumped openly", 5),
        ("food stall near CP metro is visibly unhygienic", "Unhygienic food stall", 3),
    ],
    "encroachment": [
        ("footpath pe thela wala kaam kar raha hai, log nahi chal sakte", "Vendor blocking footpath", 3),
        ("illegal parking blocking entire service lane", "Illegal parking blocking lane", 3),
        ("shop has extended structure onto public footpath", "Shop encroachment on footpath", 3),
        ("billboard illegally installed on public property", "Illegal billboard", 2),
        ("construction material stored on road for 2 weeks", "Road blocked by construction material", 4),
    ],
    "safety": [
        ("purani imarat khatarnak lag rahi hai, girne wali hai", "Old building looks dangerous, collapse risk", 5),
        ("ped bahut jhuk gaya hai, toota to car ke upar giregi", "Dangerously tilted tree may fall on cars", 5),
        ("aawara kutton ka jhund hai, logon ko kaat raha hai", "Stray dog pack attacking people", 5),
        ("missing manhole cover on busy road near G Block", "Missing manhole cover", 5),
        ("gas leak smell near Connaught Lane underground", "Gas leak near underground area", 5),
    ],
    "civic": [
        ("janam praman patra 3 mahine se nahi mila", "Birth certificate not received in 3 months", 3),
        ("property tax objection pending since 6 months", "Property tax dispute unresolved", 3),
        ("park gate broken, anti-social elements entering at night", "Broken park gate, security concern", 3),
        ("public toilet near Central Park is always locked", "Public toilet locked and inaccessible", 3),
        ("trade licence renewal pending for 2 months", "Trade licence delay", 3),
    ],
}

STATUS_WEIGHTS = ["open", "open", "open", "assigned", "assigned", "in_progress", "resolved", "resolved"]

complaints = []
comp_id = 1

for day_offset in range(90):
    dt_base = THREE_MO + timedelta(days=day_offset)
    # More complaints during monsoon season simulation (days 0–30 = Dec-Jan here, but let's vary)
    n_today = random.randint(4, 18)

    for _ in range(n_today):
        ctype    = random.choices(
            list(COMPLAINT_TEMPLATES.keys()),
            weights=[22, 20, 15, 15, 10, 8, 6, 4], k=1
        )[0]
        tmpl     = random.choice(COMPLAINT_TEMPLATES[ctype])
        hindi, english, severity_base = tmpl
        severity = min(5, severity_base + random.choice([-1, 0, 0, 1]))

        loc_name, (base_lat, base_lng) = random.choice(location_names)
        lat, lng = jitter(base_lat, base_lng)
        zone     = random.choice(ZONE_ASSIGN)

        filed_at = dt_base + timedelta(
            hours=random.randint(7, 22),
            minutes=random.randint(0, 59)
        )
        status   = random.choice(STATUS_WEIGHTS)
        officer  = random.choice(officers)

        resolved_at    = None
        resolution_days = None
        confirmed      = False

        if status == "resolved":
            res_delta       = timedelta(days=max(1, round(random.gauss(officer["avg_resolution_days"], 3))))
            resolved_at     = filed_at + res_delta
            resolution_days = res_delta.days
            confirmed       = random.random() < officer["citizen_confirmation_rate"]

        grief_base = severity * 8 + random.randint(0, 20)
        if zone == "service_lanes":
            grief_base = int(grief_base * 2.0)

        complaints.append({
            "id":                  f"CMP-{comp_id:05d}",
            "type":                ctype,
            "subtype":             english.split(",")[0].strip(),
            "text_hindi":          hindi,
            "text_english":        english,
            "severity":            severity,
            "status":              status,
            "ward_id":             "WARD-CP-01",
            "zone_type":           zone,
            "lat":                 lat,
            "lng":                 lng,
            "location_name":       loc_name,
            "filed_at":            ts(filed_at),
            "assigned_officer_id": officer["id"],
            "resolved_at":         ts(resolved_at) if resolved_at else None,
            "resolution_days":     resolution_days,
            "citizen_confirmed":   confirmed,
            "grief_score":         grief_base if status != "resolved" else 0,
            "infrastructure_node_hint": random.choice([n["id"] for n in nodes if n["type"] == {
                "drainage": "drain", "roads": "road", "electricity": "transformer",
                "waste": "garbage_zone", "health": "sewer_main",
            }.get(ctype, "road")]),
        })
        comp_id += 1

# ─── Demo story cluster: 8 drain complaints near Rajiv Chowk, filed over last 6 days ───
demo_dates = [NOW - timedelta(days=d, hours=random.randint(0, 12)) for d in [6, 5, 5, 4, 3, 2, 1, 0]]
demo_texts = [
    ("Rajiv Chowk ke paas naali band hai, paani sadak pe aa raha hai",    "Drain blocked near Rajiv Chowk, water on road"),
    ("outer circle drain overflow ho raha hai",                            "Outer circle drain overflow"),
    ("manhole khula hua hai near barakhamba road, koi gir sakta hai",      "Open manhole near Barakhamba road, fall risk"),
    ("naali se bahut buri boo aa rahi hai, market mein dikkat ho rahi hai","Foul smell from drain affecting market"),
    ("gutter choke hai, 5 din se paani khada hai footpath pe",             "Gutter choked, water standing on footpath for 5 days"),
    ("drain overflow ne road tod di near CP outer circle",                 "Drain overflow damaging road surface"),
    ("bijli ka transformaer paas mein hai, paani bahut khatarnak hai",     "Water near transformer, very dangerous"),
    ("ek aur naali band, ab road pe bhi gadhhe ho gaye hain",              "Another blocked drain, now potholes forming on road"),
]
for i, (filed_at, (hindi, english)) in enumerate(zip(demo_dates, demo_texts)):
    lat, lng = jitter(28.6341, 77.2195, radius_m=100)
    complaints.append({
        "id":                  f"CMP-DEMO-{i+1:02d}",
        "type":                "drainage",
        "subtype":             "blocked drain",
        "text_hindi":          hindi,
        "text_english":        english,
        "severity":            5,
        "status":              "open" if i < 6 else "assigned",
        "ward_id":             "WARD-CP-01",
        "zone_type":           "outer_roads",
        "lat":                 lat,
        "lng":                 lng,
        "location_name":       "Rajiv Chowk / Outer Circle NE",
        "filed_at":            ts(filed_at),
        "assigned_officer_id": "OFF-001",
        "resolved_at":         None,
        "resolution_days":     None,
        "citizen_confirmed":   False,
        "grief_score":         120 + i * 35,   # escalating grief
        "infrastructure_node_hint": "NODE-001",
        "is_demo_cluster":     True,
    })


# ─────────────────────────────────────────
# 5. HISTORICAL CASES (3 memorable cases)
# ─────────────────────────────────────────

historical_cases = [
    {
        "id":          "HIST-001",
        "title":       "Rajiv Chowk Drain Overflow — July 2022",
        "description": "Recurring storm drain overflow at Outer Circle NE corner causing road damage and transformer risk.",
        "root_cause":  "Primary storm drain SD-RC-04 had not been desilted for 22 months. Blockage caused cascading overflow into road foundation, weakening subgrade near Barakhamba transformer vault.",
        "start_date":  ts(datetime(2022, 7, 3)),
        "resolved_date": ts(datetime(2022, 7, 19)),
        "resolution_days": 16,
        "contractor":  "Mehta Infrastructure Pvt Ltd",
        "complaint_count": 11,
        "departments": ["drainage", "roads", "electricity"],
        "zone":        "outer_roads",
        "lat_center":  28.6341,
        "lng_center":  77.2200,
        "fingerprint_vector_hint": "high_velocity_spatial_cluster + seasonal_monsoon + drain_road_transformer_chain",
        "similarity_to_current":   0.82,
        "outcome":     "Desilting of SD-RC-04 + road patching + transformer inspection. No recurrence for 14 months.",
        "lesson":      "Desilting cycle must be completed before June 15 every year for outer circle drains.",
        "ward_id":     "WARD-CP-01",
    },
    {
        "id":          "HIST-002",
        "title":       "Palika Bazaar Transformer Chain Failure — November 2023",
        "description": "Three consecutive transformer failures in 9 days affecting the Palika Bazaar underground market and adjacent street lighting.",
        "root_cause":  "Water ingress from cracked road surface above underground cable conduit. Original road repair in Aug 2023 by subcontractor did not seal conduit entry points.",
        "start_date":  ts(datetime(2023, 11, 1)),
        "resolved_date": ts(datetime(2023, 11, 24)),
        "resolution_days": 23,
        "contractor":  "Singh Electricals (subcontractor: Kapur Road Works)",
        "complaint_count": 19,
        "departments": ["electricity", "roads"],
        "zone":        "inner_circle",
        "lat_center":  28.6317,
        "lng_center":  77.2173,
        "fingerprint_vector_hint": "road_water_ingress + transformer_cascade + underground_infrastructure",
        "similarity_to_current":   0.61,
        "outcome":     "All three transformers replaced. Cable conduit resealed. Road surface redone with proper conduit protection.",
        "lesson":      "Any road repair above underground electrical infrastructure requires electrical dept sign-off before closure.",
        "ward_id":     "WARD-CP-01",
    },
    {
        "id":          "HIST-003",
        "title":       "Janpath Service Lane Sanitation Collapse — March 2024",
        "description": "Garbage not collected from Janpath service lane for 11 consecutive days leading to disease vector complaints and stray dog surge.",
        "root_cause":  "Vehicle breakdown combined with route reassignment after staff transfer. No backup protocol. Complaints were filed but routed to wrong sub-department (construction wing instead of SWM).",
        "start_date":  ts(datetime(2024, 3, 4)),
        "resolved_date": ts(datetime(2024, 3, 18)),
        "resolution_days": 14,
        "contractor":  "MCD Sanitation Zone 4",
        "complaint_count": 27,
        "departments": ["waste", "health"],
        "zone":        "service_lanes",
        "lat_center":  28.6270,
        "lng_center":  77.2189,
        "fingerprint_vector_hint": "missed_collection_velocity + health_vector_escalation + misrouting",
        "similarity_to_current":   0.74,
        "outcome":     "Emergency collection deployed day 12. Routing error flagged. Service lane added to priority watch list.",
        "lesson":      "Service lane waste complaints must go directly to SWM. Misrouting to construction wing is a known failure mode.",
        "ward_id":     "WARD-CP-01",
    },
]


# ─────────────────────────────────────────
# 6. TRUST LEDGER — SEED ENTRIES
# ─────────────────────────────────────────

ledger_entries = []
prev_hash = "0000000000000000"

def make_ledger_entry(action_type, actor_id, entity_id, metadata, timestamp):
    global prev_hash
    payload = json.dumps({
        "action_type": action_type,
        "actor_id":    actor_id,
        "entity_id":   entity_id,
        "metadata":    metadata,
        "timestamp":   ts(timestamp),
        "prev_hash":   prev_hash,
    }, sort_keys=True)
    new_hash = hashlib.sha256(payload.encode()).hexdigest()
    entry = {
        "id":          f"LEDGER-{len(ledger_entries)+1:06d}",
        "action_type": action_type,
        "actor_id":    actor_id,
        "entity_id":   entity_id,
        "metadata":    metadata,
        "timestamp":   ts(timestamp),
        "prev_hash":   prev_hash,
        "entry_hash":  new_hash,
    }
    prev_hash = new_hash
    ledger_entries.append(entry)

# Seed ~60 ledger entries from historical complaint lifecycle
sample_complaints = random.sample([c for c in complaints if c["status"] == "resolved"], 30)
for c in sample_complaints:
    filed  = datetime.fromisoformat(c["filed_at"])
    make_ledger_entry("complaint_filed",    c.get("id","?"),            c["id"], {"type": c["type"], "severity": c["severity"]}, filed)
    make_ledger_entry("complaint_assigned", c.get("assigned_officer_id","?"), c["id"], {"officer": c["assigned_officer_id"]},         filed + timedelta(hours=random.randint(1,8)))
    if c["resolved_at"]:
        resolved = datetime.fromisoformat(c["resolved_at"])
        make_ledger_entry("complaint_resolved", c["assigned_officer_id"], c["id"], {"resolution_days": c["resolution_days"]}, resolved)
        if c["citizen_confirmed"]:
            make_ledger_entry("citizen_confirmed", "CITIZEN",             c["id"], {"confirmed": True}, resolved + timedelta(hours=random.randint(2, 48)))

# Demo cluster ledger entries
for i in range(1, 6):
    cid   = f"CMP-DEMO-{i:02d}"
    filed = datetime.fromisoformat(next(c["filed_at"] for c in complaints if c["id"] == cid))
    make_ledger_entry("complaint_filed", "CITIZEN", cid, {"demo_cluster": True, "severity": 5}, filed)

make_ledger_entry("moral_alert_sent",     "SYSTEM",   "CMP-DEMO-CLUSTER", {"grief_score": 520, "threshold": "CRITICAL"}, NOW - timedelta(hours=6))
make_ledger_entry("cluster_detected",     "SYSTEM",   "CLUSTER-CP-2026-001", {"size": 8, "type": "drainage", "historical_match": "HIST-001", "similarity": 0.82}, NOW - timedelta(hours=5))


# ─────────────────────────────────────────
# 7. WARD TRUST SCORE HISTORY (12 weeks)
# ─────────────────────────────────────────

trust_history = []
for week in range(12):
    week_date = NOW - timedelta(weeks=11 - week)
    # Scores drift realistically over time
    trust_history.append({
        "week":                  week + 1,
        "date":                  ts(week_date),
        "ward_id":               "WARD-CP-01",
        "total_score":           round(random.gauss(58 + week * 1.2, 4), 1),
        "resolution_authenticity": round(random.gauss(11 + week * 0.3, 1.5), 1),
        "proactive_action_rate": round(random.gauss(9 + week * 0.2, 1.2), 1),
        "recurrence_prevention": round(random.gauss(12 + week * 0.15, 1.0), 1),
        "response_equity":       round(random.gauss(10 + week * 0.2, 2.0), 1),
        "moral_alert_response":  round(random.gauss(10 + week * 0.25, 1.5), 1),
    })
    # Clamp all subscores 0-20
    for key in ["resolution_authenticity","proactive_action_rate","recurrence_prevention","response_equity","moral_alert_response"]:
        trust_history[-1][key] = round(max(0, min(20, trust_history[-1][key])), 1)

# ─── Equity Map: resolution time by zone ───
equity_map = [
    {"zone_type": "inner_circle",  "income_proxy": "high",   "avg_resolution_days": 4.1,  "complaint_count": 180, "ward_id": "WARD-CP-01"},
    {"zone_type": "middle_ring",   "income_proxy": "medium", "avg_resolution_days": 6.8,  "complaint_count": 220, "ward_id": "WARD-CP-01"},
    {"zone_type": "outer_roads",   "income_proxy": "medium", "avg_resolution_days": 8.3,  "complaint_count": 310, "ward_id": "WARD-CP-01"},
    {"zone_type": "service_lanes", "income_proxy": "low",    "avg_resolution_days": 17.4, "complaint_count": 190, "ward_id": "WARD-CP-01"},
]

# ─────────────────────────────────────────
# 8. STRIKE LIST (pre-generated for demo)
# ─────────────────────────────────────────

strike_list = [
    {
        "rank": 1,
        "node_id": "NODE-001",
        "node_name": "Storm Drain — Rajiv Chowk N",
        "type": "drain",
        "predicted_failure_probability": 0.91,
        "predicted_surge_days": 3,
        "signals_firing": ["complaint_acceleration", "low_health_score", "no_maintenance_310d", "rain_forecast_72h"],
        "confidence_tier": "HIGH",
        "recommended_action": "Emergency desilt inspection — assign within 24 hours",
        "affected_population_est": 18000,
        "sensitive_zones_nearby": ["Rajiv Chowk Metro Station", "Outer Circle Market"],
        "historical_match": "HIST-001",
        "lat": 28.6341, "lng": 77.2195,
    },
    {
        "rank": 2,
        "node_id": "NODE-024",
        "node_name": "Road Segment — Outer Circle NE",
        "type": "road",
        "predicted_failure_probability": 0.74,
        "predicted_surge_days": 5,
        "signals_firing": ["cascade_from_NODE-001", "health_score_worsening", "rain_forecast_72h"],
        "confidence_tier": "HIGH",
        "recommended_action": "Road inspection for subgrade integrity — inspect if NODE-001 confirmed",
        "affected_population_est": 12000,
        "sensitive_zones_nearby": ["Barakhamba Metro", "Connaught Place outer market"],
        "lat": 28.6352, "lng": 77.2208,
    },
    {
        "rank": 3,
        "node_id": "NODE-048",
        "node_name": "Transformer — Barakhamba Rd Junction",
        "type": "transformer",
        "predicted_failure_probability": 0.51,
        "predicted_surge_days": 9,
        "signals_firing": ["cascade_from_NODE-024", "water_exposure_risk"],
        "confidence_tier": "MEDIUM",
        "recommended_action": "Electrical inspection to check conduit waterproofing",
        "affected_population_est": 8000,
        "sensitive_zones_nearby": ["Barakhamba offices", "Underground market power supply"],
        "lat": 28.6345, "lng": 77.2228,
    },
    {
        "rank": 4,
        "node_id": random.choice([n["id"] for n in nodes if n["type"] == "sewer_main"]),
        "node_name": "Sewer Main — Janpath Service Lane",
        "type": "sewer_main",
        "predicted_failure_probability": 0.63,
        "predicted_surge_days": 6,
        "signals_firing": ["complaint_velocity_rising", "age_years_high"],
        "confidence_tier": "MEDIUM",
        "recommended_action": "CCTV inspection of sewer line — schedule within 3 days",
        "affected_population_est": 9500,
        "sensitive_zones_nearby": ["Janpath Market", "Service lane residences"],
        "lat": 28.6270, "lng": 77.2189,
    },
    {
        "rank": 5,
        "node_id": random.choice([n["id"] for n in nodes if n["type"] == "garbage_zone"]),
        "node_name": "Garbage Zone — Palika Bazaar Service Exit",
        "type": "garbage_zone",
        "predicted_failure_probability": 0.55,
        "predicted_surge_days": 4,
        "signals_firing": ["collection_miss_pattern", "seasonal_heat"],
        "confidence_tier": "MEDIUM",
        "recommended_action": "Verify collection schedule adherence — check last 7 days logs",
        "affected_population_est": 6000,
        "sensitive_zones_nearby": ["Palika Bazaar underground market"],
        "lat": 28.6305, "lng": 77.2162,
    },
]


# ─────────────────────────────────────────
# WRITE ALL JSON FILES
# ─────────────────────────────────────────

datasets = {
    "nodes":            nodes,
    "edges":            edges,
    "officers":         officers,
    "routing_outcomes": routing_outcomes,
    "complaints":       complaints,
    "historical_cases": historical_cases,
    "trust_ledger":     ledger_entries,
    "trust_history":    trust_history,
    "equity_map":       equity_map,
    "strike_list":      strike_list,
}

for name, data in datasets.items():
    path = f"data/{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓  {path:<35} {len(data):>5} records")

# Summary
print("\n─── SUMMARY ───────────────────────────────")
print(f"  Infrastructure nodes  : {len(nodes)}")
print(f"  Graph edges           : {len(edges)}")
print(f"  Officers              : {len(officers)}")
print(f"  Routing outcomes      : {len(routing_outcomes)}")
print(f"  Complaints (3 months) : {len(complaints)}  (incl. {sum(1 for c in complaints if c.get('is_demo_cluster'))} demo-cluster)")
print(f"  Historical cases      : {len(historical_cases)}")
print(f"  Trust ledger entries  : {len(ledger_entries)}")
print(f"  Trust score history   : {len(trust_history)} weeks")
print(f"  Strike list items     : {len(strike_list)}")
print("\nAll files written to ./data/")
print("Run: python generate_data.py")
