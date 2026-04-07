Healthcare VOC Compliance Calculator
=====================================

An open-source calculator and dataset collection for evaluating VOC (Volatile Organic
Compound) exposure from cleaning products used in healthcare facilities. Covers 26
jurisdictions across the United States and Canada.

.. contents:: Table of Contents
   :depth: 2
   :local:

Overview
--------

This tool calculates VOC exposure concentration per cleaning cycle and checks regulatory
compliance across 26 jurisdictions. It is designed for healthcare facility managers who
need to verify that their cleaning products meet applicable VOC limits.

**Datasets included:**

* **VOC Regulatory Limits** — 650 records covering 25 product categories across 26 jurisdictions
* **Healthcare Cleaning Products** — 5,000 products with VOC content, certifications, and compliance flags

**Calculation engines** are implemented in Python, Rust, Java, Ruby, Elixir, PHP, and Go.

Installation
------------

Python
^^^^^^

.. code-block:: bash

   pip install healthcare-voc-compliance

From source:

.. code-block:: bash

   git clone https://github.com/DaveCookVectorLabs/healthcare-voc-compliance.git
   cd healthcare-voc-compliance/engines/python
   pip install -r requirements.txt
   python engine.py          # CLI mode
   python engine.py --serve  # HTTP server on port 8001

Rust
^^^^

.. code-block:: bash

   cargo install healthcare-voc-engine

   # Or build from source:
   cd engines/rust
   cargo build --release
   ./target/release/healthcare-voc-engine --port 8001

API Reference
-------------

POST /calculate
^^^^^^^^^^^^^^^

Calculate VOC exposure for a single cleaning cycle.

**Request body (JSON):**

.. code-block:: json

   {
     "room_sqft": 200,
     "ceiling_height_ft": 9,
     "product_voc_g_per_L": 8.0,
     "dilution_ratio": 0.015625,
     "coverage_sqft_per_L": 400,
     "air_changes_per_hour": 6,
     "cleaning_frequency_per_year": 365,
     "product_category": "General Purpose Cleaner",
     "space_type": "patient_room"
   }

**Response:**

.. code-block:: json

   {
     "room_volume_m3": 50.97,
     "steady_state_concentration_mg_per_m3": 0.40,
     "osha_pel_percent": 0.13,
     "time_to_safe_reentry_minutes": 0.0,
     "annual_voc_load_kg": 0.0225,
     "compliant_jurisdictions": ["US-FED", "US-CA", "..."],
     "warnings": []
   }

GET /health
^^^^^^^^^^^

Returns engine status and version information.

Calculation Model
-----------------

The steady-state VOC concentration during a cleaning cycle is calculated using a
single-zone mass balance model:

.. code-block:: text

   effective_VOC     = product_VOC × dilution_ratio
   product_applied   = room_sqft ÷ coverage_rate
   total_VOC_mg      = effective_VOC × product_applied × 1000
   emission_rate     = total_VOC_mg ÷ cleaning_duration_hr
   steady_state      = emission_rate ÷ (ACH × room_volume_m³)
   osha_pel_percent  = (steady_state ÷ 300) × 100

The OSHA Total VOC PEL of 300 mg/m³ is used as the reference threshold
(29 CFR 1910.1000, Table Z-1).

ASHRAE 62.1-2022 minimum ventilation rates are built in for healthcare space types.

Regulatory Sources
------------------

* EPA 40 CFR Part 59, Subpart C
* CARB Consumer Products Regulations (Title 17 CCR §94507-94517)
* Canada SOR/2021-268 (VOC Concentration Limits)
* OSHA 29 CFR 1910.1000, Table Z-1
* ASHRAE 62.1-2022
* Green Seal GS-37, UL GREENGUARD Gold, EPA Safer Choice

License
-------

MIT License. See `LICENSE <https://github.com/DaveCookVectorLabs/healthcare-voc-compliance/blob/main/LICENSE>`_.

PDF Guide: `VOC Compliance for Healthcare Facility Cleaning <https://www.binx.ca/guides/healthcare-voc-compliance-guide.pdf>`_

Maintained by Dave Cook — `Binx Professional Cleaning <https://www.binx.ca/commercial.php>`_, North Bay and Sudbury, Ontario.
