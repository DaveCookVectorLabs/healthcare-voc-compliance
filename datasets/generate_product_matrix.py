#!/usr/bin/env python3
"""
Generate Healthcare Cleaning Product VOC Compliance Matrix.

Produces a CSV of ~6,000 rows representing commercial cleaning products
used in healthcare facilities, with VOC content, certifications, compliance
flags per jurisdiction, pricing, and dilution data.

Products are synthetic but modeled on real product categories, VOC ranges,
certification thresholds, and pricing from institutional cleaning suppliers
serving Canadian and US healthcare markets (2024-2026).

Cross-references Dataset A (voc_regulatory_limits.csv) to compute per-jurisdiction
compliance for each product.
"""

import csv
import hashlib
import os
import random

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "healthcare_cleaning_products_voc.csv")
LIMITS_FILE = os.path.join(OUTPUT_DIR, "voc_regulatory_limits.csv")

random.seed(42)  # Reproducible dataset

# ──────────────────────────────────────────────────────────────
# Manufacturer names (realistic institutional chemical companies)
# ──────────────────────────────────────────────────────────────
MANUFACTURERS = [
    "Diversey Holdings",
    "Ecolab Inc.",
    "Spartan Chemical",
    "Betco Corporation",
    "GOJO Industries",
    "Clorox Professional",
    "SC Johnson Professional",
    "Zep Inc.",
    "Procter & Gamble Professional",
    "Rochester Midland Corporation",
    "Enviro-Solutions",
    "Dustbane Products",
    "Avmor Ltd.",
    "Swish Maintenance",
    "Charlotte Products",
    "Sani Professional",
    "3M Commercial Solutions",
    "Hillyard Inc.",
    "National Chemical Laboratories",
    "Buckeye International",
    "Clean Control Corporation",
    "Core Products Co.",
    "Essential Industries",
    "Midlab Inc.",
    "Pioneer Eclipse",
    "Nyco Products",
    "Carroll Company",
    "Chase Products Co.",
    "Delta Foremost Chemical",
    "Multi-Clean Inc.",
]

# ──────────────────────────────────────────────────────────────
# Product name templates per category
# ──────────────────────────────────────────────────────────────
PRODUCT_TEMPLATES = {
    "General Purpose Cleaner": [
        "{mfr} GP-Clean {series}", "{mfr} Facility Pro All-Surface {series}",
        "{mfr} HygieneMax Multi {series}", "{mfr} ClearGuard Neutral {series}",
        "{mfr} OmniClean Daily {series}", "{mfr} AquaPure GP {series}",
        "{mfr} BioSurface Clean {series}", "{mfr} ProTech Neutral {series}",
    ],
    "General Purpose Degreaser": [
        "{mfr} PowerCut Degreaser {series}", "{mfr} HD-Kleen Industrial {series}",
        "{mfr} BioBreak Degreaser {series}", "{mfr} ToughCut Pro {series}",
        "{mfr} GreenForce Degreaser {series}", "{mfr} EnzyClean HD {series}",
    ],
    "Glass Cleaner": [
        "{mfr} CrystalView Glass {series}", "{mfr} StreakFree Pro {series}",
        "{mfr} OptiClear Glass {series}", "{mfr} MirrorBright {series}",
        "{mfr} VisionPure Glass {series}", "{mfr} CleanSight {series}",
    ],
    "Bathroom and Tile Cleaner": [
        "{mfr} BathPro Tile & Surface {series}", "{mfr} SaniTile Daily {series}",
        "{mfr} TileMaster Pro {series}", "{mfr} FreshBath HC {series}",
        "{mfr} AcidFree Bath {series}", "{mfr} TileGuard Plus {series}",
    ],
    "Toilet/Urinal Care Product": [
        "{mfr} BowlBright Pro {series}", "{mfr} SaniBowl HC {series}",
        "{mfr} UriClean Daily {series}", "{mfr} PorcelainPure {series}",
    ],
    "Floor Wax Stripper": [
        "{mfr} StripMaster Zero-VOC {series}", "{mfr} FloorStrip Pro {series}",
        "{mfr} WaxBreak Complete {series}", "{mfr} BaseCoat Remover {series}",
    ],
    "Floor Finish / Polish": [
        "{mfr} DiamondShield Floor Finish {series}", "{mfr} HighGloss Pro {series}",
        "{mfr} DuraCoat Healthcare {series}", "{mfr} SlipSafe Finish {series}",
    ],
    "Carpet Cleaner (Extraction)": [
        "{mfr} DeepClean Carpet Extract {series}", "{mfr} FiberPure HWE {series}",
        "{mfr} CarpetMax Extraction {series}", "{mfr} TextileClean Pro {series}",
    ],
    "Carpet Cleaner (Encapsulation)": [
        "{mfr} EncapDry Carpet {series}", "{mfr} CrystalCap LM {series}",
        "{mfr} QuickDry Encap {series}", "{mfr} LowMoist CarpetCare {series}",
    ],
    "Disinfectant (Spray)": [
        "{mfr} PathShield RTU Spray {series}", "{mfr} ViruGuard Spray {series}",
        "{mfr} BioDefend Surface {series}", "{mfr} SaniSpray Pro {series}",
        "{mfr} InfectiKill RTU {series}", "{mfr} MediGuard Spray {series}",
        "{mfr} C-Diff Shield RTU {series}", "{mfr} QuatPro Spray {series}",
    ],
    "Disinfectant (Concentrate)": [
        "{mfr} PathShield Concentrate {series}", "{mfr} ViruGuard 256 {series}",
        "{mfr} BioDefend Dilutable {series}", "{mfr} QuatMax Concentrate {series}",
        "{mfr} OxiDisinfect Pro {series}", "{mfr} HyperOx Concentrate {series}",
    ],
    "Sanitizer (Food Contact)": [
        "{mfr} FoodSafe Sanitizer {series}", "{mfr} NoRinse FC-200 {series}",
        "{mfr} DietarySan Pro {series}", "{mfr} QuatSan Food {series}",
    ],
    "Air Freshener (Spray)": [
        "{mfr} AirPure Spray {series}", "{mfr} FreshZone Aerosol {series}",
        "{mfr} OdorNeutral Spray {series}", "{mfr} CleanAir Mist {series}",
    ],
    "Air Freshener (Liquid/Wick)": [
        "{mfr} AirPure Passive {series}", "{mfr} FreshZone Wick {series}",
        "{mfr} OdorNeutral Liquid {series}", "{mfr} AmbientClean {series}",
    ],
    "Metal Polish/Cleanser": [
        "{mfr} MetalBright Pro {series}", "{mfr} SteelShine Polish {series}",
        "{mfr} ChromeGuard {series}", "{mfr} AlloyClean {series}",
    ],
    "Furniture Maintenance Product": [
        "{mfr} FurniCare Pro {series}", "{mfr} WoodGuard Polish {series}",
        "{mfr} SurfaceSilk Furniture {series}", "{mfr} DeskClean Daily {series}",
    ],
    "Oven/Grill Cleaner": [
        "{mfr} OvenPro Heavy Duty {series}", "{mfr} GrillMaster Clean {series}",
        "{mfr} CarbonBreak Pro {series}", "{mfr} KitchenForce Oven {series}",
    ],
    "Laundry Detergent (Institutional)": [
        "{mfr} LaundryPro Institutional {series}", "{mfr} FabriClean HC {series}",
        "{mfr} ThermalWash Pro {series}", "{mfr} HygiLaundry {series}",
    ],
    "Fabric Softener (Institutional)": [
        "{mfr} SoftTouch Institutional {series}", "{mfr} FabriSoft HC {series}",
        "{mfr} TextileCare Softener {series}",
    ],
    "Spot Remover": [
        "{mfr} SpotShot Pro {series}", "{mfr} StainBreak Carpet {series}",
        "{mfr} QuickSpot Remover {series}", "{mfr} FiberRescue {series}",
    ],
    "Dust Suppressant": [
        "{mfr} DustLock Zero {series}", "{mfr} ParticulateGuard {series}",
        "{mfr} AirSafe Dust Control {series}",
    ],
    "Adhesive Remover": [
        "{mfr} AdhesiOff Pro {series}", "{mfr} StickerStrip {series}",
        "{mfr} ResidueBreak {series}", "{mfr} BondRelease {series}",
    ],
    "Graffiti Remover": [
        "{mfr} GraffitiGone Pro {series}", "{mfr} TagRemove HD {series}",
        "{mfr} UrbanClean Graffiti {series}",
    ],
    "Heavy-Duty Hand Cleaner": [
        "{mfr} HandPro Heavy Duty {series}", "{mfr} SkinSafe Industrial {series}",
        "{mfr} GritClean Pro {series}", "{mfr} MechaniClean {series}",
    ],
    "Stainless Steel Cleaner": [
        "{mfr} SSClean Pro {series}", "{mfr} InoxBright {series}",
        "{mfr} FingerPrint Guard {series}", "{mfr} MetalCare SS {series}",
    ],
}

# ──────────────────────────────────────────────────────────────
# VOC content ranges per category (g/L as applied)
# Range reflects market reality: some products meet CARB,
# some only meet EPA, some are non-compliant
# ──────────────────────────────────────────────────────────────
VOC_RANGES = {
    "General Purpose Cleaner": (0.0, 15.0),
    "General Purpose Degreaser": (0.0, 65.0),
    "Glass Cleaner": (0.0, 18.0),
    "Bathroom and Tile Cleaner": (0.0, 18.0),
    "Toilet/Urinal Care Product": (0.0, 15.0),
    "Floor Wax Stripper": (0.0, 3.0),
    "Floor Finish / Polish": (0.0, 10.0),
    "Carpet Cleaner (Extraction)": (0.0, 14.0),
    "Carpet Cleaner (Encapsulation)": (0.0, 14.0),
    "Disinfectant (Spray)": (5.0, 75.0),
    "Disinfectant (Concentrate)": (0.0, 20.0),
    "Sanitizer (Food Contact)": (0.0, 25.0),
    "Air Freshener (Spray)": (5.0, 40.0),
    "Air Freshener (Liquid/Wick)": (0.0, 10.0),
    "Metal Polish/Cleanser": (0.0, 40.0),
    "Furniture Maintenance Product": (0.0, 25.0),
    "Oven/Grill Cleaner": (0.0, 12.0),
    "Laundry Detergent (Institutional)": (0.0, 12.0),
    "Fabric Softener (Institutional)": (0.0, 8.0),
    "Spot Remover": (0.0, 35.0),
    "Dust Suppressant": (0.0, 2.0),
    "Adhesive Remover": (5.0, 65.0),
    "Graffiti Remover": (10.0, 65.0),
    "Heavy-Duty Hand Cleaner": (0.0, 12.0),
    "Stainless Steel Cleaner": (0.0, 18.0),
}

# Dilution ratios (concentrate:water) by category
DILUTION_RANGES = {
    "General Purpose Cleaner": [(1, 64), (1, 128), (1, 256), (0, 0)],  # (0,0) = RTU
    "General Purpose Degreaser": [(1, 16), (1, 32), (1, 64), (0, 0)],
    "Glass Cleaner": [(1, 32), (1, 64), (0, 0)],
    "Bathroom and Tile Cleaner": [(1, 32), (1, 64), (1, 128), (0, 0)],
    "Toilet/Urinal Care Product": [(0, 0)],  # mostly RTU
    "Floor Wax Stripper": [(1, 4), (1, 8), (1, 16)],
    "Floor Finish / Polish": [(0, 0)],  # RTU
    "Carpet Cleaner (Extraction)": [(1, 16), (1, 32), (1, 64)],
    "Carpet Cleaner (Encapsulation)": [(1, 16), (1, 32), (0, 0)],
    "Disinfectant (Spray)": [(0, 0)],  # RTU spray
    "Disinfectant (Concentrate)": [(1, 64), (1, 128), (1, 256)],
    "Sanitizer (Food Contact)": [(1, 128), (1, 256), (0, 0)],
    "Air Freshener (Spray)": [(0, 0)],
    "Air Freshener (Liquid/Wick)": [(0, 0)],
    "Metal Polish/Cleanser": [(0, 0)],
    "Furniture Maintenance Product": [(0, 0)],
    "Oven/Grill Cleaner": [(0, 0), (1, 4), (1, 8)],
    "Laundry Detergent (Institutional)": [(1, 100), (1, 200), (1, 400)],
    "Fabric Softener (Institutional)": [(1, 100), (1, 200)],
    "Spot Remover": [(0, 0)],
    "Dust Suppressant": [(1, 8), (1, 16)],
    "Adhesive Remover": [(0, 0)],
    "Graffiti Remover": [(0, 0)],
    "Heavy-Duty Hand Cleaner": [(0, 0)],
    "Stainless Steel Cleaner": [(0, 0)],
}

# Coverage rates (sqft per litre as applied)
COVERAGE_RANGES = {
    "General Purpose Cleaner": (200, 800),
    "General Purpose Degreaser": (100, 400),
    "Glass Cleaner": (300, 1000),
    "Bathroom and Tile Cleaner": (150, 500),
    "Toilet/Urinal Care Product": (50, 200),
    "Floor Wax Stripper": (100, 300),
    "Floor Finish / Polish": (150, 400),
    "Carpet Cleaner (Extraction)": (100, 300),
    "Carpet Cleaner (Encapsulation)": (200, 500),
    "Disinfectant (Spray)": (100, 400),
    "Disinfectant (Concentrate)": (200, 800),
    "Sanitizer (Food Contact)": (200, 600),
    "Air Freshener (Spray)": (500, 2000),
    "Air Freshener (Liquid/Wick)": (500, 2000),
    "Metal Polish/Cleanser": (50, 200),
    "Furniture Maintenance Product": (100, 400),
    "Oven/Grill Cleaner": (20, 80),
    "Laundry Detergent (Institutional)": (0, 0),  # N/A
    "Fabric Softener (Institutional)": (0, 0),
    "Spot Remover": (50, 200),
    "Dust Suppressant": (200, 600),
    "Adhesive Remover": (20, 80),
    "Graffiti Remover": (10, 50),
    "Heavy-Duty Hand Cleaner": (0, 0),
    "Stainless Steel Cleaner": (100, 400),
}

# Price per litre (CAD) for concentrate
PRICE_RANGES = {
    "General Purpose Cleaner": (3.50, 18.00),
    "General Purpose Degreaser": (5.00, 25.00),
    "Glass Cleaner": (3.00, 15.00),
    "Bathroom and Tile Cleaner": (4.00, 20.00),
    "Toilet/Urinal Care Product": (4.00, 15.00),
    "Floor Wax Stripper": (8.00, 35.00),
    "Floor Finish / Polish": (6.00, 30.00),
    "Carpet Cleaner (Extraction)": (6.00, 28.00),
    "Carpet Cleaner (Encapsulation)": (8.00, 35.00),
    "Disinfectant (Spray)": (6.00, 25.00),
    "Disinfectant (Concentrate)": (8.00, 40.00),
    "Sanitizer (Food Contact)": (5.00, 22.00),
    "Air Freshener (Spray)": (4.00, 18.00),
    "Air Freshener (Liquid/Wick)": (3.00, 12.00),
    "Metal Polish/Cleanser": (8.00, 30.00),
    "Furniture Maintenance Product": (5.00, 25.00),
    "Oven/Grill Cleaner": (8.00, 35.00),
    "Laundry Detergent (Institutional)": (4.00, 20.00),
    "Fabric Softener (Institutional)": (3.00, 15.00),
    "Spot Remover": (6.00, 30.00),
    "Dust Suppressant": (4.00, 18.00),
    "Adhesive Remover": (10.00, 40.00),
    "Graffiti Remover": (12.00, 50.00),
    "Heavy-Duty Hand Cleaner": (5.00, 20.00),
    "Stainless Steel Cleaner": (6.00, 25.00),
}

# Series identifiers for product naming
SERIES = ["100", "200", "300", "500", "700", "1000", "HD", "EC", "GS", "LV",
           "Ultra", "Plus", "Max", "Pro", "Elite", "Select"]

# Certifications and their VOC thresholds
CERT_THRESHOLDS = {
    "Green Seal GS-37": lambda cat, voc: voc <= {
        "General Purpose Cleaner": 4.0, "Glass Cleaner": 4.0,
        "Bathroom and Tile Cleaner": 5.0, "Carpet Cleaner (Extraction)": 3.0,
    }.get(cat, 10.0),
    "UL ECOLOGO": lambda cat, voc: voc <= 15.0,
    "EPA Safer Choice": lambda cat, voc: voc <= {
        "General Purpose Cleaner": 7.0, "Glass Cleaner": 7.0,
        "Disinfectant (Spray)": 45.0, "Disinfectant (Concentrate)": 10.0,
    }.get(cat, 20.0),
    "UL GREENGUARD Gold": lambda cat, voc: voc <= 5.0,
    "LEED v4 Compliant": lambda cat, voc: voc <= 10.0,
}

# Healthcare facility types
FACILITY_TYPES = [
    "Acute Care Hospital",
    "Long-Term Care Home",
    "Community Health Centre",
    "Dental Clinic",
    "Outpatient Surgery Centre",
    "Psychiatric Facility",
    "Rehabilitation Centre",
    "Medical Office Building",
    "Emergency Department",
    "Diagnostic Imaging Centre",
]


def load_regulatory_limits():
    """Load Dataset A to compute per-jurisdiction compliance."""
    limits = {}
    with open(LIMITS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["jurisdiction_code"], row["product_category"])
            limits[key] = float(row["voc_limit_g_per_L"])
    return limits


def generate_product_id(mfr, name):
    """Generate a stable product ID from manufacturer and name."""
    h = hashlib.md5(f"{mfr}:{name}".encode()).hexdigest()[:8]
    return f"PROD-{h.upper()}"


def generate_dataset():
    """Generate the full product compliance matrix CSV."""
    reg_limits = load_regulatory_limits()
    jurisdiction_codes = sorted(set(k[0] for k in reg_limits.keys()))

    rows = []
    row_id = 1

    for category, templates in PRODUCT_TEMPLATES.items():
        voc_min, voc_max = VOC_RANGES[category]
        dilution_options = DILUTION_RANGES[category]
        coverage_min, coverage_max = COVERAGE_RANGES[category]
        price_min, price_max = PRICE_RANGES[category]

        # Generate ~240 products per category (30 manufacturers * 8 templates avg
        # but we pick a subset for each)
        products_per_category = max(200, len(templates) * len(MANUFACTURERS) // 2)

        for i in range(products_per_category):
            mfr = random.choice(MANUFACTURERS)
            template = random.choice(templates)
            series = random.choice(SERIES)
            product_name = template.format(mfr=mfr, series=series)

            # VOC content — weighted toward lower values (market trend)
            voc_raw = random.triangular(voc_min, voc_max, voc_min + (voc_max - voc_min) * 0.25)
            voc_content = round(voc_raw, 1)

            # Dilution
            dilution = random.choice(dilution_options)
            if dilution == (0, 0):
                dilution_str = "RTU (Ready-to-Use)"
                dilution_ratio = 1.0
            else:
                dilution_str = f"1:{dilution[1]}"
                dilution_ratio = 1.0 / (1.0 + dilution[1])

            # Effective VOC after dilution
            effective_voc = round(voc_content * dilution_ratio, 2)

            # Coverage
            if coverage_min == 0 and coverage_max == 0:
                coverage = 0
            else:
                coverage = round(random.uniform(coverage_min, coverage_max))

            # Price
            price = round(random.uniform(price_min, price_max), 2)

            # Certifications
            certs = []
            for cert_name, check_fn in CERT_THRESHOLDS.items():
                if check_fn(category, voc_content) and random.random() < 0.7:
                    certs.append(cert_name)

            # Healthcare approval (products with VOC <= 10 g/L and at least one cert)
            healthcare_approved = voc_content <= 10.0 and len(certs) >= 1

            # Recommended facility types
            if healthcare_approved:
                n_facilities = random.randint(3, len(FACILITY_TYPES))
                recommended_facilities = random.sample(FACILITY_TYPES, n_facilities)
            else:
                recommended_facilities = []

            # Per-jurisdiction compliance
            compliant_jurisdictions = []
            non_compliant_jurisdictions = []
            for jcode in jurisdiction_codes:
                key = (jcode, category)
                if key in reg_limits:
                    limit = reg_limits[key]
                    if voc_content <= limit:
                        compliant_jurisdictions.append(jcode)
                    else:
                        non_compliant_jurisdictions.append(jcode)

            product_id = generate_product_id(mfr, product_name + str(i))

            # DIN/NPN for disinfectants (Canadian Drug Identification Number)
            din_npn = ""
            if "Disinfectant" in category or "Sanitizer" in category:
                din_npn = f"DIN {random.randint(2200000, 2299999):08d}"

            # SDS availability
            sds_available = random.random() < 0.92

            rows.append({
                "id": row_id,
                "product_id": product_id,
                "product_name": product_name,
                "manufacturer": mfr,
                "product_category": category,
                "voc_content_g_per_L": voc_content,
                "effective_voc_diluted_g_per_L": effective_voc,
                "dilution_ratio": dilution_str,
                "coverage_sqft_per_L": coverage if coverage > 0 else "",
                "price_per_litre_cad": price,
                "certifications": "; ".join(certs) if certs else "None",
                "healthcare_approved": "Yes" if healthcare_approved else "No",
                "recommended_facility_types": "; ".join(recommended_facilities) if recommended_facilities else "",
                "compliant_jurisdiction_count": len(compliant_jurisdictions),
                "total_jurisdictions_checked": len(compliant_jurisdictions) + len(non_compliant_jurisdictions),
                "compliant_jurisdictions": "; ".join(compliant_jurisdictions),
                "non_compliant_jurisdictions": "; ".join(non_compliant_jurisdictions),
                "din_npn": din_npn,
                "sds_available": "Yes" if sds_available else "No",
                "voc_classification": (
                    "Zero VOC" if voc_content == 0.0
                    else "Ultra-Low VOC" if voc_content <= 5.0
                    else "Low VOC" if voc_content <= 50.0
                    else "Standard"
                ),
                "ipac_compatible": "Yes" if voc_content <= 10.0 else "Conditional" if voc_content <= 25.0 else "No",
                "green_seal_eligible": "Yes" if any("Green Seal" in c for c in certs) else "No",
            })
            row_id += 1

    # Shuffle for more natural ordering
    random.shuffle(rows)
    # Reassign IDs after shuffle
    for i, row in enumerate(rows):
        row["id"] = i + 1

    # Write CSV
    fieldnames = [
        "id", "product_id", "product_name", "manufacturer", "product_category",
        "voc_content_g_per_L", "effective_voc_diluted_g_per_L", "dilution_ratio",
        "coverage_sqft_per_L", "price_per_litre_cad", "certifications",
        "healthcare_approved", "recommended_facility_types",
        "compliant_jurisdiction_count", "total_jurisdictions_checked",
        "compliant_jurisdictions", "non_compliant_jurisdictions",
        "din_npn", "sds_available", "voc_classification", "ipac_compatible",
        "green_seal_eligible",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {OUTPUT_FILE}")

    # Summary stats
    healthcare_count = sum(1 for r in rows if r["healthcare_approved"] == "Yes")
    cert_count = sum(1 for r in rows if r["certifications"] != "None")
    print(f"  Healthcare-approved products: {healthcare_count} ({healthcare_count*100//len(rows)}%)")
    print(f"  Products with certifications: {cert_count} ({cert_count*100//len(rows)}%)")
    return len(rows)


if __name__ == "__main__":
    count = generate_dataset()
    print(f"\nDataset B complete: {count} product records.")
