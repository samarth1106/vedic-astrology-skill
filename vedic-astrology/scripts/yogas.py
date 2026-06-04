#!/usr/bin/env python3
"""
yogas.py — Detect common classical yogas in a Vedic birth chart and produce a
readable interpretation.

This v1 detects a curated, well-defined subset of yogas where the rules are
unambiguous and computable from the D1 chart. It is intentionally NOT
exhaustive — classical jyotish describes hundreds of yogas, many with
conflicting definitions. Each detected yoga carries a short, plain-language
note. See references/yogas.md for definitions and caveats.

Detected yogas:
  - Gajakesari yoga       (Jupiter in a kendra from the Moon)
  - Budhaditya yoga       (Sun + Mercury conjunct)
  - Chandra-Mangala yoga  (Moon + Mars conjunct)
  - Pancha Mahapurusha    (Ruchaka/Bhadra/Hamsa/Malavya/Sasa)
  - Simplified Raj yoga   (a kendra lord conjunct a trikona lord)

Usage:
    python yogas.py --date 1990-08-15 --time 14:30:00 \\
        --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata [--ayanamsa lahiri] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys

import core
import kundli as kundli_mod

KENDRAS = {1, 4, 7, 10}      # angular houses
TRIKONAS = {1, 5, 9}         # trine houses

# Mahapurusha yoga names by planet.
MAHAPURUSHA = {
    "Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa",
    "Venus": "Malavya", "Saturn": "Sasa",
}


def _same_house(planets: dict, a: str, b: str) -> bool:
    return planets[a]["house"] == planets[b]["house"]


def detect_yogas(chart: dict) -> list[dict]:
    planets = chart["planets"]
    asc_sign = chart["ascendant"]["sign_num"]
    found: list[dict] = []

    # --- Gajakesari: Jupiter in a kendra (1/4/7/10) FROM the Moon -------------
    moon_sign = planets["Moon"]["sign_num"]
    jup_from_moon = ((planets["Jupiter"]["sign_num"] - moon_sign) % 12) + 1
    if jup_from_moon in KENDRAS:
        found.append({
            "name": "Gajakesari Yoga",
            "rule": "Jupiter occupies a kendra (1/4/7/10) from the Moon.",
            "note": "Associated with intelligence, respect, and lasting reputation.",
        })

    # --- Budhaditya: Sun + Mercury conjunct -----------------------------------
    if _same_house(planets, "Sun", "Mercury"):
        found.append({
            "name": "Budhaditya Yoga",
            "rule": "Sun and Mercury occupy the same sign/house.",
            "note": "Linked to intellect, communication skill, and analytical ability.",
        })

    # --- Chandra-Mangala: Moon + Mars conjunct --------------------------------
    if _same_house(planets, "Moon", "Mars"):
        found.append({
            "name": "Chandra-Mangala Yoga",
            "rule": "Moon and Mars occupy the same sign/house.",
            "note": "Classically tied to financial drive and resourcefulness.",
        })

    # --- Pancha Mahapurusha yogas ---------------------------------------------
    for planet, yoga_name in MAHAPURUSHA.items():
        info = planets[planet]
        in_kendra = info["house"] in KENDRAS
        strong = info["dignity"] in ("exalted", "own sign")
        if in_kendra and strong:
            found.append({
                "name": f"{yoga_name} Yoga (Pancha Mahapurusha)",
                "rule": f"{planet} is {info['dignity']} and in a kendra (house {info['house']}).",
                "note": "A Mahapurusha yoga — marks pronounced strength of this planet's significations.",
            })

    # --- Simplified Raj yoga: a kendra lord conjunct a trikona lord -----------
    kendra_lords = {core.SIGN_LORD[((asc_sign - 1 + (h - 1)) % 12) + 1] for h in KENDRAS}
    trikona_lords = {core.SIGN_LORD[((asc_sign - 1 + (h - 1)) % 12) + 1] for h in TRIKONAS}
    raj_pairs = []
    grahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i in range(len(grahas)):
        for j in range(i + 1, len(grahas)):
            a, b = grahas[i], grahas[j]
            if _same_house(planets, a, b):
                if (a in kendra_lords and b in trikona_lords) or \
                   (b in kendra_lords and a in trikona_lords):
                    raj_pairs.append(f"{a}+{b}")
    if raj_pairs:
        found.append({
            "name": "Raja Yoga (simplified)",
            "rule": f"Kendra lord conjunct trikona lord: {', '.join(raj_pairs)}.",
            "note": "A Raja yoga association — classically a marker of status and success. "
                    "(Simplified detection: conjunction only, not aspects/exchange.)",
        })

    return found


def render_text(chart: dict, yogas: list[dict]) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  YOGA ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"  Lagna: {chart['ascendant']['sign']} | "
                 f"Moon: {chart['planets']['Moon']['sign']}")
    lines.append("-" * 60)
    if not yogas:
        lines.append("  No yogas from the detected set were found in this chart.")
        lines.append("  (This set is curated, not exhaustive — see references/yogas.md.)")
    else:
        for y in yogas:
            lines.append(f"  ● {y['name']}")
            lines.append(f"      Rule: {y['rule']}")
            lines.append(f"      {y['note']}")
            lines.append("")
    lines.append("=" * 60)
    lines.append("  For cultural/educational use. Not predictive of real outcomes.")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Detect classical yogas in a birth chart.")
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--ayanamsa", default=core.DEFAULT_AYANAMSA)
    ap.add_argument("--house-system", default=core.DEFAULT_HOUSE_SYSTEM, dest="house_system")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        chart = kundli_mod.compute_kundli(args)
        yogas = detect_yogas(chart)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"yogas": yogas, "ascendant": chart["ascendant"]}, indent=2))
    else:
        print(render_text(chart, yogas))


if __name__ == "__main__":
    main()
