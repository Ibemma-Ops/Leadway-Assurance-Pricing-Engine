"""
Data models for the Leadway Householder Insurance Pricing Engine.
"""
from dataclasses import dataclass, field
from typing import Optional
from pydantic import BaseModel, Field


# ─── REQUEST MODEL ─────────────────────────────────────────────────────────────
class RiskProfile(BaseModel):
    # Segment
    segment: str = Field(..., description="Individual or Corporate")

    # Property
    address: str = Field(default="", description="Property address")
    location: str = Field(..., description="City: Lagos, Abuja, Port Harcourt, Ibadan, Kaduna, Other")
    building_age: int = Field(..., ge=0, description="Age of building in years")

    # Sum insured
    building_si: float = Field(default=0.0, ge=0, description="Building sum insured (NGN)")
    content_si: float = Field(default=0.0, ge=0, description="Contents sum insured (NGN)")

    # Cover type
    cover_type: str = Field(..., description="Basic / Bronze / Silver / Standard / Gold / Platinum")

    # Duration
    duration_months: int = Field(default=12, ge=1, le=12, description="Policy duration in months")

    # Risk factors
    claims_last_3_years: int = Field(default=0, ge=0, description="Number of claims in last 3 years")
    has_security_system: bool = Field(default=False)
    has_fire_extinguisher: bool = Field(default=False)

    # Optional overrides (advanced)
    override_building_rate: Optional[float] = Field(default=None)
    override_content_rate: Optional[float] = Field(default=None)


# ─── RESPONSE MODEL ────────────────────────────────────────────────────────────
class SectionPremium(BaseModel):
    section: str
    sum_insured: float
    rate: float
    base_premium: float


class AdjustmentItem(BaseModel):
    label: str
    type: str           # "loading" | "discount" | "info"
    percentage: float
    amount: float


class PremiumBreakdown(BaseModel):
    # Input echo
    segment: str
    cover_type: str
    location: str
    building_si: float
    content_si: float
    total_si: float
    duration_months: int
    band: Optional[int] = None

    # Section premiums
    sections: list[SectionPremium]
    base_premium: float

    # Adjustments
    adjustments: list[AdjustmentItem]
    total_adjustment_amount: float

    # Final premiums
    gross_premium: float
    commission_rate: float
    commission_amount: float
    net_premium: float

    # Metadata
    rate_per_mille: float   # gross premium per 1000 of total SI
    minimum_applied: bool
    currency: str = "NGN"
