#!/usr/bin/env python3
"""Generate/check InfoPulse PL SWIR Progress SVG PRO assets.

The repository currently has no canonical measurable product roadmap. Product
readiness must therefore remain N/A; the v3.2.0 release is tracked separately.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "readme"

CARD = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="190" viewBox="0 0 1200 190" role="img" aria-labelledby="title desc">
  <title id="title">InfoPulse PL product progress</title>
  <desc id="desc">InfoPulse PL product readiness is N/A because the repository has no canonical measurable roadmap.</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient><linearGradient id="cyan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient><pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="#62E5FF" stroke-opacity="0.05"/></pattern></defs>
  <rect x="1" y="1" width="1198" height="188" rx="24" fill="url(#bg)" stroke="#62E5FF" stroke-opacity="0.22"/><rect x="1" y="1" width="1198" height="188" rx="24" fill="url(#grid)"/>
  <text x="50" y="43" fill="#62E5FF" font-family="Segoe UI, Arial, sans-serif" font-size="17" font-weight="700" letter-spacing="4">SWIR PROGRESS</text>
  <text x="50" y="79" fill="#F4FAFF" font-family="Segoe UI, Arial, sans-serif" font-size="31" font-weight="800">INFOPULSE PL</text>
  <text x="50" y="107" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="15">PRODUCT READINESS • NO CANONICAL ROADMAP</text>
  <text x="1110" y="79" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI, Arial, sans-serif" font-size="35" font-weight="800">N/A</text>
  <text x="1110" y="106" text-anchor="end" fill="#62E5FF" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="650" letter-spacing="1.5">IN PROGRESS</text>
  <rect x="50" y="126" width="1100" height="22" rx="11" fill="#08131F" stroke="#62E5FF" stroke-opacity="0.18"/><path d="M50 137H1150" stroke="url(#cyan)" stroke-opacity="0.14" stroke-width="2"/>
  <text x="50" y="174" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="13">Roadmap items: N/A</text><text x="1150" y="174" text-anchor="end" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="13">Release v3.2.0 exists; release ≠ completion percentage</text>
</svg>
'''

MINI = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-labelledby="title desc">
  <title id="title">InfoPulse PL compact product progress</title>
  <desc id="desc">Product readiness is N/A because InfoPulse PL has no canonical measurable roadmap.</desc>
  <defs><linearGradient id="fill" x1="0" y1="0" x2="700" y2="0"><stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient></defs>
  <rect x="1" y="1" width="898" height="70" rx="18" fill="#02050A" stroke="#62E5FF" stroke-opacity="0.22"/>
  <text x="24" y="27" fill="#62E5FF" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="2">PRODUCT READINESS</text>
  <text x="24" y="52" fill="#F4FAFF" font-family="Segoe UI, Arial, sans-serif" font-size="21" font-weight="800">N/A</text>
  <rect x="170" y="24" width="700" height="20" rx="10" fill="#08131F"/>
  <path d="M170 34H870" stroke="url(#fill)" stroke-opacity="0.14" stroke-width="2"/>
  <text x="870" y="59" text-anchor="end" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="12">NO CANONICAL ROADMAP</text>
</svg>
'''

TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="190" viewBox="0 0 1200 190" role="img" aria-labelledby="title desc">
  <title id="title">SWIR progress template — not project data</title>
  <desc id="desc">Reusable local template for generated SWIR progress graphics. This file is not live project progress.</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient></defs>
  <rect x="1" y="1" width="1198" height="188" rx="24" fill="url(#bg)" stroke="#62E5FF" stroke-opacity="0.22"/>
  <text x="50" y="43" fill="#62E5FF" font-family="Segoe UI, Arial, sans-serif" font-size="17" font-weight="700" letter-spacing="4">SWIR PROGRESS TEMPLATE</text>
  <text x="50" y="79" fill="#F4FAFF" font-family="Segoe UI, Arial, sans-serif" font-size="31" font-weight="800">PROJECT NAME</text>
  <text x="50" y="107" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="15">MEASURED SCOPE</text>
  <text x="1110" y="79" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI, Arial, sans-serif" font-size="30" font-weight="800">NOT PROJECT DATA</text>
  <text x="1110" y="106" text-anchor="end" fill="#62E5FF" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="650">TEMPLATE</text>
  <rect x="50" y="126" width="1100" height="22" rx="11" fill="#08131F" stroke="#62E5FF" stroke-opacity="0.18"/>
  <text x="50" y="174" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="13">Generated files must use verified source data.</text>
  <text x="1150" y="174" text-anchor="end" fill="#8DA8B8" font-family="Segoe UI, Arial, sans-serif" font-size="13">TEMPLATE / NOT LIVE PROGRESS</text>
</svg>
'''

OUTPUTS = {ASSETS / "progress-card.svg": CARD, ASSETS / "progress-mini.svg": MINI, ASSETS / "progress-template.svg": TEMPLATE}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, content in OUTPUTS.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        print("Stale progress assets:")
        for path in stale:
            print(f"- {path}")
        return 1
    print("SWIR progress SVGs are current (product readiness: N/A; no canonical roadmap)." if args.check else "Generated SWIR progress SVGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
