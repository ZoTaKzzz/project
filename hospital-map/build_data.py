#!/usr/bin/env python3
"""
Build the enriched hospital JSON from CMS CSV + GeoJSON sources.
Includes ALL hospitals: CMS-verified and GeoJSON-only.
Adds: regions, health system grouping, prospect scores, care type inference.
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict

CMS_CSV = "/home/ubuntu/attachments/1cb1bd41-857c-47a6-b827-7ba499b8d0c1/Hospital_General_Information.csv"
GEOJSON = "/tmp/geojson/hospitals-3-geojson.geojson"
OUTPUT = "/home/ubuntu/repos/project/hospital-map/hospitals_all.json"

REGIONS = {
    "Northeast": ["ME","NH","VT","MA","RI","CT","NY","NJ","PA"],
    "Southeast": ["VA","WV","NC","SC","GA","FL","AL","MS","TN","KY"],
    "Midwest": ["OH","MI","IN","IL","WI","MN","IA","MO","KS","NE","ND","SD"],
    "Southwest": ["TX","OK","AR","LA","NM"],
    "West": ["CO","WY","MT","ID","UT","NV","AZ","WA","OR","CA","AK","HI"],
    "Mid-Atlantic": ["MD","DE","DC"],
}
STATE_TO_REGION = {}
for region, states in REGIONS.items():
    for st in states:
        STATE_TO_REGION[st] = region

# CMS Hospital Type -> care type inference
# Acute Care, Critical Access, Children's = likely inpatient
# Psychiatric, Long-term = inpatient
# Rural Emergency = could be outpatient
INPATIENT_TYPES = {
    "Acute Care Hospitals", "Critical Access Hospitals", "Childrens",
    "Psychiatric", "Long-term", "Acute Care - Veterans Administration",
    "Acute Care - Department of Defense"
}
OUTPATIENT_TYPES = {"Rural Emergency Hospital"}

# Ownership mapping from CMS to simplified categories
OWNERSHIP_MAP = {
    "Voluntary non-profit - Private": "Nonprofit",
    "Voluntary non-profit - Church": "Nonprofit",
    "Voluntary non-profit - Other": "Nonprofit",
    "Proprietary": "For-Profit",
    "Government - Hospital District or Authority": "Government",
    "Government - Local": "Government",
    "Government - State": "Government",
    "Government - Federal": "Government",
    "Department of Defense": "Government",
    "Veterans Health Administration": "Government",
    "Tribal": "Government",
    "Physician": "For-Profit",
}

def normalize(name):
    n = name.upper().strip()
    n = re.sub(r'[^A-Z0-9\s]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def make_words(name):
    return set(normalize(name).split())

def infer_health_system(name):
    """Infer health system from hospital name patterns."""
    n = name.upper()
    systems = [
        ("HCA", ["HCA", "HOSPITAL CORPORATION"]),
        ("CommonSpirit Health", ["COMMONSPIRIT", "CHI ", "CATHOLIC HEALTH", "DIGNITY HEALTH", "ST. JOSEPH", "ST JOSEPH"]),
        ("Ascension", ["ASCENSION", "ST. VINCENT", "ST VINCENT"]),
        ("Trinity Health", ["TRINITY HEALTH", "MERCY HEALTH", "SAINT JOSEPH MERCY"]),
        ("Tenet Healthcare", ["TENET"]),
        ("Community Health Systems", ["COMMUNITY HEALTH SYSTEM"]),
        ("Universal Health Services", ["UHS ", "UNIVERSAL HEALTH"]),
        ("Encompass Health", ["ENCOMPASS HEALTH"]),
        ("Kindred Healthcare", ["KINDRED"]),
        ("LifePoint Health", ["LIFEPOINT"]),
        ("Providence", ["PROVIDENCE"]),
        ("Adventist Health", ["ADVENTIST HEALTH", "ADVENTHEALTH"]),
        ("Banner Health", ["BANNER HEALTH", "BANNER "]),
        ("Atrium Health", ["ATRIUM HEALTH"]),
        ("Baylor Scott & White", ["BAYLOR SCOTT", "BAYLOR "]),
        ("Intermountain", ["INTERMOUNTAIN"]),
        ("Kaiser Permanente", ["KAISER"]),
        ("Mayo Clinic", ["MAYO CLINIC"]),
        ("Cleveland Clinic", ["CLEVELAND CLINIC"]),
        ("Novant Health", ["NOVANT"]),
        ("Ochsner Health", ["OCHSNER"]),
        ("Prisma Health", ["PRISMA"]),
        ("Spectrum Health", ["SPECTRUM HEALTH"]),
        ("SSM Health", ["SSM HEALTH"]),
        ("WellStar", ["WELLSTAR"]),
        ("Memorial Hermann", ["MEMORIAL HERMANN"]),
        ("Northwell Health", ["NORTHWELL"]),
        ("NYU Langone", ["NYU LANGONE"]),
        ("Mount Sinai", ["MOUNT SINAI", "MT SINAI"]),
        ("Cedars-Sinai", ["CEDARS-SINAI", "CEDARS SINAI"]),
        ("Sutter Health", ["SUTTER HEALTH", "SUTTER "]),
        ("UPMC", ["UPMC"]),
        ("Geisinger", ["GEISINGER"]),
        ("Mass General Brigham", ["MASS GENERAL", "BRIGHAM"]),
        ("Sentara", ["SENTARA"]),
        ("Bon Secours Mercy", ["BON SECOURS", "MERCY HEALTH"]),
        ("Baptist Health", ["BAPTIST HEALTH", "BAPTIST MEDICAL"]),
        ("Piedmont Healthcare", ["PIEDMONT"]),
        ("ChristianaCare", ["CHRISTIANACARE", "CHRISTIANA"]),
        ("Hackensack Meridian", ["HACKENSACK"]),
        ("MedStar Health", ["MEDSTAR"]),
        ("OhioHealth", ["OHIOHEALTH"]),
        ("ProMedica", ["PROMEDICA"]),
        ("Sanford Health", ["SANFORD HEALTH", "SANFORD "]),
        ("Essentia Health", ["ESSENTIA"]),
        ("Froedtert", ["FROEDTERT"]),
        ("Gundersen", ["GUNDERSEN"]),
        ("Marshfield Clinic", ["MARSHFIELD"]),
        ("VA Medical Center", ["VA MEDICAL CENTER", "VETERANS AFFAIRS", "VA HEALTH"]),
    ]
    for system_name, patterns in systems:
        for pattern in patterns:
            if pattern in n:
                return system_name
    return "Independent"

def compute_prospect_score(hospital):
    """Compute a prospect score from 1-100 based on UShift integration criteria."""
    score = 35  # base - lower to create better spread

    # Health system size factor (biggest differentiator: 0-25 points)
    sys_size = hospital.get("systemSize", 0)
    if sys_size == 0:  # Independent - best target
        score += 25
    elif sys_size <= 5:
        score += 20
    elif sys_size <= 10:
        score += 15
    elif sys_size <= 20:
        score += 10
    elif sys_size <= 30:
        score += 0
    else:  # 30+ massive systems
        score -= 15

    # Care type factor (0-10 points)
    care = hospital.get("careType", "Unknown")
    if care == "Inpatient":
        score += 10
    elif care == "Both":
        score += 5
    # Outpatient gets 0

    # Bed count factor - sweet spot is 50-500 (0-15 points)
    beds = hospital.get("beds", 0)
    if 101 <= beds <= 250:
        score += 15  # ideal mid-size
    elif 51 <= beds <= 100:
        score += 12
    elif 251 <= beds <= 500:
        score += 10
    elif 25 <= beds <= 50:
        score += 5
    elif beds > 500:
        score -= 5  # too large/complex
    elif beds <= 0:
        score -= 10  # no bed data = uncertain

    # Ownership factor (0-8 points)
    own = hospital.get("ownershipCategory", "")
    if own == "For-Profit":
        score += 8  # more likely to buy software
    elif own == "Nonprofit":
        score += 5
    elif own == "Government":
        score -= 5  # procurement hurdles

    # Emergency services = operational complexity = bigger staffing needs
    if hospital.get("emergencyServices") == "Yes":
        score += 5

    # CMS type bonus
    cms_type = hospital.get("cmsType", "")
    if cms_type == "Acute Care Hospitals":
        score += 3
    elif cms_type == "Critical Access Hospitals":
        score += 5  # rural, likely less tech, good target

    return max(1, min(100, score))


# GeoJSON TYPE -> CMS-equivalent type mapping
GEO_TYPE_MAP = {
    "GENERAL ACUTE CARE": "Acute Care Hospitals",
    "CRITICAL ACCESS": "Critical Access Hospitals",
    "CHILDREN": "Childrens",
    "PSYCHIATRIC": "Psychiatric",
    "LONG TERM CARE": "Long-term",
    "MILITARY": "Acute Care - Department of Defense",
    "REHABILITATION": "Rehabilitation",
    "CHRONIC DISEASE": "Chronic Disease",
    "SPECIAL": "Special",
    "WOMEN": "Women",
}

# GeoJSON OWNER -> ownership category mapping
GEO_OWNER_MAP = {
    "NON-PROFIT": ("Voluntary non-profit - Private", "Nonprofit"),
    "PROPRIETARY": ("Proprietary", "For-Profit"),
    "GOVERNMENT - DISTRICT/AUTHORITY": ("Government - Hospital District or Authority", "Government"),
    "GOVERNMENT - FEDERAL": ("Government - Federal", "Government"),
    "GOVERNMENT - LOCAL": ("Government - Local", "Government"),
    "GOVERNMENT - STATE": ("Government - State", "Government"),
}


def main():
    # Load GeoJSON
    with open(GEOJSON) as f:
        geo = json.load(f)
    features = geo["features"]

    # Build GeoJSON lookups
    geo_by_name_state = {}
    geo_by_zip = {}
    geo_by_addr_city_state = {}
    matched_geo_ids = set()  # Track which GeoJSON features get matched to CMS
    for feat in features:
        p = feat["properties"]
        key1 = (normalize(p["NAME"]), p["STATE"])
        geo_by_name_state[key1] = feat

        z = p.get("ZIP", "")[:5]
        if z:
            geo_by_zip.setdefault(z, []).append(feat)

        addr_norm = normalize(p.get("ADDRESS", "").split(",")[0])
        city = p.get("CITY", "").upper().strip()
        key2 = (addr_norm, city, p["STATE"])
        geo_by_addr_city_state[key2] = feat

    # Load CMS CSV
    with open(CMS_CSV) as f:
        cms_rows = list(csv.DictReader(f))

    print(f"CMS records: {len(cms_rows)}")
    print(f"GeoJSON features: {len(features)}")

    # ---- Phase 1: Process CMS hospitals, match to GeoJSON for coordinates ----
    hospitals = []
    cms_matched = 0
    cms_no_coords = 0
    for r in cms_rows:
        state = r["State"].upper().strip()
        name_norm = normalize(r["Facility Name"])
        lat, lng = None, None
        geo_extra = {}
        matched_feat = None

        # Try exact name+state
        if (name_norm, state) in geo_by_name_state:
            matched_feat = geo_by_name_state[(name_norm, state)]
        else:
            # Try address+city+state
            addr = normalize(r["Address"].split(",")[0])
            city = r["City/Town"].upper().strip()
            if (addr, city, state) in geo_by_addr_city_state:
                matched_feat = geo_by_addr_city_state[(addr, city, state)]
            else:
                # Try ZIP code with name word overlap
                z = r["ZIP Code"][:5]
                if z in geo_by_zip:
                    cms_words = make_words(r["Facility Name"])
                    best_overlap = 0
                    best_feat = None
                    for gf in geo_by_zip[z]:
                        geo_words = make_words(gf["properties"]["NAME"])
                        overlap = len(cms_words & geo_words)
                        if overlap > best_overlap:
                            best_overlap = overlap
                            best_feat = gf
                    if best_overlap >= 2 and best_feat:
                        matched_feat = best_feat

        if matched_feat:
            lat = matched_feat["properties"]["LATITUDE"]
            lng = matched_feat["properties"]["LONGITUDE"]
            geo_extra = matched_feat["properties"]
            matched_geo_ids.add(matched_feat["properties"]["OBJECTID"])
            cms_matched += 1

        # Skip CMS hospitals without coordinates (can't place on map)
        if lat is None or lng is None:
            cms_no_coords += 1
            continue

        ccn = r["Facility ID"].strip()
        beds_val = geo_extra.get("BEDS", -999)
        if isinstance(beds_val, str):
            try:
                beds_val = int(beds_val)
            except ValueError:
                beds_val = 0
        if beds_val < 0:
            beds_val = 0

        cms_type = r["Hospital Type"].strip()
        care_type = "Inpatient" if cms_type in INPATIENT_TYPES else ("Outpatient" if cms_type in OUTPATIENT_TYPES else "Both")

        ownership_raw = r["Hospital Ownership"].strip()
        ownership_cat = OWNERSHIP_MAP.get(ownership_raw, "Other")

        health_system = infer_health_system(r["Facility Name"])

        rating = r.get("Hospital overall rating", "").strip()
        if not rating or rating == "Not Available":
            rating = None

        h = {
            "id": ccn,
            "ccn": ccn,
            "name": r["Facility Name"].strip(),
            "address": r["Address"].strip(),
            "city": r["City/Town"].strip(),
            "state": state,
            "zip": r["ZIP Code"].strip(),
            "county": (r.get("County/Parish", "").strip() or geo_extra.get("COUNTY", "").strip()),
            "phone": (r.get("Telephone Number", "").strip() or geo_extra.get("TELEPHONE", "").strip()),
            "lat": float(lat),
            "lng": float(lng),
            "cmsType": cms_type,
            "careType": care_type,
            "ownership": ownership_raw,
            "ownershipCategory": ownership_cat,
            "beds": beds_val,
            "emergencyServices": r.get("Emergency Services", "").strip(),
            "birthingFriendly": r.get("Meets criteria for birthing friendly designation", "").strip(),
            "rating": rating,
            "healthSystem": health_system,
            "systemSize": 0,
            "region": STATE_TO_REGION.get(state, "Other"),
            "website": geo_extra.get("WEBSITE", ""),
            "trauma": geo_extra.get("TRAUMA", ""),
            "helipad": geo_extra.get("HELIPAD", ""),
            "hasCMS": True,
            "prospectScore": 0,
        }
        if h["website"] == "NOT AVAILABLE":
            h["website"] = ""
        if h["trauma"] == "NOT AVAILABLE":
            h["trauma"] = ""

        hospitals.append(h)

    print(f"CMS matched with coordinates: {cms_matched}")
    print(f"CMS without coordinates (skipped): {cms_no_coords}")
    print(f"CMS hospitals included: {len(hospitals)}")

    # ---- Phase 2: Add GeoJSON-only hospitals not matched to CMS ----
    geo_only = 0
    for feat in features:
        p = feat["properties"]
        if p["OBJECTID"] in matched_geo_ids:
            continue  # already included via CMS match
        if p.get("STATUS", "").upper() != "OPEN":
            continue  # skip closed facilities

        lat = p.get("LATITUDE")
        lng = p.get("LONGITUDE")
        if lat is None or lng is None:
            continue

        state = p.get("STATE", "").upper().strip()
        geo_type = p.get("TYPE", "NOT AVAILABLE").strip()
        cms_type_equiv = GEO_TYPE_MAP.get(geo_type, geo_type)

        # Infer care type from GeoJSON TYPE
        if geo_type in ("GENERAL ACUTE CARE", "CRITICAL ACCESS", "CHILDREN", "PSYCHIATRIC", "LONG TERM CARE", "MILITARY"):
            care_type = "Inpatient"
        elif geo_type in ("REHABILITATION", "CHRONIC DISEASE", "SPECIAL", "WOMEN"):
            care_type = "Both"
        else:
            care_type = "Unknown"

        owner_raw = p.get("OWNER", "NOT AVAILABLE").strip()
        if owner_raw in GEO_OWNER_MAP:
            ownership_raw, ownership_cat = GEO_OWNER_MAP[owner_raw]
        else:
            ownership_raw = owner_raw
            ownership_cat = "Other"

        beds_val = p.get("BEDS", -999)
        if isinstance(beds_val, str):
            try:
                beds_val = int(beds_val)
            except ValueError:
                beds_val = 0
        if beds_val < 0:
            beds_val = 0

        name = p.get("NAME", "").strip()
        health_system = infer_health_system(name)

        phone = p.get("TELEPHONE", "").strip()
        if phone == "NOT AVAILABLE":
            phone = ""
        website = p.get("WEBSITE", "").strip()
        if website == "NOT AVAILABLE":
            website = ""
        trauma = p.get("TRAUMA", "").strip()
        if trauma == "NOT AVAILABLE":
            trauma = ""
        county = p.get("COUNTY", "").strip()

        addr_raw = p.get("ADDRESS", "").strip()
        # Split address at comma to get just street part
        addr_parts = addr_raw.split(",")
        address = addr_parts[0].strip()

        geo_id = f"geo_{p['OBJECTID']}"
        h = {
            "id": geo_id,
            "ccn": "",
            "name": name,
            "address": address,
            "city": p.get("CITY", "").strip(),
            "state": state,
            "zip": p.get("ZIP", "").strip(),
            "county": county,
            "phone": phone,
            "lat": float(lat),
            "lng": float(lng),
            "cmsType": cms_type_equiv,
            "careType": care_type,
            "ownership": ownership_raw,
            "ownershipCategory": ownership_cat,
            "beds": beds_val,
            "emergencyServices": "",
            "birthingFriendly": "",
            "rating": None,
            "healthSystem": health_system,
            "systemSize": 0,
            "region": STATE_TO_REGION.get(state, "Other"),
            "website": website,
            "trauma": trauma,
            "helipad": p.get("HELIPAD", ""),
            "hasCMS": False,
            "prospectScore": 0,
        }

        hospitals.append(h)
        geo_only += 1

    print(f"GeoJSON-only hospitals added: {geo_only}")
    print(f"Total hospitals: {len(hospitals)}")

    cms_count = sum(1 for h in hospitals if h["hasCMS"])
    print(f"\nCMS-verified: {cms_count}")
    print(f"GeoJSON-only: {geo_only}")

    # Compute health system sizes
    system_counts = Counter(h["healthSystem"] for h in hospitals if h["healthSystem"] != "Independent")
    for h in hospitals:
        if h["healthSystem"] == "Independent":
            h["systemSize"] = 0
        else:
            h["systemSize"] = system_counts.get(h["healthSystem"], 1)

    # Compute prospect scores
    for h in hospitals:
        h["prospectScore"] = compute_prospect_score(h)

    # Stats
    print(f"\nBy region:")
    region_counts = Counter(h["region"] for h in hospitals)
    for r, c in region_counts.most_common():
        print(f"  {r}: {c}")

    print(f"\nBy care type:")
    care_counts = Counter(h["careType"] for h in hospitals)
    for c, n in care_counts.most_common():
        print(f"  {c}: {n}")

    print(f"\nBy ownership category:")
    own_counts = Counter(h["ownershipCategory"] for h in hospitals)
    for o, n in own_counts.most_common():
        print(f"  {o}: {n}")

    print(f"\nTop health systems:")
    sys_counts_all = Counter(h["healthSystem"] for h in hospitals)
    for s, n in sys_counts_all.most_common(15):
        print(f"  {s}: {n}")

    print(f"\nProspect score distribution:")
    score_ranges = {"1-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for h in hospitals:
        s = h["prospectScore"]
        if s <= 20: score_ranges["1-20"] += 1
        elif s <= 40: score_ranges["21-40"] += 1
        elif s <= 60: score_ranges["41-60"] += 1
        elif s <= 80: score_ranges["61-80"] += 1
        else: score_ranges["81-100"] += 1
    for r, c in score_ranges.items():
        print(f"  {r}: {c}")

    # Write output
    with open(OUTPUT, "w") as f:
        json.dump(hospitals, f, separators=(",", ":"))

    size_mb = len(json.dumps(hospitals, separators=(",", ":"))) / 1024 / 1024
    print(f"\nOutput: {OUTPUT} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
