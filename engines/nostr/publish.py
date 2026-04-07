#!/usr/bin/env python3
"""
Publish Healthcare VOC Compliance content to Nostr public relays.
Reuses the Binx keypair from the window_cleaning_2026 campaign.
"""

import asyncio
import json
import time
from pathlib import Path
from nostr_sdk import (
    Keys, Client, EventBuilder, Tag, TagKind, Metadata,
    NostrSigner, SendEventOutput, RelayUrl,
)

RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.nostr.band",
    "wss://relay.snort.social",
    "wss://nostr.wine",
    "wss://relay.primal.net",
]

# Reuse existing keypair from window_cleaning campaign
KEYS_FILE = Path(__file__).resolve().parent.parent.parent.parent / "window_cleaning_2026" / "engines" / "nostr" / "nostr_keys.json"
LOCAL_KEYS = Path(__file__).parent / "nostr_keys.json"


def get_keys():
    # Try local keys first, then fall back to window_cleaning keys
    for kf in [LOCAL_KEYS, KEYS_FILE]:
        if kf.exists():
            data = json.loads(kf.read_text())
            keys = Keys.parse(data["nsec"])
            print(f"Loaded keypair from {kf}: {keys.public_key().to_bech32()}")
            return keys
    keys = Keys.generate()
    LOCAL_KEYS.write_text(json.dumps({
        "nsec": keys.secret_key().to_bech32(),
        "npub": keys.public_key().to_bech32(),
    }, indent=2))
    print(f"Generated new keypair: {keys.public_key().to_bech32()}")
    return keys


LONG_FORM_CONTENT = """# VOC Compliance for Healthcare Facility Cleaning: What Facility Managers Need to Know

Volatile Organic Compound (VOC) regulations for cleaning products vary significantly across North American jurisdictions. Healthcare facilities face the strictest scrutiny because patient populations — immunocompromised, post-surgical, neonatal — are vulnerable to airborne chemical exposure.

## The Regulatory Landscape

VOC limits for institutional cleaning products are set at multiple levels:

- **US Federal (EPA)**: 40 CFR Part 59 Subpart C sets baseline limits. General purpose cleaners: 10 g/L.
- **California (CARB)**: The strictest US jurisdiction. General purpose cleaners: 4 g/L (effective 2023).
- **OTC States**: 12 Ozone Transport Commission states (NY, NJ, CT, MA, etc.) adopt limits between EPA and CARB.
- **Canada Federal**: SOR/2021-268 aligns with CARB Phase II limits. Came into force January 2023.

A product compliant in Ohio (EPA federal limits) may be non-compliant in California or Ontario.

## Key Product Categories for Healthcare

Healthcare facilities use a narrower range of cleaning chemicals than commercial offices, but the compliance requirements are more stringent:

| Category | CARB Limit | EPA Limit | Healthcare Context |
|----------|-----------|-----------|-------------------|
| General Purpose Cleaner | 4.0 g/L | 10.0 g/L | Patient room turnover, common areas |
| Disinfectant (Spray) | 35.0 g/L | 60.0 g/L | Surface disinfection (C. diff, MRSA, VRE) |
| Disinfectant (Concentrate) | 8.0 g/L | 15.0 g/L | Mop-and-bucket, autoscrubber |
| Floor Wax Stripper | 0.0 g/L | 0.0 g/L | Zero-VOC required everywhere |
| Glass Cleaner | 4.0 g/L | 12.0 g/L | Interior partitions, nurse stations |

## The Calculation

VOC exposure per cleaning cycle depends on five variables:

```
effective_voc = product_voc × dilution_ratio
product_applied = room_sqft / coverage_rate
total_voc_mg = effective_voc × product_applied × 1000
steady_state_mg_per_m3 = (total_voc_mg / cleaning_duration_hr) / (ACH × room_volume_m3)
osha_pel_percent = steady_state / 300 × 100
```

Open-source calculator with implementations in Python, Rust, Java, Ruby, Elixir, PHP, and Go:
https://github.com/DaveCookVectorLabs/healthcare-voc-compliance

Datasets (650 regulatory limits + 5,000 products):
https://huggingface.co/datasets/davecook1985/healthcare-voc-compliance
"""

SHORT_NOTES = [
    (
        "Released an open-source healthcare VOC compliance calculator — "
        "computes VOC exposure, OSHA PEL comparison, and multi-jurisdiction "
        "regulatory compliance for cleaning products used in hospitals, LTC homes, "
        "and clinics. Python, Rust, Java, Ruby, Elixir, PHP, and Go.\n\n"
        "https://github.com/DaveCookVectorLabs/healthcare-voc-compliance"
    ),
    (
        "Published two open datasets for healthcare facility managers:\n"
        "• 650 VOC regulatory limits across 26 jurisdictions (EPA, CARB, OTC, Canada)\n"
        "• 5,000 healthcare cleaning products with VOC content and compliance flags\n\n"
        "CC-BY 4.0.\n\n"
        "https://huggingface.co/datasets/davecook1985/healthcare-voc-compliance"
    ),
    (
        "A general purpose cleaner at 8 g/L VOC (concentrate), diluted 1:64, "
        "applied in a 200 sqft patient room with 6 ACH ventilation: steady-state "
        "concentration is 0.40 mg/m³ — just 0.13% of the OSHA PEL. "
        "But switch to an undiluted spray disinfectant at 50 g/L in the same room "
        "and you hit 26% of PEL. Dilution ratio and product selection matter."
    ),
    (
        "Canadian healthcare facilities: SOR/2021-268 (federal VOC regulations) "
        "came into force Jan 2023. Limits align with California CARB Phase II — "
        "stricter than US EPA federal. If your cleaning supplier says a product is "
        "'EPA compliant,' it may not meet Canadian limits for the same category."
    ),
]


async def main():
    keys = get_keys()
    signer = NostrSigner.keys(keys)
    client = Client(signer)

    for relay in RELAYS:
        await client.add_relay(RelayUrl.parse(relay))
    await client.connect()
    await asyncio.sleep(3)

    # Publish long-form article (NIP-23, kind 30023)
    hashtags = [
        Tag.hashtag("healthcare"),
        Tag.hashtag("VOC"),
        Tag.hashtag("compliance"),
        Tag.hashtag("facilitymaintenance"),
        Tag.hashtag("cleaning"),
        Tag.hashtag("opensource"),
    ]
    builder = EventBuilder.long_form_text_note(LONG_FORM_CONTENT).tags([
        Tag.identifier("healthcare-voc-compliance"),
        Tag.title("VOC Compliance for Healthcare Facility Cleaning"),
        *hashtags,
    ])
    output = await client.send_event_builder(builder)
    print(f"Long-form article published: {output.id.to_bech32()}")
    await asyncio.sleep(1)

    # Publish short notes (kind 1)
    short_tags = [
        Tag.hashtag("healthcare"),
        Tag.hashtag("VOC"),
        Tag.hashtag("compliance"),
        Tag.hashtag("facilitymaintenance"),
    ]
    for i, note in enumerate(SHORT_NOTES):
        builder = EventBuilder.text_note(note).tags(short_tags)
        output = await client.send_event_builder(builder)
        print(f"Note {i+1} published: {output.id.to_bech32()}")
        await asyncio.sleep(1)

    await asyncio.sleep(3)
    await client.disconnect()

    npub = keys.public_key().to_bech32()
    print(f"\nDone. View profile: https://njump.me/{npub}")


if __name__ == "__main__":
    asyncio.run(main())
