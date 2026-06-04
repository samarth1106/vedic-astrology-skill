#!/usr/bin/env python3
"""
houses.py — Bhava (house) report.

The kundli lists planets; this reads the chart house by house — the way a
practitioner actually answers "what about my 7th house / my career / my health".
For each of the twelve bhavas it gives the sign on the house, its lord and where
that lord sits (and in what dignity), the planets sitting in the house, the
planets aspecting it (Vedic graha drishti), and the natural karaka — the four
classical ways a house gets its results.

Usage:
    python houses.py --date 1990-08-15 --time 14:30:00 \\
        --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata \\
        [--house 7] [--ayanamsa lahiri] [--json]

--house  show just one bhava (1..12); omit for all twelve.

Disclaimer: cultural / educational use only. Not predictive of real outcomes.
"""

from __future__ import annotations

import argparse
import json
import sys

import core

BHAVA = {
    1: ("Tanu", "self, body, vitality, personality, overall life direction", "Sun"),
    2: ("Dhana", "wealth, savings, family, food, speech, accumulated assets", "Jupiter"),
    3: ("Sahaja", "courage, siblings, communication, skills, short journeys, effort", "Mars"),
    4: ("Sukha", "home, mother, property, vehicles, comforts, inner peace, education base", "Moon"),
    5: ("Putra", "children, intellect, romance, creativity, speculation, past-life merit", "Jupiter"),
    6: ("Ari", "enemies, debts, disease, litigation, service, daily work, competition", "Mars"),
    7: ("Yuvati", "spouse, marriage, partnerships, business, trade, the public", "Venus"),
    8: ("Randhra", "longevity, sudden events, inheritance, transformation, the occult, obstacles", "Saturn"),
    9: ("Dharma", "fortune, dharma, father, guru, higher learning, long travel, luck", "Jupiter"),
    10: ("Karma", "career, status, authority, public reputation, action in the world", "Sun"),
    11: ("Labha", "gains, income, friends, networks, elder siblings, fulfilment of desires", "Jupiter"),
    12: ("Vyaya", "loss, expenses, foreign lands, isolation, sleep, liberation (moksha)", "Saturn"),
}

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}


def _parse_time(t: str):
    p = t.split(":")
    return int(p[0]), (int(p[1]) if len(p) > 1 else 0), (int(p[2]) if len(p) > 2 else 0)


def quality(h: int) -> str:
    if h in TRIKONA and h != 1:
        return "trikona (fortune)"
    if h == 1:
        return "kendra + trikona (lagna)"
    if h in KENDRA:
        return "kendra (pillar)"
    if h in DUSTHANA:
        return "dusthana (difficult)"
    if h in (3, 11):
        return "upachaya (growing)"
    return "neutral"


def compute(args) -> dict:
    core.init_engine(
        args.ayanamsa, node=getattr(args, "node", "mean"),
        topocentric=not getattr(args, "geocentric", False),
        lat=args.lat, lon=args.lon, ephemeris=getattr(args, "ephemeris", "moshier"),
    )
    y, m, d = (int(x) for x in args.date.split("-"))
    hh, mm, ss = _parse_time(args.time)
    jd = core.to_julian_ut(y, m, d, hh, mm, ss, args.tz)

    asc = core.ascendant(jd, args.lat, args.lon)
    asc_sign = asc["sign_num"]
    positions = core.all_planet_positions(jd)

    # Annotate every planet with its house once.
    pl = {}
    for name, p in positions.items():
        pl[name] = {
            "sign_num": p["sign_num"],
            "house": core.house_of(p["sign_num"], asc_sign),
            "dignity": core.dignity(name, p["sign_num"]),
        }

    bhavas = []
    for h in range(1, 13):
        sign_num = ((asc_sign - 1) + (h - 1)) % 12 + 1
        lord = core.SIGN_LORD[sign_num]
        lord_house = pl[lord]["house"]
        occupants = [n for n in core.PLANET_ORDER if pl[n]["house"] == h]
        aspecting = [n for n in core.PLANET_ORDER
                     if n not in occupants and h in core.aspected_houses(pl[n]["house"], n)]
        name_s, signf, karaka = BHAVA[h]
        bhavas.append({
            "house": h,
            "name": name_s,
            "quality": quality(h),
            "sign": core.SIGNS[sign_num - 1],
            "sign_num": sign_num,
            "lord": lord,
            "lord_house": lord_house,
            "lord_dignity": pl[lord]["dignity"],
            "occupants": occupants,
            "occupant_dignities": {n: pl[n]["dignity"] for n in occupants},
            "aspected_by": aspecting,
            "karaka": karaka,
            "karaka_house": pl[karaka]["house"] if karaka in pl else None,
            "significations": signf,
        })

    return {
        "input": {"date": args.date, "time": args.time, "lat": args.lat,
                  "lon": args.lon, "timezone": args.tz, "ayanamsa": args.ayanamsa},
        "lagna_sign": asc["sign"],
        "bhavas": bhavas,
    }


def render_text(result: dict, only: int | None) -> str:
    L = []
    A = L.append
    A("=" * 70)
    A("  BHAVA (HOUSE) REPORT")
    A("=" * 70)
    A(f"  Lagna: {result['lagna_sign']}")
    for b in result["bhavas"]:
        if only and b["house"] != only:
            continue
        A("-" * 70)
        A(f"  HOUSE {b['house']} — {b['name']} Bhava   [{b['quality']}]   sign: {b['sign']}")
        A(f"    Significations : {b['significations']}")
        A(f"    House lord     : {b['lord']} ({b['lord_dignity']}), placed in House {b['lord_house']}")
        if b["occupants"]:
            occ = ", ".join(f"{n} ({b['occupant_dignities'][n]})" for n in b["occupants"])
            A(f"    Occupied by    : {occ}")
        else:
            A(f"    Occupied by    : — (empty; read via the lord and aspects)")
        A(f"    Aspected by    : {', '.join(b['aspected_by']) if b['aspected_by'] else '—'}")
        A(f"    Natural karaka : {b['karaka']} (placed in House {b['karaka_house']})")
    A("=" * 70)
    A("  A bhava is judged by four things: its lord's placement & strength, the")
    A("  planets in it, the planets aspecting it, and its natural karaka. A house")
    A("  lord in a kendra/trikona strengthens the house; in a dusthana (6/8/12),")
    A("  it strains it. For cultural/educational use only.")
    A("=" * 70)
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Bhava (house-by-house) report.")
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--house", type=int, choices=range(1, 13), metavar="1..12",
                    help="Show only this house (default: all 12)")
    ap.add_argument("--ayanamsa", default=core.DEFAULT_AYANAMSA)
    ap.add_argument("--node", default="mean", choices=["mean", "true"])
    ap.add_argument("--geocentric", action="store_true")
    ap.add_argument("--ephemeris", default="moshier", choices=["moshier", "swiss"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        result = compute(args)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2) if args.json else render_text(result, args.house))


if __name__ == "__main__":
    main()
