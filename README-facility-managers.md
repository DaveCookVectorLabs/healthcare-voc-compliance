# VOC Compliance Guide for Healthcare Facility Managers

This guide explains how to use the datasets in this repository to check whether your cleaning products meet VOC regulations in your jurisdiction.

---

## What Are VOCs?

Volatile Organic Compounds (VOCs) are chemicals that evaporate at room temperature. Many cleaning products contain VOCs as solvents. In healthcare settings, VOC exposure is a concern because patients — especially those who are immunocompromised, post-surgical, or in neonatal care — are more sensitive to airborne chemical exposure than healthy adults.

Regulations limit how much VOC a cleaning product can contain, measured in grams per litre (g/L).

---

## Which Regulations Apply to You?

Regulations are set at multiple levels. Your facility must comply with the **most restrictive** applicable regulation:

### United States

- **All states**: EPA federal limits (40 CFR Part 59 Subpart C) apply as a baseline.
- **California**: CARB limits are significantly stricter than federal. If you operate in California, check CARB limits specifically.
- **OTC states** (CT, DE, ME, MD, MA, NH, NJ, NY, PA, RI, VA, DC): These states adopted limits between EPA and CARB.
- **Other regulated states**: MI, CO, IL, IN, IA, OH, UT, WA each have their own limits.

### Canada

- **All provinces**: Federal SOR/2021-268 limits apply nationally. These are comparable to California CARB limits.
- **Ontario, BC, Quebec**: May have additional provincial requirements.

---

## How to Check a Product

1. **Find the product's VOC content** on its Safety Data Sheet (SDS), typically in Section 9 (Physical and Chemical Properties) or Section 15 (Regulatory Information). Look for "VOC content," "Total VOC," or "VOC as applied."

2. **Identify the product category** — e.g., "General Purpose Cleaner," "Disinfectant (Spray)," "Glass Cleaner."

3. **Look up the limit** in `datasets/voc_regulatory_limits.csv` for your jurisdiction and product category.

4. **Compare**: If the product's VOC content (g/L) is less than or equal to the limit, it is compliant in that jurisdiction.

### Example

Your facility in Ontario uses a general purpose cleaner with a VOC content of 6.0 g/L.

- Canada Federal (SOR/2021-268) limit for General Purpose Cleaner: **4.0 g/L**
- Ontario limit: **4.0 g/L**
- This product is **not compliant** in Ontario (6.0 > 4.0).

The same product would be compliant under US EPA federal limits (10.0 g/L) but not in California (4.0 g/L) or OTC states (7.0 g/L).

---

## Using the Product Dataset

The file `datasets/healthcare_cleaning_products_voc.csv` contains 5,000 cleaning products with pre-computed compliance flags. You can:

- Filter by `product_category` to find products in the category you need
- Filter by `healthcare_approved = Yes` to see only healthcare-suitable products
- Check the `compliant_jurisdictions` column to see which jurisdictions a product meets
- Sort by `voc_content_g_per_L` to find the lowest-VOC options
- Filter by `certifications` for specific standards (Green Seal GS-37, UL GREENGUARD Gold, etc.)

### Key Columns

| Column | Description |
|--------|-------------|
| `voc_content_g_per_L` | VOC content of the concentrate |
| `effective_voc_diluted_g_per_L` | VOC content after dilution |
| `healthcare_approved` | "Yes" if VOC ≤ 10 g/L and at least one certification |
| `ipac_compatible` | "Yes" (≤10 g/L), "Conditional" (≤25 g/L), or "No" |
| `compliant_jurisdiction_count` | Number of jurisdictions where the product is compliant |
| `certifications` | Third-party certifications held |

---

## Certification Standards

| Certification | What It Means |
|--------------|---------------|
| **Green Seal GS-37** | Meets industrial/institutional cleaning product standard including VOC limits tied to CARB |
| **UL GREENGUARD Gold** | Low total VOC emissions (≤5 g/L) — designed for sensitive environments including healthcare |
| **EPA Safer Choice** | Ingredients meet EPA safety criteria; VOC limits per CARB/OTC |
| **UL ECOLOGO** | Environmental sustainability certification including VOC limits |
| **LEED v4 Compliant** | Meets LEED low-emitting materials credit requirements |

---

## IPAC Considerations

IPAC (Infection Prevention and Control) protocols in Canadian healthcare facilities require cleaning products that are both effective against nosocomial pathogens (C. difficile, MRSA, VRE) and safe for vulnerable patient populations. VOC compliance is one part of this — the product must also have an appropriate kill spectrum and contact time.

The `ipac_compatible` field in the product dataset indicates whether the product's VOC level is suitable for IPAC-governed spaces, but does not evaluate antimicrobial efficacy. Always verify the product's DIN (Drug Identification Number) for disinfection claims.

---

## Further Reading

- [EPA Consumer Products VOC Standards](https://www.epa.gov/stationary-sources-air-pollution/consumer-products-national-volatile-organic-compound-emission)
- [Canada VOC Regulations (SOR/2021-268)](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2021-268/FullText.html)
- [CARB Consumer Products Program](https://ww2.arb.ca.gov/our-work/programs/consumer-products-program/about)
- [Green Seal GS-37 Standard](https://greenseal.org/standards/gs-37-cleaning-products-for-industrial-and-institutional-use/)
- [OSHA Permissible Exposure Limits](https://www.osha.gov/annotated-pels/table-z-1)

---

Maintained by Dave Cook — [Binx Professional Cleaning](https://www.binx.ca/commercial.php), North Bay and Sudbury, Ontario.
