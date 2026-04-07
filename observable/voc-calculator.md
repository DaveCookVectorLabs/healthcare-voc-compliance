# Healthcare VOC Compliance Calculator

Interactive VOC exposure calculator for healthcare facility cleaning products. Select a jurisdiction, product category, and input your room parameters to calculate steady-state VOC concentration and regulatory compliance.

Data sources: EPA 40 CFR Part 59, CARB, Canada SOR/2021-268, OSHA 29 CFR 1910.1000, ASHRAE 62.1-2022.

---

## Jurisdiction and Product Selection

```js
viewof jurisdiction = Inputs.select(
  ["US-FED", "US-CA", "US-NY", "US-MI", "CA-FED", "CA-ON", "CA-BC"],
  {label: "Jurisdiction", value: "CA-FED"}
)
```

```js
viewof product_category = Inputs.select(
  ["General Purpose Cleaner", "Glass Cleaner", "Disinfectant (Spray)",
   "Disinfectant (Concentrate)", "Bathroom and Tile Cleaner",
   "Floor Wax Stripper", "Floor Finish / Polish", "Carpet Cleaner (Extraction)",
   "Sanitizer (Food Contact)", "Air Freshener (Spray)", "Laundry Detergent (Institutional)"],
  {label: "Product Category", value: "General Purpose Cleaner"}
)
```

## Room Parameters

```js
viewof room_sqft = Inputs.range([50, 2000], {label: "Room area (sqft)", step: 10, value: 200})
viewof ceiling_ft = Inputs.range([7, 20], {label: "Ceiling height (ft)", step: 0.5, value: 9})
viewof product_voc = Inputs.range([0, 70], {label: "Product VOC (g/L concentrate)", step: 0.5, value: 8})
viewof dilution = Inputs.select(
  [["RTU (undiluted)", 1.0], ["1:16", 1/17], ["1:32", 1/33], ["1:64", 1/65], ["1:128", 1/129], ["1:256", 1/257]],
  {label: "Dilution ratio", value: ["1:64", 1/65], format: d => d[0]}
)
viewof coverage = Inputs.range([50, 1000], {label: "Coverage (sqft/L)", step: 10, value: 400})
viewof ach = Inputs.range([0, 25], {label: "Air changes/hour (ACH)", step: 0.5, value: 6})
viewof freq = Inputs.range([1, 730], {label: "Cleaning frequency (per year)", step: 1, value: 365})
```

## Results

```js
{
  const SQFT_TO_SQM = 0.09290304;
  const FT_TO_M = 0.3048;
  const OSHA_PEL = 300.0;

  const room_vol = room_sqft * SQFT_TO_SQM * ceiling_ft * FT_TO_M;
  const eff_voc = product_voc * dilution[1];
  const applied = room_sqft / coverage;
  const total_mg = eff_voc * applied * 1000;
  const emission = total_mg / 0.5;
  const vent = ach * room_vol;
  const ss = vent > 0 ? emission / vent : total_mg / room_vol;
  const pel_pct = (ss / OSHA_PEL) * 100;

  const target = OSHA_PEL * 0.1;
  const reentry = ss <= target ? 0 : ach > 0 ? Math.log(ss / target) / ach * 60 : -1;
  const annual_kg = (eff_voc * applied * freq) / 1000;

  // VOC limits by jurisdiction (general purpose cleaner as reference)
  const limits = {
    "US-FED": {"General Purpose Cleaner": 10, "Glass Cleaner": 12, "Disinfectant (Spray)": 60, "Disinfectant (Concentrate)": 15},
    "US-CA": {"General Purpose Cleaner": 4, "Glass Cleaner": 4, "Disinfectant (Spray)": 35, "Disinfectant (Concentrate)": 8},
    "US-NY": {"General Purpose Cleaner": 7, "Glass Cleaner": 7, "Disinfectant (Spray)": 45, "Disinfectant (Concentrate)": 10},
    "US-MI": {"General Purpose Cleaner": 5, "Glass Cleaner": 5, "Disinfectant (Spray)": 38, "Disinfectant (Concentrate)": 9},
    "CA-FED": {"General Purpose Cleaner": 4, "Glass Cleaner": 4, "Disinfectant (Spray)": 35, "Disinfectant (Concentrate)": 8},
    "CA-ON": {"General Purpose Cleaner": 4, "Glass Cleaner": 4, "Disinfectant (Spray)": 35, "Disinfectant (Concentrate)": 8},
    "CA-BC": {"General Purpose Cleaner": 4, "Glass Cleaner": 4, "Disinfectant (Spray)": 35, "Disinfectant (Concentrate)": 8},
  };

  const limit = limits[jurisdiction]?.[product_category] ?? "N/A";
  const compliant = typeof limit === "number" ? product_voc <= limit : "Unknown";

  return md`
### Calculation Results

| Metric | Value |
|--------|-------|
| Room volume | ${room_vol.toFixed(1)} m³ |
| Effective VOC (diluted) | ${eff_voc.toFixed(4)} g/L |
| Product applied | ${applied.toFixed(3)} L |
| Total VOC released | ${total_mg.toFixed(1)} mg |
| **Steady-state concentration** | **${ss.toFixed(2)} mg/m³** |
| **OSHA PEL usage** | **${pel_pct.toFixed(2)}%** |
| Time to safe reentry | ${reentry >= 0 ? reentry.toFixed(1) + " min" : "N/A (no ventilation)"} |
| Annual VOC load | ${annual_kg.toFixed(4)} kg/year |
| Jurisdiction limit | ${limit} g/L |
| **Compliant** | **${compliant === true ? "✓ Yes" : compliant === false ? "✗ No" : "Unknown"}** |
  `;
}
```

---

## ASHRAE 62.1 Healthcare Ventilation Reference

```js
{
  const ashrae = [
    ["Patient Room", 6], ["ICU", 12], ["Operating Room", 20],
    ["Exam Room", 6], ["Corridor", 4], ["Laboratory", 12],
    ["Dietary Kitchen", 10], ["Pharmacy", 8], ["Bathroom", 10],
    ["Janitor Closet", 10], ["General Office", 4]
  ];
  return Inputs.table(ashrae.map(([space, min_ach]) => ({
    "Space Type": space,
    "Minimum ACH": min_ach,
    "Your ACH": ach,
    "Meets Minimum": ach >= min_ach ? "✓" : "✗"
  })));
}
```

---

Source code: [GitHub](https://github.com/DaveCookVectorLabs/healthcare-voc-compliance) |
Datasets: [Hugging Face](https://huggingface.co/datasets/davecook1985/healthcare-voc-compliance) |
PDF Guide: [VOC Compliance for Healthcare Facility Cleaning](https://www.binx.ca/guides/healthcare-voc-compliance-guide.pdf) |
Maintained by Dave Cook — [Binx Professional Cleaning](https://www.binx.ca/commercial.php)
