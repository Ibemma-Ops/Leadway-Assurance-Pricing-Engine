"""
Leadway Assurance — Householder Insurance Pricing Engine API
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from engine.models import RiskProfile, PremiumBreakdown
from engine.calculator import calculate_premium
from engine.rates import (
    INDIVIDUAL_RATES, CORPORATE_BANDS, COVER_TYPE_BAND,
    LOCATION_FACTORS, COMMISSION_RATE,
    MIN_PREMIUM_INDIVIDUAL, MIN_PREMIUM_CORPORATE,
)

app = FastAPI(
    title="Leadway Householder Insurance Pricing Engine",
    description="Instant premium quotes for Leadway Assurance householder policies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/quote", response_model=PremiumBreakdown, tags=["Pricing"])
async def get_quote(profile: RiskProfile):
    """
    Generate an instant premium quote for a householder insurance policy.

    Accepts a RiskProfile and returns a full PremiumBreakdown including:
    - Per-section base premiums
    - All loadings and discounts applied
    - Gross premium, commission, and net premium
    """
    # Validate segment
    if profile.segment not in ("Individual", "Corporate"):
        raise HTTPException(400, "segment must be 'Individual' or 'Corporate'")

    # Validate cover type
    valid_covers = ["Basic", "Bronze", "Silver", "Standard", "Gold", "Platinum"]
    if profile.cover_type not in valid_covers:
        raise HTTPException(400, f"cover_type must be one of {valid_covers}")

    # Validate location
    valid_locs = list(LOCATION_FACTORS.keys())
    if profile.location not in valid_locs:
        raise HTTPException(400, f"location must be one of {valid_locs}")

    # Validate sum insured
    if profile.building_si == 0 and profile.content_si == 0:
        raise HTTPException(400, "At least one of building_si or content_si must be > 0")

    try:
        breakdown = calculate_premium(profile)
        return breakdown
    except Exception as e:
        raise HTTPException(500, f"Calculation error: {str(e)}")


@app.get("/api/rates", tags=["Reference"])
async def get_rates():
    """
    Returns the full rate card — individual and corporate rates with all bands.
    """
    return {
        "individual": {
            "building":               {"rate": INDIVIDUAL_RATES["building"],     "description": "Building (Fire & Special Perils)", "applied_to": "Building SI"},
            "content":                {"rate": INDIVIDUAL_RATES["content"],      "description": "Contents (Fire, Burglary & Special Perils)", "applied_to": "Content SI"},
            "accidental_damage":      {"rate": INDIVIDUAL_RATES["accidental_damage"], "description": "Accidental Damage to Contents", "applied_to": "Content SI"},
            "all_risks":              {"rate": INDIVIDUAL_RATES["all_risks"],    "description": "All Risks Extension", "applied_to": "10% of Content SI"},
            "personal_accident":      {"rate": INDIVIDUAL_RATES["personal_accident"], "description": "Personal Accident", "applied_to": "Total SI"},
            "alternative_accommodation": {"rate": INDIVIDUAL_RATES["alternative_accommodation"], "description": "Alternative Accommodation", "applied_to": "Building SI"},
        },
        "corporate": {
            "bands": {
                "Band 1 (Basic/Bronze)":    CORPORATE_BANDS[1],
                "Band 2 (Silver/Standard)": CORPORATE_BANDS[2],
                "Band 3 (Gold)":            CORPORATE_BANDS[3],
                "Band 4 (Platinum)":        CORPORATE_BANDS[4],
            },
            "additional_coverages": "Same as individual rates",
        },
        "adjustments": {
            "location_factors": LOCATION_FACTORS,
            "building_age": {
                "0-5 years":    "0%",
                "6-15 years":   "+5%",
                "16-30 years":  "+10%",
                "30+ years":    "+20%",
            },
            "claims_history": {
                "0 claims": "0%",
                "1 claim":  "+10%",
                "2 claims": "+25%",
                "3 claims": "+50%",
                "4+ claims":"+75% (cap)",
            },
            "discounts": {
                "security_system":    "-5%",
                "fire_extinguisher":  "-3%",
            },
            "volume_discounts": {
                "individual": {"50M+ SI": "-3%", "100M+ SI": "-5%"},
                "corporate":  {"100M+ SI": "-4%", "500M+ SI": "-7%", "1B+ SI": "-10%"},
            },
        },
        "minimum_premiums": {
            "individual": MIN_PREMIUM_INDIVIDUAL,
            "corporate":  MIN_PREMIUM_CORPORATE,
        },
        "commission_rate": COMMISSION_RATE,
        "currency": "NGN",
    }


# ─── Serve Frontend ────────────────────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
