"""
Leadway Householder Insurance — Premium Calculator
Implements the official calculation flow step by step.
"""
from .models import RiskProfile, PremiumBreakdown, SectionPremium, AdjustmentItem
from .rates import (
    INDIVIDUAL_RATES, CORPORATE_BANDS, CORPORATE_ADDITIONAL_RATES,
    COVER_TYPE_BAND, COVER_TYPE_INCLUSIONS,
    LOCATION_FACTORS, building_age_loading, claims_history_loading,
    SECURITY_SYSTEM_DISCOUNT, FIRE_EXTINGUISHER_DISCOUNT,
    volume_discount_individual, volume_discount_corporate,
    MIN_PREMIUM_INDIVIDUAL, MIN_PREMIUM_CORPORATE,
    COMMISSION_RATE, SHORT_PERIOD_LOADING,
)


def calculate_premium(profile: RiskProfile) -> PremiumBreakdown:
    is_corporate = profile.segment.lower() == "corporate"
    inclusions = COVER_TYPE_INCLUSIONS.get(profile.cover_type, {})
    band = COVER_TYPE_BAND.get(profile.cover_type, 1) if is_corporate else None

    sections: list[SectionPremium] = []

    # ── STEP 1: Base section premiums ─────────────────────────────────────────
    if is_corporate:
        corp_rates = CORPORATE_BANDS[band]
        building_rate = profile.override_building_rate or corp_rates["building"]
        content_rate  = profile.override_content_rate  or corp_rates["content"]
        additional_rates = CORPORATE_ADDITIONAL_RATES
    else:
        building_rate = profile.override_building_rate or INDIVIDUAL_RATES["building"]
        content_rate  = profile.override_content_rate  or INDIVIDUAL_RATES["content"]
        additional_rates = INDIVIDUAL_RATES

    # Building
    if inclusions.get("building") and profile.building_si > 0:
        bp = profile.building_si * building_rate
        sections.append(SectionPremium(
            section="Building (Fire & Special Perils)",
            sum_insured=profile.building_si,
            rate=building_rate,
            base_premium=bp,
        ))

    # Content
    if inclusions.get("content") and profile.content_si > 0:
        cp = profile.content_si * content_rate
        sections.append(SectionPremium(
            section="Contents (Fire, Burglary & Special Perils)",
            sum_insured=profile.content_si,
            rate=content_rate,
            base_premium=cp,
        ))

    # Accidental Damage
    if inclusions.get("accidental_damage") and profile.content_si > 0:
        r = additional_rates["accidental_damage"]
        ap = profile.content_si * r
        sections.append(SectionPremium(
            section="Accidental Damage to Contents",
            sum_insured=profile.content_si,
            rate=r,
            base_premium=ap,
        ))

    # All Risks Extension — applied to 10% of content SI
    if inclusions.get("all_risks") and profile.content_si > 0:
        r = additional_rates["all_risks"]
        ar_base = profile.content_si * 0.10
        arp = ar_base * r
        sections.append(SectionPremium(
            section="All Risks Extension",
            sum_insured=ar_base,
            rate=r,
            base_premium=arp,
        ))

    # Personal Accident — applied to total SI
    total_si = profile.building_si + profile.content_si
    if inclusions.get("personal_accident") and total_si > 0:
        r = additional_rates["personal_accident"]
        pap = total_si * r
        sections.append(SectionPremium(
            section="Personal Accident",
            sum_insured=total_si,
            rate=r,
            base_premium=pap,
        ))

    # Alternative Accommodation
    if inclusions.get("alternative_accommodation") and profile.building_si > 0:
        r = additional_rates["alternative_accommodation"]
        aap = profile.building_si * r
        sections.append(SectionPremium(
            section="Alternative Accommodation",
            sum_insured=profile.building_si,
            rate=r,
            base_premium=aap,
        ))

    # ── STEP 2: Sum base premiums ──────────────────────────────────────────────
    base_premium = sum(s.base_premium for s in sections)

    adjustments: list[AdjustmentItem] = []
    running = base_premium

    # ── STEP 3: Location factor ────────────────────────────────────────────────
    loc_factor = LOCATION_FACTORS.get(profile.location, 0.0)
    if loc_factor != 0:
        loc_amount = running * loc_factor
        adjustments.append(AdjustmentItem(
            label=f"Location Loading ({profile.location})",
            type="loading" if loc_factor > 0 else "discount",
            percentage=loc_factor,
            amount=loc_amount,
        ))
        running += loc_amount

    # ── STEP 4: (Individual only) Cover type multiplier already handled via rates
    # Corporate uses rate bands instead; no additional multiplier needed

    # ── STEP 5: Building age loading ──────────────────────────────────────────
    age_loading = building_age_loading(profile.building_age)
    if age_loading > 0:
        age_amount = running * age_loading
        adjustments.append(AdjustmentItem(
            label=f"Building Age Loading ({profile.building_age} yrs)",
            type="loading",
            percentage=age_loading,
            amount=age_amount,
        ))
        running += age_amount

    # ── STEP 6: Claims history loading ────────────────────────────────────────
    claims_loading = claims_history_loading(profile.claims_last_3_years)
    if claims_loading > 0:
        claims_amount = running * claims_loading
        adjustments.append(AdjustmentItem(
            label=f"Claims History Loading ({profile.claims_last_3_years} claim(s))",
            type="loading",
            percentage=claims_loading,
            amount=claims_amount,
        ))
        running += claims_amount

    # ── STEP 7: Security system discount ──────────────────────────────────────
    if profile.has_security_system:
        sec_amount = running * SECURITY_SYSTEM_DISCOUNT
        adjustments.append(AdjustmentItem(
            label="Security System Discount",
            type="discount",
            percentage=-SECURITY_SYSTEM_DISCOUNT,
            amount=-sec_amount,
        ))
        running -= sec_amount

    # ── STEP 8: Fire extinguisher discount ────────────────────────────────────
    if profile.has_fire_extinguisher:
        fire_amount = running * FIRE_EXTINGUISHER_DISCOUNT
        adjustments.append(AdjustmentItem(
            label="Fire Extinguisher Discount",
            type="discount",
            percentage=-FIRE_EXTINGUISHER_DISCOUNT,
            amount=-fire_amount,
        ))
        running -= fire_amount

    # ── STEP 9: Volume discount ────────────────────────────────────────────────
    vol_disc = (
        volume_discount_corporate(total_si) if is_corporate
        else volume_discount_individual(total_si)
    )
    if vol_disc > 0:
        vol_amount = running * vol_disc
        adjustments.append(AdjustmentItem(
            label="Volume Discount",
            type="discount",
            percentage=-vol_disc,
            amount=-vol_amount,
        ))
        running -= vol_amount

    # ── STEP 10: Duration adjustment ──────────────────────────────────────────
    if profile.duration_months < 12:
        pro_rata = profile.duration_months / 12.0
        short_period_factor = pro_rata * (1 + SHORT_PERIOD_LOADING)
        duration_amount = running * short_period_factor - running
        adjustments.append(AdjustmentItem(
            label=f"Short Period Adjustment ({profile.duration_months} months)",
            type="loading",
            percentage=short_period_factor - 1,
            amount=duration_amount,
        ))
        running += duration_amount

    # ── STEP 11: Minimum premium floor ────────────────────────────────────────
    min_premium = MIN_PREMIUM_CORPORATE if is_corporate else MIN_PREMIUM_INDIVIDUAL
    minimum_applied = False
    if running < min_premium:
        adjustments.append(AdjustmentItem(
            label=f"Minimum Premium Applied (₦{min_premium:,.0f})",
            type="info",
            percentage=0,
            amount=min_premium - running,
        ))
        running = min_premium
        minimum_applied = True

    gross_premium = round(running, 2)

    # ── STEP 12: Commission ────────────────────────────────────────────────────
    commission_amount = round(gross_premium * COMMISSION_RATE, 2)

    # ── STEP 13: Net premium ───────────────────────────────────────────────────
    net_premium = round(gross_premium - commission_amount, 2)

    total_adjustment_amount = sum(a.amount for a in adjustments)
    rate_per_mille = (gross_premium / total_si * 1000) if total_si > 0 else 0

    return PremiumBreakdown(
        segment=profile.segment,
        cover_type=profile.cover_type,
        location=profile.location,
        building_si=profile.building_si,
        content_si=profile.content_si,
        total_si=total_si,
        duration_months=profile.duration_months,
        band=band,
        sections=sections,
        base_premium=round(base_premium, 2),
        adjustments=adjustments,
        total_adjustment_amount=round(total_adjustment_amount, 2),
        gross_premium=gross_premium,
        commission_rate=COMMISSION_RATE,
        commission_amount=commission_amount,
        net_premium=net_premium,
        rate_per_mille=round(rate_per_mille, 4),
        minimum_applied=minimum_applied,
    )
