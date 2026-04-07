#!/usr/bin/env python3
"""
Healthcare VOC Compliance Calculator — Python Engine

Calculates VOC exposure concentration per cleaning cycle based on product
VOC content, dilution ratio, coverage rate, room geometry, and ventilation.
Compares results against OSHA PELs and jurisdiction-specific limits.

Exposes /calculate and /health REST endpoints via FastAPI.

Reference:
- OSHA 29 CFR 1910.1000 Table Z-1 (Total VOC PEL: 300 mg/m³ as TVOC)
- ASHRAE 62.1-2022 (ventilation rates for healthcare)
- EPA 40 CFR Part 59 Subpart C
- Canada SOR/2021-268
"""

import csv
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

# OSHA Total VOC PEL (mg/m³) — conservative general threshold
OSHA_TVOC_PEL = 300.0

# ASHRAE 62.1 minimum ventilation for healthcare spaces (ACH)
ASHRAE_HEALTHCARE_ACH = {
    "patient_room": 6,
    "operating_room": 20,
    "icu": 12,
    "corridor": 4,
    "waiting_room": 6,
    "exam_room": 6,
    "laboratory": 12,
    "pharmacy": 8,
    "dietary_kitchen": 10,
    "laundry": 10,
    "soiled_utility": 10,
    "clean_utility": 4,
    "bathroom": 10,
    "janitor_closet": 10,
    "general_office": 4,
}

# Conversion factors
SQFT_TO_SQM = 0.09290304
FT_TO_M = 0.3048
G_PER_L_TO_MG_PER_ML = 1.0  # 1 g/L = 1 mg/mL

# Regulatory limits dataset path
DATASETS_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"
LIMITS_CSV = DATASETS_DIR / "voc_regulatory_limits.csv"


# ──────────────────────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────────────────────

@dataclass
class VOCCalculation:
    """Result of a VOC exposure calculation."""
    room_volume_m3: float
    product_voc_g_per_L: float
    effective_voc_g_per_L: float
    product_applied_L: float
    total_voc_released_g: float
    total_voc_released_mg: float
    initial_concentration_mg_per_m3: float
    steady_state_concentration_mg_per_m3: float
    osha_pel_percent: float
    time_to_safe_reentry_minutes: float
    annual_voc_load_g: float
    annual_voc_load_kg: float
    air_changes_per_hour: float
    compliant_jurisdictions: list
    non_compliant_jurisdictions: list
    warnings: list


# ──────────────────────────────────────────────────────────────
# Core calculation
# ──────────────────────────────────────────────────────────────

def load_regulatory_limits():
    """Load jurisdiction VOC limits from Dataset A."""
    limits = {}
    if not LIMITS_CSV.exists():
        return limits
    with open(LIMITS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["jurisdiction_code"], row["product_category"])
            limits[key] = float(row["voc_limit_g_per_L"])
    return limits


_REG_LIMITS = None

def get_regulatory_limits():
    global _REG_LIMITS
    if _REG_LIMITS is None:
        _REG_LIMITS = load_regulatory_limits()
    return _REG_LIMITS


def calculate_voc_exposure(
    room_sqft: float,
    ceiling_height_ft: float,
    product_voc_g_per_L: float,
    dilution_ratio: float,
    coverage_sqft_per_L: float,
    air_changes_per_hour: float,
    cleaning_frequency_per_year: int,
    product_category: str = "General Purpose Cleaner",
    space_type: str = "patient_room",
) -> VOCCalculation:
    """
    Calculate VOC exposure for a single cleaning cycle.

    Parameters
    ----------
    room_sqft : float
        Room floor area in square feet.
    ceiling_height_ft : float
        Ceiling height in feet.
    product_voc_g_per_L : float
        VOC content of the product concentrate in g/L.
    dilution_ratio : float
        Fraction of concentrate in the applied solution (1.0 = RTU, 0.015625 = 1:64).
    coverage_sqft_per_L : float
        Area covered per litre of applied solution.
    air_changes_per_hour : float
        Room ventilation rate in air changes per hour (ACH).
    cleaning_frequency_per_year : int
        Number of cleaning cycles per year.
    product_category : str
        Product category for regulatory lookup.
    space_type : str
        Healthcare space type for ASHRAE reference.

    Returns
    -------
    VOCCalculation
        Complete calculation result with compliance data.
    """
    warnings = []

    # Room volume
    room_sqm = room_sqft * SQFT_TO_SQM
    ceiling_m = ceiling_height_ft * FT_TO_M
    room_volume_m3 = room_sqm * ceiling_m

    if room_volume_m3 <= 0:
        raise ValueError("Room volume must be positive")

    # Effective VOC after dilution
    effective_voc = product_voc_g_per_L * dilution_ratio

    # Amount of product applied
    if coverage_sqft_per_L <= 0:
        raise ValueError("Coverage rate must be positive")
    product_applied_L = room_sqft / coverage_sqft_per_L

    # Total VOC released in one cleaning cycle
    total_voc_g = effective_voc * product_applied_L
    total_voc_mg = total_voc_g * 1000.0

    # Initial peak concentration (instantaneous mixing, no ventilation)
    initial_conc = total_voc_mg / room_volume_m3

    # Steady-state concentration with ventilation
    # Using single-zone mass balance: C_ss = E / (Q)
    # where E = emission rate (mg/hr), Q = ventilation rate (m³/hr)
    # Assume all VOC is released over a 30-minute cleaning cycle
    cleaning_duration_hr = 0.5
    emission_rate_mg_per_hr = total_voc_mg / cleaning_duration_hr
    ventilation_rate_m3_per_hr = air_changes_per_hour * room_volume_m3

    if ventilation_rate_m3_per_hr > 0:
        steady_state_conc = emission_rate_mg_per_hr / ventilation_rate_m3_per_hr
    else:
        steady_state_conc = initial_conc
        warnings.append("Zero ventilation — VOC will accumulate without dissipation")

    # OSHA PEL comparison
    osha_pel_pct = (steady_state_conc / OSHA_TVOC_PEL) * 100.0

    # Time to safe reentry (concentration drops below 10% of OSHA PEL)
    target_conc = OSHA_TVOC_PEL * 0.10  # 30 mg/m³
    if steady_state_conc <= target_conc:
        reentry_minutes = 0.0
    elif air_changes_per_hour > 0:
        # Exponential decay: C(t) = C0 * exp(-ACH * t)
        # Solve for t when C(t) = target
        decay_constant = air_changes_per_hour
        ratio = steady_state_conc / target_conc
        if ratio > 0:
            reentry_hours = math.log(ratio) / decay_constant
            reentry_minutes = max(0.0, reentry_hours * 60.0)
        else:
            reentry_minutes = 0.0
    else:
        reentry_minutes = float("inf")
        warnings.append("Cannot calculate reentry time with zero ventilation")

    # Annual VOC load
    annual_voc_g = total_voc_g * cleaning_frequency_per_year
    annual_voc_kg = annual_voc_g / 1000.0

    # ASHRAE compliance check
    ashrae_min = ASHRAE_HEALTHCARE_ACH.get(space_type, 4)
    if air_changes_per_hour < ashrae_min:
        warnings.append(
            f"Ventilation ({air_changes_per_hour} ACH) below ASHRAE 62.1 minimum "
            f"for {space_type} ({ashrae_min} ACH)"
        )

    # Jurisdiction compliance
    reg_limits = get_regulatory_limits()
    compliant = []
    non_compliant = []
    checked_codes = set()
    for (jcode, cat), limit in reg_limits.items():
        if cat == product_category:
            checked_codes.add(jcode)
            if product_voc_g_per_L <= limit:
                compliant.append(jcode)
            else:
                non_compliant.append(jcode)

    if osha_pel_pct > 50.0:
        warnings.append("Steady-state VOC exceeds 50% of OSHA PEL — consider additional ventilation or lower-VOC product")
    if osha_pel_pct > 100.0:
        warnings.append("CRITICAL: Steady-state VOC exceeds OSHA PEL — do not use without engineering controls")

    return VOCCalculation(
        room_volume_m3=round(room_volume_m3, 2),
        product_voc_g_per_L=product_voc_g_per_L,
        effective_voc_g_per_L=round(effective_voc, 4),
        product_applied_L=round(product_applied_L, 4),
        total_voc_released_g=round(total_voc_g, 4),
        total_voc_released_mg=round(total_voc_mg, 2),
        initial_concentration_mg_per_m3=round(initial_conc, 2),
        steady_state_concentration_mg_per_m3=round(steady_state_conc, 2),
        osha_pel_percent=round(osha_pel_pct, 2),
        time_to_safe_reentry_minutes=round(reentry_minutes, 1) if reentry_minutes != float("inf") else -1,
        annual_voc_load_g=round(annual_voc_g, 2),
        annual_voc_load_kg=round(annual_voc_kg, 4),
        air_changes_per_hour=air_changes_per_hour,
        compliant_jurisdictions=sorted(compliant),
        non_compliant_jurisdictions=sorted(non_compliant),
        warnings=warnings,
    )


# ──────────────────────────────────────────────────────────────
# CLI mode
# ──────────────────────────────────────────────────────────────

def cli_calculate():
    """Run a calculation from command-line arguments or defaults."""
    result = calculate_voc_exposure(
        room_sqft=200.0,
        ceiling_height_ft=9.0,
        product_voc_g_per_L=8.0,
        dilution_ratio=1.0 / 65.0,  # 1:64
        coverage_sqft_per_L=400.0,
        air_changes_per_hour=6.0,
        cleaning_frequency_per_year=365,
        product_category="General Purpose Cleaner",
        space_type="patient_room",
    )

    print("Healthcare VOC Compliance Calculator — Result")
    print("=" * 55)
    print(f"Room volume:                    {result.room_volume_m3} m³")
    print(f"Product VOC (concentrate):      {result.product_voc_g_per_L} g/L")
    print(f"Effective VOC (diluted):         {result.effective_voc_g_per_L} g/L")
    print(f"Product applied:                {result.product_applied_L} L")
    print(f"Total VOC released:             {result.total_voc_released_mg} mg")
    print(f"Initial concentration:          {result.initial_concentration_mg_per_m3} mg/m³")
    print(f"Steady-state concentration:     {result.steady_state_concentration_mg_per_m3} mg/m³")
    print(f"OSHA PEL usage:                 {result.osha_pel_percent}%")
    print(f"Time to safe reentry:           {result.time_to_safe_reentry_minutes} min")
    print(f"Annual VOC load:                {result.annual_voc_load_kg} kg/year")
    print(f"Compliant jurisdictions:        {len(result.compliant_jurisdictions)} / {len(result.compliant_jurisdictions) + len(result.non_compliant_jurisdictions)}")
    if result.warnings:
        print(f"\nWarnings:")
        for w in result.warnings:
            print(f"  ⚠ {w}")


# ──────────────────────────────────────────────────────────────
# FastAPI application
# ──────────────────────────────────────────────────────────────

if HAS_FASTAPI:
    app = FastAPI(
        title="Healthcare VOC Compliance Calculator",
        description="Calculate VOC exposure and regulatory compliance for healthcare facility cleaning products.",
        version="0.1.0",
    )

    class CalculateRequest(BaseModel):
        room_sqft: float = Field(..., gt=0, description="Room floor area in square feet")
        ceiling_height_ft: float = Field(default=9.0, gt=0, description="Ceiling height in feet")
        product_voc_g_per_L: float = Field(..., ge=0, description="Product VOC content in g/L")
        dilution_ratio: float = Field(default=1.0, gt=0, le=1.0, description="Concentrate fraction (1.0=RTU, 0.015625=1:64)")
        coverage_sqft_per_L: float = Field(default=400.0, gt=0, description="Coverage area per litre applied")
        air_changes_per_hour: float = Field(default=6.0, ge=0, description="Ventilation rate (ACH)")
        cleaning_frequency_per_year: int = Field(default=365, ge=1, description="Cleaning cycles per year")
        product_category: str = Field(default="General Purpose Cleaner", description="Product category for regulatory lookup")
        space_type: str = Field(default="patient_room", description="Healthcare space type")

    @app.post("/calculate")
    def api_calculate(req: CalculateRequest):
        try:
            result = calculate_voc_exposure(
                room_sqft=req.room_sqft,
                ceiling_height_ft=req.ceiling_height_ft,
                product_voc_g_per_L=req.product_voc_g_per_L,
                dilution_ratio=req.dilution_ratio,
                coverage_sqft_per_L=req.coverage_sqft_per_L,
                air_changes_per_hour=req.air_changes_per_hour,
                cleaning_frequency_per_year=req.cleaning_frequency_per_year,
                product_category=req.product_category,
                space_type=req.space_type,
            )
            return {
                "room_volume_m3": result.room_volume_m3,
                "product_voc_g_per_L": result.product_voc_g_per_L,
                "effective_voc_g_per_L": result.effective_voc_g_per_L,
                "product_applied_L": result.product_applied_L,
                "total_voc_released_g": result.total_voc_released_g,
                "total_voc_released_mg": result.total_voc_released_mg,
                "initial_concentration_mg_per_m3": result.initial_concentration_mg_per_m3,
                "steady_state_concentration_mg_per_m3": result.steady_state_concentration_mg_per_m3,
                "osha_pel_percent": result.osha_pel_percent,
                "time_to_safe_reentry_minutes": result.time_to_safe_reentry_minutes,
                "annual_voc_load_g": result.annual_voc_load_g,
                "annual_voc_load_kg": result.annual_voc_load_kg,
                "air_changes_per_hour": result.air_changes_per_hour,
                "compliant_jurisdictions": result.compliant_jurisdictions,
                "non_compliant_jurisdictions": result.non_compliant_jurisdictions,
                "warnings": result.warnings,
            }
        except (ValueError, ZeroDivisionError) as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/health")
    def health():
        limits = get_regulatory_limits()
        return {
            "status": "ok",
            "engine": "python",
            "version": "0.1.0",
            "regulatory_limits_loaded": len(limits),
        }


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--serve" in sys.argv:
        if not HAS_FASTAPI:
            print("FastAPI not installed. Run: pip install fastapi uvicorn")
            sys.exit(1)
        port = 8001
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        cli_calculate()
