"""
Leadway Assurance — Householder Insurance Rate Tables
Official rates as approved by underwriting.
"""

# ─── INDIVIDUAL / RETAIL RATES ────────────────────────────────────────────────
INDIVIDUAL_RATES = {
    "building":               0.001,     # 0.10%
    "content":                0.002,     # 0.20%
    "accidental_damage":      0.00125,   # 0.125%
    "all_risks":              0.02,      # 2.0% of 10% content SI
    "personal_accident":      0.00185,   # 0.185%
    "alternative_accommodation": 0.002,  # 0.20%
}

# ─── CORPORATE / COMMERCIAL RATE BANDS ────────────────────────────────────────
CORPORATE_BANDS = {
    1: {"building": 0.00125, "content": 0.003},
    2: {"building": 0.0015,  "content": 0.0035},
    3: {"building": 0.00175, "content": 0.0045},
    4: {"building": 0.00185, "content": 0.005},
}

# Corporate additional coverages use same rates as Individual
CORPORATE_ADDITIONAL_RATES = {
    "accidental_damage":      0.00125,
    "all_risks":              0.02,
    "personal_accident":      0.00185,
    "alternative_accommodation": 0.002,
}

# ─── COVER TYPE → BAND MAPPING ────────────────────────────────────────────────
COVER_TYPE_BAND = {
    "Basic":    1,
    "Bronze":   1,
    "Silver":   2,
    "Standard": 2,
    "Gold":     3,
    "Platinum": 4,
}

# What each cover type includes
COVER_TYPE_INCLUSIONS = {
    "Basic": {
        "building": True,
        "content": False,
        "accidental_damage": False,
        "all_risks": False,
        "personal_accident": False,
        "alternative_accommodation": False,
    },
    "Bronze": {
        "building": True,
        "content": True,
        "accidental_damage": False,
        "all_risks": False,
        "personal_accident": False,
        "alternative_accommodation": False,
    },
    "Silver": {
        "building": True,
        "content": True,
        "accidental_damage": True,
        "all_risks": False,
        "personal_accident": False,
        "alternative_accommodation": False,
    },
    "Standard": {
        "building": True,
        "content": True,
        "accidental_damage": False,
        "all_risks": False,
        "personal_accident": False,
        "alternative_accommodation": False,
    },
    "Gold": {
        "building": True,
        "content": True,
        "accidental_damage": True,
        "all_risks": True,
        "personal_accident": True,
        "alternative_accommodation": False,
    },
    "Platinum": {
        "building": True,
        "content": True,
        "accidental_damage": True,
        "all_risks": True,
        "personal_accident": True,
        "alternative_accommodation": True,
    },
}

# ─── LOCATION FACTORS ─────────────────────────────────────────────────────────
LOCATION_FACTORS = {
    "Lagos":         0.15,
    "Port Harcourt": 0.10,
    "Abuja":         0.05,
    "Ibadan":        -0.05,
    "Kaduna":        -0.10,
    "Other":         0.00,
}

# ─── BUILDING AGE LOADINGS ────────────────────────────────────────────────────
def building_age_loading(age: int) -> float:
    if age <= 5:
        return 0.00
    elif age <= 15:
        return 0.05
    elif age <= 30:
        return 0.10
    else:
        return 0.20

# ─── CLAIMS HISTORY LOADING ───────────────────────────────────────────────────
CLAIMS_LOADING = {
    0: 0.00,
    1: 0.10,
    2: 0.25,
    3: 0.50,
    4: 0.75,  # cap at 75%
}

def claims_history_loading(claims: int) -> float:
    return CLAIMS_LOADING.get(min(claims, 4), 0.75)

# ─── DISCOUNT RATES ───────────────────────────────────────────────────────────
SECURITY_SYSTEM_DISCOUNT    = 0.05   # 5%
FIRE_EXTINGUISHER_DISCOUNT  = 0.03   # 3%

# ─── VOLUME DISCOUNTS ─────────────────────────────────────────────────────────
def volume_discount_individual(total_si: float) -> float:
    if total_si >= 100_000_000:
        return 0.05
    elif total_si >= 50_000_000:
        return 0.03
    return 0.00

def volume_discount_corporate(total_si: float) -> float:
    if total_si >= 1_000_000_000:
        return 0.10
    elif total_si >= 500_000_000:
        return 0.07
    elif total_si >= 100_000_000:
        return 0.04
    return 0.00

# ─── MINIMUM PREMIUMS ─────────────────────────────────────────────────────────
MIN_PREMIUM_INDIVIDUAL = 5_000.0
MIN_PREMIUM_CORPORATE  = 25_000.0

# ─── COMMISSION ───────────────────────────────────────────────────────────────
COMMISSION_RATE = 0.15   # 15%

# ─── SHORT PERIOD LOADING ─────────────────────────────────────────────────────
SHORT_PERIOD_LOADING = 0.15  # 15% extra on pro-rata if < 12 months
