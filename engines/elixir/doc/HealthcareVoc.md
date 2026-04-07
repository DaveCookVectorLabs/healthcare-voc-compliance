# `HealthcareVoc`

Healthcare VOC Compliance Calculator — Elixir Engine

Calculates VOC exposure concentration per cleaning cycle based on product
VOC content, dilution ratio, coverage rate, room geometry, and ventilation.

Reference:
- OSHA 29 CFR 1910.1000 Table Z-1 (TVOC PEL: 300 mg/m³)
- ASHRAE 62.1-2022 (healthcare ventilation rates)
- EPA 40 CFR Part 59 Subpart C
- Canada SOR/2021-268

# `calculate`

Calculate VOC exposure for a single healthcare cleaning cycle.

## Parameters
- `room_sqft` - Room floor area in square feet
- `ceiling_height_ft` - Ceiling height in feet
- `product_voc_g_per_l` - Product VOC content (concentrate) in g/L
- `dilution_ratio` - Concentrate fraction (1.0 = RTU, 0.015625 = 1:64)
- `coverage_sqft_per_l` - Coverage area per litre of applied solution
- `air_changes_per_hour` - Ventilation rate (ACH)
- `cleaning_frequency_per_year` - Number of cleaning cycles per year
- `space_type` - Healthcare space type for ASHRAE reference

## Returns
Map with calculation results and compliance data.

---

*Consult [api-reference.md](api-reference.md) for complete listing*
