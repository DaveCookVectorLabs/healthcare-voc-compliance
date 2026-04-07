# Healthcare VOC Compliance Calculator

[![PyPI version](https://badge.fury.io/py/healthcare-voc-compliance.svg)](https://pypi.org/project/healthcare-voc-compliance/)
[![npm version](https://badge.fury.io/js/%40davecook%2Fhealthcare-voc-compliance.svg)](https://www.npmjs.com/package/@davecook/healthcare-voc-compliance)
[![Crates.io](https://img.shields.io/crates/v/healthcare-voc-engine.svg)](https://crates.io/crates/healthcare-voc-engine)
[![Gem Version](https://badge.fury.io/rb/healthcare_voc_compliance.svg)](https://rubygems.org/gems/healthcare_voc_compliance)
[![Hex.pm](https://img.shields.io/hexpm/v/healthcare_voc.svg)](https://hex.pm/packages/healthcare_voc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source calculator and dataset collection for evaluating VOC (Volatile Organic Compound) exposure from cleaning products used in healthcare facilities. Covers 26 jurisdictions across the United States and Canada.

---

## What This Does

Given a cleaning product's VOC content, a room's geometry, and ventilation parameters, this tool calculates:

- **VOC concentration** (mg/m³) at steady state during a cleaning cycle
- **OSHA PEL comparison** — what percentage of the Permissible Exposure Limit the concentration represents
- **Time to safe reentry** — how long until VOC concentration drops below 10% of PEL
- **Annual VOC load** — total VOC released per year at the given cleaning frequency
- **Multi-jurisdiction compliance** — whether the product meets VOC limits in each of 26 jurisdictions

---

## Datasets

Two CSV datasets are included in `datasets/`:

### Dataset A: VOC Regulatory Limits by Jurisdiction (650 rows)

VOC limits (g/L) for 25 cleaning product categories across 26 jurisdictions:

- US Federal (EPA 40 CFR Part 59 Subpart C)
- California (CARB Consumer Products Regulations)
- 12 OTC states (CT, DE, ME, MD, MA, NH, NJ, NY, PA, RI, VA, DC)
- 8 states with independent regulations (MI, CO, IL, IN, IA, OH, UT, WA)
- Canada Federal (SOR/2021-268)
- Ontario, British Columbia, Quebec

Each row includes the product category, numeric VOC limit, regulation name, effective date, and healthcare-specific context notes.

### Dataset B: Healthcare Cleaning Product VOC Compliance Matrix (5,000 rows)

Synthetic product data modeled on real institutional cleaning product categories:

- VOC content (g/L concentrate and effective diluted)
- Certifications (Green Seal GS-37, UL ECOLOGO, EPA Safer Choice, UL GREENGUARD Gold, LEED v4)
- Per-jurisdiction compliance flags (compliant/non-compliant in each of 26 jurisdictions)
- Healthcare approval status, IPAC compatibility rating
- Pricing (CAD/litre), dilution ratios, coverage rates
- Recommended healthcare facility types

---

## Calculation Model

```
effective_voc     = product_voc_g_per_L × dilution_ratio
product_applied_L = room_sqft / coverage_sqft_per_L
total_voc_mg      = effective_voc × product_applied_L × 1000

# Single-zone mass balance with ventilation
emission_rate     = total_voc_mg / cleaning_duration_hr
ventilation_rate  = air_changes_per_hour × room_volume_m3
steady_state      = emission_rate / ventilation_rate

osha_pel_percent  = (steady_state / 300) × 100
```

ASHRAE 62.1-2022 minimum ventilation rates for healthcare spaces are built in as reference values:

| Space Type | Minimum ACH |
|-----------|------------|
| Patient room | 6 |
| ICU | 12 |
| Operating room | 20 |
| Exam room | 6 |
| Corridor | 4 |
| Laboratory | 12 |
| Dietary kitchen | 10 |

---

## Engines

The calculation is implemented in seven languages. Each exposes `/calculate` (POST) and `/health` (GET) REST endpoints:

| Language | Directory | Package |
|----------|-----------|---------|
| Python (FastAPI) | `engines/python/` | `healthcare-voc-compliance` on PyPI |
| Rust | `engines/rust/` | `healthcare-voc-engine` on Crates.io |
| Java | `engines/java/` | `io.github.davecookvectorlabs:healthcare-voc-engine` on Maven Central |
| Ruby (Sinatra) | `engines/ruby/` | `healthcare_voc_compliance` on RubyGems |
| Elixir (Plug) | `engines/elixir/` | `healthcare_voc` on Hex.pm |
| PHP | `engines/php/` | `davecook/healthcare-voc-compliance` on Packagist |
| Go (net/http) | `engines/go/` | `github.com/DaveCookVectorLabs/healthcare-voc-compliance` on pkg.go.dev |

### Quick Start (Python)

```bash
pip install healthcare-voc-compliance
# or run from source:
cd engines/python
pip install -r requirements.txt
python engine.py          # CLI mode — runs sample calculation
python engine.py --serve  # HTTP server on port 8001
```

### API Example

```bash
curl -X POST http://localhost:8001/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "room_sqft": 200,
    "ceiling_height_ft": 9,
    "product_voc_g_per_L": 8.0,
    "dilution_ratio": 0.015625,
    "coverage_sqft_per_L": 400,
    "air_changes_per_hour": 6,
    "cleaning_frequency_per_year": 365,
    "product_category": "General Purpose Cleaner",
    "space_type": "patient_room"
  }'
```

---

## Regulatory Sources

- [EPA 40 CFR Part 59 Subpart C](https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-59/subpart-C) — US federal VOC emission standards for consumer products
- [CARB Consumer Products Program](https://ww2.arb.ca.gov/our-work/programs/consumer-products-program/about) — California VOC limits
- [Canada SOR/2021-268](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2021-268/FullText.html) — Federal VOC concentration limits
- [OSHA 29 CFR 1910.1000 Table Z-1](https://www.osha.gov/annotated-pels/table-z-1) — Permissible Exposure Limits
- [ASHRAE 62.1-2022](https://www.ashrae.org/technical-resources/bookstore/standards-62-1-62-2) — Ventilation for healthcare facilities
- [Green Seal GS-37](https://greenseal.org/standards/gs-37-cleaning-products-for-industrial-and-institutional-use/) — Institutional cleaning product standard
- [UL GREENGUARD Gold](https://www.ul.com/services/ul-greenguard-certification) — Low-emission certification for sensitive environments
- [EPA Safer Choice](https://www.epa.gov/saferchoice) — Product certification program

---

## Project Structure

```
healthcare-voc-compliance/
├── datasets/
│   ├── generate_regulatory_limits.py     # Dataset A generator
│   ├── generate_product_matrix.py        # Dataset B generator
│   ├── voc_regulatory_limits.csv         # 650 regulatory limits
│   └── healthcare_cleaning_products_voc.csv  # 5,000 products
├── engines/
│   ├── python/engine.py                  # Python (FastAPI)
│   ├── rust/src/main.rs                  # Rust
│   ├── java/src/.../VOCCalculator.java   # Java
│   ├── ruby/lib/healthcare_voc_compliance.rb  # Ruby
│   ├── elixir/lib/healthcare_voc.ex      # Elixir
│   ├── php/src/VOCCalculator.php         # PHP
│   └── go/main.go                        # Go
├── notebooks/
│   └── voc_compliance_analysis.ipynb     # Jupyter analysis notebook
├── pdfs/
│   └── generate_pdfs.py                  # PDF white paper generator
├── docs/                                 # Sphinx documentation
└── public/                               # PHP web frontend
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

Maintained by Dave Cook — [Binx Professional Cleaning](https://www.binx.ca/commercial.php), North Bay and Sudbury, Ontario.
