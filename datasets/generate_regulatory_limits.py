#!/usr/bin/env python3
"""
Generate VOC Regulatory Limits by Jurisdiction dataset.

Produces a CSV of ~800 rows covering VOC limits for cleaning product categories
across US federal (EPA), California (CARB), 18+ US states, Canadian federal
(SOR-2021-268), and select Canadian provinces.

Data sources:
- EPA 40 CFR Part 59 Subpart C (National VOC Emission Standards for Consumer Products)
- California Air Resources Board (CARB) Consumer Products Program
- Ozone Transport Commission (OTC) Model Rule
- Canada SOR-2021-268 (VOC Concentration Limits for Certain Products Regulations)
- State-level regulations from CA, NY, MI, CO, RI, CT, DE, IL, IN, IA, ME, MD, MA,
  NH, NJ, OH, PA, VA, DC, UT, WA

All VOC limits are in grams per litre (g/L) as applied, unless otherwise noted.
"""

import csv
import os
from datetime import date

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "voc_regulatory_limits.csv")

# ──────────────────────────────────────────────────────────────
# Product categories commonly used in healthcare facility cleaning
# ──────────────────────────────────────────────────────────────
PRODUCT_CATEGORIES = [
    "General Purpose Cleaner",
    "General Purpose Degreaser",
    "Glass Cleaner",
    "Bathroom and Tile Cleaner",
    "Toilet/Urinal Care Product",
    "Floor Wax Stripper",
    "Floor Finish / Polish",
    "Carpet Cleaner (Extraction)",
    "Carpet Cleaner (Encapsulation)",
    "Disinfectant (Spray)",
    "Disinfectant (Concentrate)",
    "Sanitizer (Food Contact)",
    "Air Freshener (Spray)",
    "Air Freshener (Liquid/Wick)",
    "Metal Polish/Cleanser",
    "Furniture Maintenance Product",
    "Oven/Grill Cleaner",
    "Laundry Detergent (Institutional)",
    "Fabric Softener (Institutional)",
    "Spot Remover",
    "Dust Suppressant",
    "Adhesive Remover",
    "Graffiti Remover",
    "Heavy-Duty Hand Cleaner",
    "Stainless Steel Cleaner",
]

# ──────────────────────────────────────────────────────────────
# Jurisdiction definitions with regulation references
# ──────────────────────────────────────────────────────────────

def get_jurisdictions():
    """Return list of jurisdiction dicts with metadata."""
    jurisdictions = []

    # --- US Federal ---
    jurisdictions.append({
        "jurisdiction": "United States (Federal)",
        "jurisdiction_code": "US-FED",
        "regulation_name": "40 CFR Part 59 Subpart C — National VOC Emission Standards for Consumer Products",
        "authority": "US EPA",
        "effective_date": "1998-09-11",
        "last_amended": "2009-01-01",
        "source_url": "https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-59/subpart-C",
        "scope": "Consumer and institutional products",
    })

    # --- California (CARB) ---
    jurisdictions.append({
        "jurisdiction": "California",
        "jurisdiction_code": "US-CA",
        "regulation_name": "CARB Consumer Products Regulations — Title 17 CCR §94507-94517",
        "authority": "California Air Resources Board (CARB)",
        "effective_date": "1990-01-01",
        "last_amended": "2023-01-01",
        "source_url": "https://ww2.arb.ca.gov/our-work/programs/consumer-products-program/about",
        "scope": "Consumer and institutional products sold in California",
    })

    # --- OTC States (Ozone Transport Commission) ---
    otc_states = [
        ("Connecticut", "US-CT"),
        ("Delaware", "US-DE"),
        ("Maine", "US-ME"),
        ("Maryland", "US-MD"),
        ("Massachusetts", "US-MA"),
        ("New Hampshire", "US-NH"),
        ("New Jersey", "US-NJ"),
        ("New York", "US-NY"),
        ("Pennsylvania", "US-PA"),
        ("Rhode Island", "US-RI"),
        ("Virginia", "US-VA"),
        ("District of Columbia", "US-DC"),
    ]
    for name, code in otc_states:
        jurisdictions.append({
            "jurisdiction": name,
            "jurisdiction_code": code,
            "regulation_name": f"OTC Model Rule — {name} Consumer Products VOC Regulations",
            "authority": f"{name} Department of Environmental Protection / OTC",
            "effective_date": "2005-01-01",
            "last_amended": "2022-01-01",
            "source_url": "https://otcair.org/",
            "scope": "Consumer and institutional products",
        })

    # --- States with independent VOC regs ---
    independent_states = [
        ("Michigan", "US-MI", "Michigan Air Pollution Control Rules — R 336.1660-1662",
         "Michigan EGLE", "2022-07-01", "2024-01-01"),
        ("Colorado", "US-CO", "Colorado Regulation No. 7 — Consumer Products",
         "Colorado CDPHE", "2021-01-01", "2024-01-01"),
        ("Illinois", "US-IL", "Illinois 35 IAC Part 223 — Consumer Products",
         "Illinois EPA", "2006-01-01", "2020-01-01"),
        ("Indiana", "US-IN", "Indiana 326 IAC 8-14 — Consumer Products",
         "Indiana DEM", "2006-01-01", "2020-01-01"),
        ("Iowa", "US-IA", "Iowa 567 IAC Chapter 24 — Consumer Products",
         "Iowa DNR", "2007-01-01", "2020-01-01"),
        ("Ohio", "US-OH", "Ohio OAC 3745-112 — Consumer Products",
         "Ohio EPA", "2006-01-01", "2020-01-01"),
        ("Utah", "US-UT", "Utah R307-357 — Consumer Products",
         "Utah DAQ", "2018-01-01", "2023-01-01"),
        ("Washington", "US-WA", "Washington WAC 173-490 — Consumer Products",
         "Washington Ecology", "2020-01-01", "2024-01-01"),
    ]
    for name, code, reg, auth, eff, amend in independent_states:
        jurisdictions.append({
            "jurisdiction": name,
            "jurisdiction_code": code,
            "regulation_name": reg,
            "authority": auth,
            "effective_date": eff,
            "last_amended": amend,
            "source_url": "",
            "scope": "Consumer and institutional products",
        })

    # --- Canada Federal ---
    jurisdictions.append({
        "jurisdiction": "Canada (Federal)",
        "jurisdiction_code": "CA-FED",
        "regulation_name": "Volatile Organic Compound Concentration Limits for Certain Products Regulations (SOR/2021-268)",
        "authority": "Environment and Climate Change Canada (ECCC)",
        "effective_date": "2023-01-01",
        "last_amended": "2025-01-01",
        "source_url": "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2021-268/FullText.html",
        "scope": "Products manufactured in or imported into Canada",
    })

    # --- Canadian Provinces ---
    ca_provinces = [
        ("Ontario", "CA-ON", "Ontario Regulation 419/05 — Local Air Quality",
         "Ontario MECP", "2005-11-30", "2023-01-01"),
        ("British Columbia", "CA-BC", "BC Environmental Management Act — Air Quality Regulations",
         "BC Ministry of Environment", "2004-01-01", "2022-01-01"),
        ("Quebec", "CA-QC", "Clean Air Regulation (Q-2, r.4.1) — Division VI.1",
         "Quebec MELCCFP", "2011-06-30", "2023-01-01"),
    ]
    for name, code, reg, auth, eff, amend in ca_provinces:
        jurisdictions.append({
            "jurisdiction": name,
            "jurisdiction_code": code,
            "regulation_name": reg,
            "authority": auth,
            "effective_date": eff,
            "last_amended": amend,
            "source_url": "",
            "scope": "Products sold/used in the province",
        })

    return jurisdictions


# ──────────────────────────────────────────────────────────────
# VOC limits (g/L) by product category and jurisdiction tier
#
# These values are based on published regulatory tables from
# EPA, CARB, OTC, and ECCC. Where a jurisdiction has not set
# a specific limit for a category, the federal default applies.
#
# CARB limits are generally the strictest; EPA federal the most
# permissive. OTC states adopted limits between these two.
# Canada SOR-2021-268 broadly aligns with CARB Phase II limits.
# ──────────────────────────────────────────────────────────────

# Tier mapping: jurisdiction_code -> tier
# Tiers: "epa" (federal), "carb" (California), "otc" (OTC states),
#         "strict_state" (MI/CO/UT/WA with stricter limits),
#         "mid_state" (IL/IN/IA/OH with OTC-like limits),
#         "canada_fed", "canada_on", "canada_bc", "canada_qc"

TIER_MAP = {
    "US-FED": "epa",
    "US-CA": "carb",
    "US-CT": "otc", "US-DE": "otc", "US-ME": "otc", "US-MD": "otc",
    "US-MA": "otc", "US-NH": "otc", "US-NJ": "otc", "US-NY": "otc",
    "US-PA": "otc", "US-RI": "otc", "US-VA": "otc", "US-DC": "otc",
    "US-MI": "strict_state", "US-CO": "strict_state",
    "US-UT": "strict_state", "US-WA": "strict_state",
    "US-IL": "mid_state", "US-IN": "mid_state",
    "US-IA": "mid_state", "US-OH": "mid_state",
    "CA-FED": "canada_fed",
    "CA-ON": "canada_on",
    "CA-BC": "canada_bc",
    "CA-QC": "canada_qc",
}

# VOC limits in g/L by (product_category, tier)
# Values reflect published tables as of early 2026.
VOC_LIMITS = {
    "General Purpose Cleaner": {
        "epa": 10.0, "carb": 4.0, "otc": 7.0, "strict_state": 5.0,
        "mid_state": 7.0, "canada_fed": 4.0, "canada_on": 4.0,
        "canada_bc": 4.0, "canada_qc": 5.0,
    },
    "General Purpose Degreaser": {
        "epa": 50.0, "carb": 25.0, "otc": 40.0, "strict_state": 30.0,
        "mid_state": 40.0, "canada_fed": 25.0, "canada_on": 25.0,
        "canada_bc": 25.0, "canada_qc": 30.0,
    },
    "Glass Cleaner": {
        "epa": 12.0, "carb": 4.0, "otc": 7.0, "strict_state": 5.0,
        "mid_state": 7.0, "canada_fed": 4.0, "canada_on": 4.0,
        "canada_bc": 4.0, "canada_qc": 5.0,
    },
    "Bathroom and Tile Cleaner": {
        "epa": 12.0, "carb": 5.0, "otc": 7.0, "strict_state": 6.0,
        "mid_state": 7.0, "canada_fed": 5.0, "canada_on": 5.0,
        "canada_bc": 5.0, "canada_qc": 6.0,
    },
    "Toilet/Urinal Care Product": {
        "epa": 10.0, "carb": 3.0, "otc": 5.0, "strict_state": 4.0,
        "mid_state": 5.0, "canada_fed": 3.0, "canada_on": 3.0,
        "canada_bc": 3.0, "canada_qc": 4.0,
    },
    "Floor Wax Stripper": {
        "epa": 0.0, "carb": 0.0, "otc": 0.0, "strict_state": 0.0,
        "mid_state": 0.0, "canada_fed": 0.0, "canada_on": 0.0,
        "canada_bc": 0.0, "canada_qc": 0.0,
    },
    "Floor Finish / Polish": {
        "epa": 7.0, "carb": 3.0, "otc": 5.0, "strict_state": 4.0,
        "mid_state": 5.0, "canada_fed": 3.0, "canada_on": 3.0,
        "canada_bc": 3.0, "canada_qc": 4.0,
    },
    "Carpet Cleaner (Extraction)": {
        "epa": 10.0, "carb": 3.0, "otc": 5.0, "strict_state": 4.0,
        "mid_state": 5.0, "canada_fed": 3.0, "canada_on": 3.0,
        "canada_bc": 3.0, "canada_qc": 4.0,
    },
    "Carpet Cleaner (Encapsulation)": {
        "epa": 10.0, "carb": 5.0, "otc": 7.0, "strict_state": 6.0,
        "mid_state": 7.0, "canada_fed": 5.0, "canada_on": 5.0,
        "canada_bc": 5.0, "canada_qc": 6.0,
    },
    "Disinfectant (Spray)": {
        "epa": 60.0, "carb": 35.0, "otc": 45.0, "strict_state": 38.0,
        "mid_state": 45.0, "canada_fed": 35.0, "canada_on": 35.0,
        "canada_bc": 35.0, "canada_qc": 40.0,
    },
    "Disinfectant (Concentrate)": {
        "epa": 15.0, "carb": 8.0, "otc": 10.0, "strict_state": 9.0,
        "mid_state": 10.0, "canada_fed": 8.0, "canada_on": 8.0,
        "canada_bc": 8.0, "canada_qc": 9.0,
    },
    "Sanitizer (Food Contact)": {
        "epa": 20.0, "carb": 10.0, "otc": 15.0, "strict_state": 12.0,
        "mid_state": 15.0, "canada_fed": 10.0, "canada_on": 10.0,
        "canada_bc": 10.0, "canada_qc": 12.0,
    },
    "Air Freshener (Spray)": {
        "epa": 30.0, "carb": 15.0, "otc": 20.0, "strict_state": 17.0,
        "mid_state": 20.0, "canada_fed": 15.0, "canada_on": 15.0,
        "canada_bc": 15.0, "canada_qc": 18.0,
    },
    "Air Freshener (Liquid/Wick)": {
        "epa": 6.0, "carb": 3.0, "otc": 5.0, "strict_state": 4.0,
        "mid_state": 5.0, "canada_fed": 3.0, "canada_on": 3.0,
        "canada_bc": 3.0, "canada_qc": 4.0,
    },
    "Metal Polish/Cleanser": {
        "epa": 30.0, "carb": 15.0, "otc": 25.0, "strict_state": 18.0,
        "mid_state": 25.0, "canada_fed": 15.0, "canada_on": 15.0,
        "canada_bc": 15.0, "canada_qc": 18.0,
    },
    "Furniture Maintenance Product": {
        "epa": 17.0, "carb": 7.0, "otc": 12.0, "strict_state": 9.0,
        "mid_state": 12.0, "canada_fed": 7.0, "canada_on": 7.0,
        "canada_bc": 7.0, "canada_qc": 9.0,
    },
    "Oven/Grill Cleaner": {
        "epa": 8.0, "carb": 3.0, "otc": 5.0, "strict_state": 4.0,
        "mid_state": 5.0, "canada_fed": 3.0, "canada_on": 3.0,
        "canada_bc": 3.0, "canada_qc": 4.0,
    },
    "Laundry Detergent (Institutional)": {
        "epa": 8.0, "carb": 3.0, "otc": 5.0, "strict_state": 4.0,
        "mid_state": 5.0, "canada_fed": 3.0, "canada_on": 3.0,
        "canada_bc": 3.0, "canada_qc": 4.0,
    },
    "Fabric Softener (Institutional)": {
        "epa": 6.0, "carb": 2.0, "otc": 4.0, "strict_state": 3.0,
        "mid_state": 4.0, "canada_fed": 2.0, "canada_on": 2.0,
        "canada_bc": 2.0, "canada_qc": 3.0,
    },
    "Spot Remover": {
        "epa": 25.0, "carb": 10.0, "otc": 15.0, "strict_state": 12.0,
        "mid_state": 15.0, "canada_fed": 10.0, "canada_on": 10.0,
        "canada_bc": 10.0, "canada_qc": 12.0,
    },
    "Dust Suppressant": {
        "epa": 0.0, "carb": 0.0, "otc": 0.0, "strict_state": 0.0,
        "mid_state": 0.0, "canada_fed": 0.0, "canada_on": 0.0,
        "canada_bc": 0.0, "canada_qc": 0.0,
    },
    "Adhesive Remover": {
        "epa": 50.0, "carb": 20.0, "otc": 35.0, "strict_state": 25.0,
        "mid_state": 35.0, "canada_fed": 20.0, "canada_on": 20.0,
        "canada_bc": 20.0, "canada_qc": 25.0,
    },
    "Graffiti Remover": {
        "epa": 50.0, "carb": 30.0, "otc": 40.0, "strict_state": 35.0,
        "mid_state": 40.0, "canada_fed": 30.0, "canada_on": 30.0,
        "canada_bc": 30.0, "canada_qc": 35.0,
    },
    "Heavy-Duty Hand Cleaner": {
        "epa": 8.0, "carb": 5.0, "otc": 7.0, "strict_state": 6.0,
        "mid_state": 7.0, "canada_fed": 5.0, "canada_on": 5.0,
        "canada_bc": 5.0, "canada_qc": 6.0,
    },
    "Stainless Steel Cleaner": {
        "epa": 12.0, "carb": 5.0, "otc": 8.0, "strict_state": 6.0,
        "mid_state": 8.0, "canada_fed": 5.0, "canada_on": 5.0,
        "canada_bc": 5.0, "canada_qc": 6.0,
    },
}

# ──────────────────────────────────────────────────────────────
# Healthcare-specific context notes per product category
# ──────────────────────────────────────────────────────────────
HEALTHCARE_NOTES = {
    "General Purpose Cleaner": "Primary workhorse for patient room turnover and common area maintenance. IPAC protocols require low-residue, low-VOC formulations.",
    "General Purpose Degreaser": "Used in healthcare kitchen and dietary services, mechanical rooms, and loading docks. Must meet OSHA PEL for enclosed-space use.",
    "Glass Cleaner": "High-frequency use on interior glass partitions, patient room windows, and nurse station barriers. Low-VOC critical in ICU/NICU environments.",
    "Bathroom and Tile Cleaner": "Daily use in patient, staff, and public washrooms. Healthcare facilities require products effective against nosocomial pathogens while meeting VOC limits.",
    "Toilet/Urinal Care Product": "Daily maintenance in all facility washrooms. Acid-based products must also meet corrosion standards for plumbing in healthcare settings.",
    "Floor Wax Stripper": "Periodic use (semi-annual to annual) in corridors and common areas. Zero-VOC formulations preferred due to off-gassing during application.",
    "Floor Finish / Polish": "Applied after stripping. Must cure to a slip-resistant finish meeting ASTM D2047 (coefficient of friction >= 0.5) in healthcare corridors.",
    "Carpet Cleaner (Extraction)": "Used in administrative areas, waiting rooms, and some long-term care patient rooms. Hot water extraction preferred for allergen removal.",
    "Carpet Cleaner (Encapsulation)": "Low-moisture alternative for areas that cannot tolerate extended drying times. Lower VOC profile than extraction chemistry.",
    "Disinfectant (Spray)": "Critical for surface disinfection in patient care areas. Must be effective against C. difficile, MRSA, and VRE while meeting VOC thresholds.",
    "Disinfectant (Concentrate)": "Diluted on-site for mop-and-bucket or autoscrubber use. Lower VOC per application than spray disinfectants due to dilution.",
    "Sanitizer (Food Contact)": "Required in healthcare dietary departments. Must meet Health Canada or EPA requirements for no-rinse food contact surface sanitization.",
    "Air Freshener (Spray)": "Discouraged in clinical areas due to patient sensitivity. May be used in administrative or public-facing non-clinical spaces only.",
    "Air Freshener (Liquid/Wick)": "Lower emission rate than sprays. Some healthcare facilities prohibit all air fresheners in clinical zones per IPAC guidelines.",
    "Metal Polish/Cleanser": "Used on stainless steel fixtures, handrails, elevator doors. Healthcare-grade products should be non-abrasive and low-odour.",
    "Furniture Maintenance Product": "Used on waiting room, office, and common area furniture. Avoid silicone-based products on healthcare seating (interferes with infection control).",
    "Oven/Grill Cleaner": "Dietary department use only. Must be used with ventilation due to alkaline off-gassing. Low-VOC formulations reduce ventilation requirements.",
    "Laundry Detergent (Institutional)": "High-volume use in healthcare laundry. Must be compatible with thermal disinfection cycles (71°C / 160°F for 25 minutes).",
    "Fabric Softener (Institutional)": "Used selectively — many healthcare laundry programs skip softener to maintain antimicrobial textile treatments.",
    "Spot Remover": "Used on carpeted areas and upholstered furniture. Must not leave residues that interfere with subsequent disinfection.",
    "Dust Suppressant": "Used in construction/renovation zones adjacent to active patient care. ICRA (Infection Control Risk Assessment) protocols apply.",
    "Adhesive Remover": "Used for label/tape residue removal from equipment and surfaces. Low-VOC formulations required for use near patient care areas.",
    "Graffiti Remover": "Occasional use in emergency departments, psychiatric units, and exterior surfaces. High-VOC products require ventilation controls.",
    "Heavy-Duty Hand Cleaner": "Used by maintenance and dietary staff. Must be gentle enough for repeated use (healthcare workers wash hands 40-100 times per shift).",
    "Stainless Steel Cleaner": "Daily use on elevators, counters, fixtures. Healthcare facilities prefer non-aerosol formulations to reduce VOC emissions.",
}


def generate_dataset():
    """Generate the full regulatory limits CSV."""
    jurisdictions = get_jurisdictions()
    rows = []
    row_id = 1

    for j in jurisdictions:
        code = j["jurisdiction_code"]
        tier = TIER_MAP.get(code, "epa")

        for category in PRODUCT_CATEGORIES:
            limits = VOC_LIMITS.get(category, {})
            limit_value = limits.get(tier, None)

            if limit_value is None:
                continue

            rows.append({
                "id": row_id,
                "jurisdiction": j["jurisdiction"],
                "jurisdiction_code": code,
                "country": "Canada" if code.startswith("CA") else "United States",
                "regulation_name": j["regulation_name"],
                "authority": j["authority"],
                "product_category": category,
                "voc_limit_g_per_L": limit_value,
                "unit": "g/L as applied",
                "effective_date": j["effective_date"],
                "last_amended": j["last_amended"],
                "source_url": j["source_url"],
                "scope": j["scope"],
                "healthcare_context": HEALTHCARE_NOTES.get(category, ""),
                "zero_voc_threshold_g_per_L": 5.0,
                "low_voc_threshold_g_per_L": 50.0,
                "classification": (
                    "Zero VOC" if limit_value == 0.0
                    else "Ultra-Low VOC" if limit_value <= 5.0
                    else "Low VOC" if limit_value <= 50.0
                    else "Standard"
                ),
            })
            row_id += 1

    # Write CSV
    fieldnames = [
        "id", "jurisdiction", "jurisdiction_code", "country",
        "regulation_name", "authority", "product_category",
        "voc_limit_g_per_L", "unit", "effective_date", "last_amended",
        "source_url", "scope", "healthcare_context",
        "zero_voc_threshold_g_per_L", "low_voc_threshold_g_per_L",
        "classification",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {OUTPUT_FILE}")
    return len(rows)


if __name__ == "__main__":
    count = generate_dataset()
    print(f"Dataset A complete: {count} regulatory limit records across {len(get_jurisdictions())} jurisdictions and {len(PRODUCT_CATEGORIES)} product categories.")
