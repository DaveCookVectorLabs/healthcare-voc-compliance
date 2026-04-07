#!/usr/bin/env python3
"""Generate branded PDF white paper for Healthcare VOC Compliance."""

import os
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)

# Binx brand colors
BRAND_BLACK = HexColor('#141414')
AMBER = HexColor('#E87A2D')
AMBER_HOVER = HexColor('#D06A22')
AMBER_LIGHT = HexColor('#FAEEDA')
AMBER_DARK = HexColor('#854F0B')
WARM_GRAY_100 = HexColor('#F5F3EF')
WARM_GRAY_300 = HexColor('#D4D0C8')
WARM_GRAY_500 = HexColor('#7A7168')
WARM_GRAY_600 = HexColor('#5C5448')
HERO_BG = HexColor('#1E1E1E')
WHITE_BG = HexColor('#FAFAF8')

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def link(url, text=None):
    label = text or url
    return f'<a href="{url}" color="#E87A2D">{label}</a>'


LINK_BINX = link('https://www.binx.ca/commercial.php', 'Binx Professional Cleaning')
LINK_GITHUB = link('https://github.com/DaveCookVectorLabs/healthcare-voc-compliance', 'GitHub')
LINK_PYPI = link('https://pypi.org/project/healthcare-voc-compliance/', 'PyPI')
LINK_HF = link('https://huggingface.co/datasets/davecook1985/healthcare-voc-compliance', 'Hugging Face')


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'BinxTitle', parent=styles['Title'],
        fontSize=24, leading=30, textColor=BRAND_BLACK,
        spaceAfter=6, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'BinxSubtitle', parent=styles['Normal'],
        fontSize=13, leading=18, textColor=WARM_GRAY_500,
        spaceAfter=20, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'BinxH1', parent=styles['Heading1'],
        fontSize=18, leading=24, textColor=AMBER_HOVER,
        spaceBefore=20, spaceAfter=10, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'BinxH2', parent=styles['Heading2'],
        fontSize=14, leading=20, textColor=BRAND_BLACK,
        spaceBefore=14, spaceAfter=8, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'BinxBody', parent=styles['Normal'],
        fontSize=10.5, leading=16, textColor=BRAND_BLACK,
        alignment=TA_JUSTIFY, spaceAfter=8, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'BinxCaption', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=WARM_GRAY_500,
        alignment=TA_CENTER, spaceAfter=12, fontName='Helvetica-Oblique'
    ))
    styles.add(ParagraphStyle(
        'BinxFooter', parent=styles['Normal'],
        fontSize=8, leading=11, textColor=WARM_GRAY_500,
        alignment=TA_CENTER, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'BinxBullet', parent=styles['Normal'],
        fontSize=10.5, leading=16, textColor=BRAND_BLACK,
        leftIndent=20, spaceAfter=4, fontName='Helvetica',
        bulletIndent=8
    ))
    return styles


def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AMBER),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEADING', (0, 0), (-1, -1), 13),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, WARM_GRAY_300),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE_BG, WARM_GRAY_100]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(style)
    return tbl


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(WARM_GRAY_500)
    canvas.drawCentredString(
        letter[0] / 2, 0.5 * inch,
        f"VOC Compliance for Healthcare Facility Cleaning — Binx Professional Cleaning — www.binx.ca — Page {doc.page}"
    )
    canvas.restoreState()


def generate_healthcare_voc_pdf():
    """Generate the main healthcare VOC compliance white paper."""
    filename = os.path.join(OUT_DIR, "healthcare-voc-compliance-guide.pdf")
    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch
    )
    s = get_styles()
    story = []

    # Title page
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph(
        "VOC Compliance for Healthcare<br/>Facility Cleaning",
        s['BinxTitle']
    ))
    story.append(Paragraph(
        "A Regulatory Reference Guide for Canadian and US Facility Managers",
        s['BinxSubtitle']
    ))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "Dave Cook<br/>Binx Professional Cleaning<br/>North Bay and Sudbury, Ontario<br/>dave@binx.ca",
        s['BinxBody']
    ))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f"Open-source tools and datasets: {LINK_GITHUB}<br/>"
        f"Python package: {LINK_PYPI}<br/>"
        f"Datasets: {LINK_HF}",
        s['BinxBody']
    ))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "Published April 2026 — CC-BY 4.0",
        s['BinxCaption']
    ))
    story.append(PageBreak())

    # Section 1: Introduction
    story.append(Paragraph("1. Introduction", s['BinxH1']))
    story.append(Paragraph(
        "Volatile Organic Compounds (VOCs) in cleaning products are regulated across North American "
        "jurisdictions to limit ground-level ozone formation and protect indoor air quality. Healthcare "
        "facilities face heightened scrutiny because patient populations — including immunocompromised, "
        "post-surgical, and neonatal patients — are disproportionately affected by airborne chemical exposure.",
        s['BinxBody']
    ))
    story.append(Paragraph(
        "This guide provides facility managers with a reference framework for understanding and "
        "navigating VOC regulations as they apply to institutional cleaning products used in hospitals, "
        "long-term care homes, clinics, and other healthcare settings. It covers 26 jurisdictions across "
        "the United States and Canada, with specific attention to product categories commonly used in "
        "healthcare environments.",
        s['BinxBody']
    ))
    story.append(Paragraph(
        "Accompanying this guide are two open datasets: (1) 650 regulatory limit records across 26 "
        "jurisdictions and 25 product categories, and (2) 5,000 healthcare cleaning products with "
        "VOC content, certifications, and per-jurisdiction compliance flags. Both datasets are freely "
        "available under a CC-BY 4.0 license.",
        s['BinxBody']
    ))

    # Section 2: Regulatory Landscape
    story.append(Paragraph("2. Regulatory Landscape", s['BinxH1']))
    story.append(Paragraph("2.1 United States Federal — EPA", s['BinxH2']))
    story.append(Paragraph(
        "The US Environmental Protection Agency regulates VOC emissions from consumer and institutional "
        "products under 40 CFR Part 59, Subpart C (National Volatile Organic Compound Emission Standards "
        "for Consumer Products). These limits, originally promulgated in 1998 and last amended in 2009, "
        "set the baseline for all US jurisdictions. EPA limits are generally the most permissive in "
        "North America.",
        s['BinxBody']
    ))
    story.append(Paragraph("2.2 California — CARB", s['BinxH2']))
    story.append(Paragraph(
        "The California Air Resources Board (CARB) Consumer Products Regulations (Title 17 CCR "
        "§94507-94517) set the strictest VOC limits in the United States. CARB limits for general "
        "purpose cleaners (4.0 g/L) are less than half the EPA federal limit (10.0 g/L). CARB "
        "regulations were most recently amended in January 2023, with a phase-out of the 2% fragrance "
        "exemption. Due to California's market influence, many national manufacturers reformulate to "
        "meet CARB limits across all markets.",
        s['BinxBody']
    ))
    story.append(Paragraph("2.3 OTC States", s['BinxH2']))
    story.append(Paragraph(
        "Twelve states and the District of Columbia participate in the Ozone Transport Commission (OTC), "
        "which coordinates regional VOC regulations: Connecticut, Delaware, Maine, Maryland, Massachusetts, "
        "New Hampshire, New Jersey, New York, Pennsylvania, Rhode Island, Virginia, and DC. OTC limits "
        "fall between EPA federal and CARB — typically 5-7 g/L for general purpose cleaners.",
        s['BinxBody']
    ))
    story.append(Paragraph("2.4 Canada — Federal and Provincial", s['BinxH2']))
    story.append(Paragraph(
        "Canada's Volatile Organic Compound Concentration Limits for Certain Products Regulations "
        "(SOR/2021-268) came into force January 1, 2023, with manufacturing/import compliance "
        "required by January 1, 2024 (disinfectants: January 1, 2025). Federal limits broadly "
        "align with CARB Phase II. Ontario, British Columbia, and Quebec may impose additional "
        "provincial requirements. For healthcare facilities operating under provincial health "
        "legislation, both federal and provincial limits must be met.",
        s['BinxBody']
    ))

    # Section 3: Key limits table
    story.append(Paragraph("3. VOC Limits — Key Healthcare Product Categories", s['BinxH1']))
    story.append(Paragraph(
        "The following table summarizes VOC limits (g/L as applied) for the product categories "
        "most commonly used in healthcare facilities, across representative jurisdictions.",
        s['BinxBody']
    ))

    limits_table = make_table(
        ['Product Category', 'EPA Federal', 'CARB (CA)', 'OTC States', 'Canada Federal'],
        [
            ['General Purpose Cleaner', '10.0', '4.0', '7.0', '4.0'],
            ['Glass Cleaner', '12.0', '4.0', '7.0', '4.0'],
            ['Bathroom/Tile Cleaner', '12.0', '5.0', '7.0', '5.0'],
            ['Disinfectant (Spray)', '60.0', '35.0', '45.0', '35.0'],
            ['Disinfectant (Conc.)', '15.0', '8.0', '10.0', '8.0'],
            ['Floor Wax Stripper', '0.0', '0.0', '0.0', '0.0'],
            ['Floor Finish/Polish', '7.0', '3.0', '5.0', '3.0'],
            ['Carpet Cleaner (Ext.)', '10.0', '3.0', '5.0', '3.0'],
            ['Sanitizer (Food Contact)', '20.0', '10.0', '15.0', '10.0'],
            ['Air Freshener (Spray)', '30.0', '15.0', '20.0', '15.0'],
            ['Laundry Detergent', '8.0', '3.0', '5.0', '3.0'],
        ],
        col_widths=[2.2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.2*inch]
    )
    story.append(limits_table)
    story.append(Paragraph(
        "Source: EPA 40 CFR Part 59, CARB Title 17 CCR §94509, OTC Model Rule, Canada SOR/2021-268",
        s['BinxCaption']
    ))

    story.append(PageBreak())

    # Section 4: Exposure Calculation
    story.append(Paragraph("4. VOC Exposure Calculation Method", s['BinxH1']))
    story.append(Paragraph(
        "Regulatory limits control product formulation (VOC content per litre). However, actual "
        "occupant exposure depends on how the product is applied in a specific space. The calculation "
        "model used in the accompanying open-source tools considers five variables:",
        s['BinxBody']
    ))

    calc_table = make_table(
        ['Variable', 'Unit', 'Description'],
        [
            ['Product VOC content', 'g/L', 'As stated on SDS (Section 9 or 15)'],
            ['Dilution ratio', 'fraction', '1.0 for RTU; 0.0156 for 1:64'],
            ['Coverage rate', 'sqft/L', 'Area cleaned per litre of applied solution'],
            ['Room volume', 'm³', 'Floor area × ceiling height'],
            ['Air changes/hour (ACH)', 'ACH', 'ASHRAE 62.1 minimum for space type'],
        ],
        col_widths=[1.8*inch, 0.8*inch, 4.1*inch]
    )
    story.append(calc_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("4.1 Steady-State Model", s['BinxH2']))
    story.append(Paragraph(
        "The steady-state VOC concentration during a cleaning cycle is calculated using a "
        "single-zone mass balance model:",
        s['BinxBody']
    ))
    story.append(Paragraph(
        "<font face='Courier' size='10'>"
        "effective_VOC = product_VOC × dilution_ratio<br/>"
        "product_applied = room_sqft ÷ coverage_rate<br/>"
        "total_VOC_mg = effective_VOC × product_applied × 1000<br/>"
        "emission_rate = total_VOC_mg ÷ cleaning_duration_hr<br/>"
        "steady_state = emission_rate ÷ (ACH × room_volume_m³)"
        "</font>",
        s['BinxBody']
    ))
    story.append(Paragraph(
        "The result is compared against the OSHA Total VOC Permissible Exposure Limit "
        "(300 mg/m³ as TVOC, per 29 CFR 1910.1000 Table Z-1). Time to safe reentry is "
        "calculated as the time for concentration to decay below 10% of PEL via exponential "
        "ventilation decay.",
        s['BinxBody']
    ))

    # Section 5: ASHRAE
    story.append(Paragraph("5. ASHRAE 62.1 Ventilation Rates for Healthcare", s['BinxH1']))

    ashrae_table = make_table(
        ['Space Type', 'Minimum ACH', 'Notes'],
        [
            ['Patient Room', '6', 'Standard inpatient rooms'],
            ['ICU', '12', 'Intensive care, includes isolation'],
            ['Operating Room', '20', 'Surgical suites, positive pressure'],
            ['Exam Room', '6', 'Outpatient clinics'],
            ['Corridor', '4', 'Common circulation areas'],
            ['Laboratory', '12', 'Clinical and research labs'],
            ['Dietary Kitchen', '10', 'Food preparation areas'],
            ['Soiled Utility', '10', 'Contaminated materials handling'],
            ['Janitor Closet', '10', 'Chemical storage and mixing'],
            ['Pharmacy', '8', 'Drug preparation areas'],
            ['Bathroom', '10', 'Patient and staff washrooms'],
        ],
        col_widths=[2.0*inch, 1.2*inch, 3.5*inch]
    )
    story.append(ashrae_table)
    story.append(Paragraph(
        "Source: ASHRAE 62.1-2022, Table 6.2.2.1 — Healthcare Facilities",
        s['BinxCaption']
    ))

    story.append(PageBreak())

    # Section 6: Certifications
    story.append(Paragraph("6. Third-Party Certifications", s['BinxH1']))
    story.append(Paragraph(
        "Several third-party certification programs evaluate VOC content alongside broader "
        "environmental and health criteria. Healthcare facility managers can use these as "
        "screening tools when selecting products.",
        s['BinxBody']
    ))

    cert_table = make_table(
        ['Certification', 'VOC Threshold', 'Relevance to Healthcare'],
        [
            ['Green Seal GS-37', 'Tied to CARB limits', 'Primary standard for institutional cleaning products'],
            ['UL GREENGUARD Gold', '≤ 5 g/L total', 'Designed for sensitive environments (hospitals, nurseries)'],
            ['EPA Safer Choice', 'Per CARB/OTC limits', 'Transparent ingredient disclosure required'],
            ['UL ECOLOGO', '≤ 15 g/L', 'Broad environmental sustainability criteria'],
            ['LEED v4 Low-Emitting', '≤ 10 g/L', 'Required for LEED-certified healthcare buildings'],
        ],
        col_widths=[1.8*inch, 1.5*inch, 3.4*inch]
    )
    story.append(cert_table)

    # Section 7: IPAC
    story.append(Paragraph("7. IPAC Considerations for Canadian Healthcare Facilities", s['BinxH1']))
    story.append(Paragraph(
        "Infection Prevention and Control (IPAC) Canada protocols require cleaning products that "
        "are effective against nosocomial pathogens including C. difficile, MRSA, and VRE. VOC "
        "compliance is necessary but not sufficient — the product must also hold a valid Drug "
        "Identification Number (DIN) from Health Canada for any disinfection claims.",
        s['BinxBody']
    ))
    story.append(Paragraph(
        "Facility managers should evaluate products on both axes: (1) VOC compliance for the "
        "applicable jurisdiction, and (2) antimicrobial efficacy per IPAC guidelines. Products "
        "with VOC content ≤ 10 g/L and at least one third-party certification are flagged as "
        "'healthcare-approved' in the accompanying dataset. Products with VOC content ≤ 25 g/L "
        "are marked 'IPAC conditional' — suitable for non-clinical spaces but requiring review "
        "for patient care areas.",
        s['BinxBody']
    ))

    # Section 8: Case Study
    story.append(Paragraph("8. Case Study — Northern Ontario Healthcare Facility", s['BinxH1']))
    story.append(Paragraph(
        "A 120-bed long-term care home in North Bay, Ontario uses four primary cleaning products "
        "across its daily cleaning program. The facility must comply with Canada SOR/2021-268 "
        "(federal) and Ontario provincial requirements, which both set general purpose cleaner "
        "limits at 4.0 g/L.",
        s['BinxBody']
    ))

    case_table = make_table(
        ['Product', 'Category', 'VOC (g/L)', 'Compliant?', 'Action'],
        [
            ['GP-Clean 200', 'General Purpose', '3.2', 'Yes (all)', 'No change'],
            ['PathShield RTU', 'Disinfectant (Spray)', '28.0', 'Yes (all)', 'Monitor — near CARB limit'],
            ['CrystalView Pro', 'Glass Cleaner', '6.5', 'No (CA, Canada)', 'Replace with ≤ 4.0 g/L'],
            ['StripMaster Zero', 'Floor Stripper', '0.0', 'Yes (all)', 'No change'],
        ],
        col_widths=[1.5*inch, 1.3*inch, 1.0*inch, 1.3*inch, 1.6*inch]
    )
    story.append(case_table)
    story.append(Paragraph(
        "Using the VOC exposure calculator with the facility's patient room parameters (180 sqft, "
        "9 ft ceiling, 6 ACH), the glass cleaner at 6.5 g/L applied undiluted produces a "
        "steady-state concentration of 4.2 mg/m³ — 1.4% of the OSHA PEL. While the exposure level "
        "is safe, the product exceeds the Canadian federal VOC limit of 4.0 g/L for glass cleaners "
        "and must be replaced to maintain regulatory compliance.",
        s['BinxBody']
    ))

    story.append(PageBreak())

    # Section 9: Resources
    story.append(Paragraph("9. Open-Source Tools and Datasets", s['BinxH1']))
    story.append(Paragraph(
        f"All tools and datasets described in this guide are freely available under the MIT "
        f"(code) and CC-BY 4.0 (data) licenses:",
        s['BinxBody']
    ))
    story.append(Paragraph(f"• Source code and calculation engines: {LINK_GITHUB}", s['BinxBullet']))
    story.append(Paragraph(f"• Python package: {LINK_PYPI}", s['BinxBullet']))
    story.append(Paragraph(f"• Datasets (CSV): {LINK_HF}", s['BinxBullet']))
    story.append(Spacer(1, 0.3*inch))

    # Section 10: References
    story.append(Paragraph("10. References", s['BinxH1']))
    refs = [
        "EPA. 40 CFR Part 59, Subpart C — National Volatile Organic Compound Emission Standards for Consumer Products.",
        "California Air Resources Board. Consumer Products Regulations, Title 17 CCR §94507-94517.",
        "Environment and Climate Change Canada. SOR/2021-268 — Volatile Organic Compound Concentration Limits for Certain Products Regulations.",
        "OSHA. 29 CFR 1910.1000, Table Z-1 — Permissible Exposure Limits.",
        "ASHRAE. Standard 62.1-2022 — Ventilation for Acceptable Indoor Air Quality.",
        "Green Seal. GS-37 — Cleaning Products for Industrial and Institutional Use, Edition 7.8 (2022).",
        "UL Solutions. UL GREENGUARD Gold Certification — Low Emission Standards for Sensitive Environments.",
        "EPA. Safer Choice Program — Product Certification for Safer Chemical Ingredients.",
        "IPAC Canada. Infection Prevention and Control Standards for Healthcare Facilities.",
        "Ozone Transport Commission. OTC Model Rule for Consumer Products VOC Limits.",
    ]
    for i, ref in enumerate(refs, 1):
        story.append(Paragraph(f"[{i}] {ref}", s['BinxBullet']))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"Maintained by Dave Cook — {LINK_BINX}, North Bay and Sudbury, Ontario.",
        s['BinxFooter']
    ))

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f"Generated: {filename}")
    return filename


if __name__ == "__main__":
    generate_healthcare_voc_pdf()
