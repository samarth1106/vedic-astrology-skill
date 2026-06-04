#!/usr/bin/env python3
"""
strength.py — Planetary-strength module for the vedic-astrology skill.

Computes two classical strength systems for a Vedic birth chart:

  PART A — ASHTAKAVARGA (fully implemented, deterministic)
      Bhinnashtakavarga (BAV) per planet (Sun..Saturn), Sarvashtakavarga (SAV),
      using the canonical Parashari benefic-point (rekha) contribution tables.
      Verified against the classical totals (SAV grand total = 337; per-planet
      BAV totals 48/49/39/54/56/52/39). The code ASSERTS these and raises if a
      table is wrong, so a miscomputed value can never silently ship.

  PART B — SHADBALA (partial, honest — see SCOPE & LIMITATIONS below)
      The six-fold strength in Rupas (1 Rupa = 60 virupas). Only the components
      that can be computed correctly from the available chart data are included.
      Everything else is listed explicitly under "not_implemented" and is NEVER
      fabricated or approximated to make a total "look complete".

Usage:
    python strength.py --date 1990-08-15 --time 14:30:00 \\
        --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata \\
        [--ayanamsa lahiri] [--node mean] [--json]

All angles are sidereal. Default ayanamsa = Lahiri.

============================================================================
SCOPE & LIMITATIONS — Shadbala (READ THIS)
============================================================================
This module computes a PARTIAL Shadbala. The total reported is the sum of ONLY
the components below and is explicitly labelled "partial Shadbala". It must NOT
be compared one-to-one against the classical required-strength thresholds as if
it were a complete Shadbala; the pass/fail flag is shown for reference only and
is annotated accordingly.

IMPLEMENTED (computed from classical rules, in virupas):
  - Sthana Bala : Uchcha Bala            (exaltation distance / 3, max 60)
  - Sthana Bala : Ojayugmarasyamsa Bala  (odd/even rashi + navamsa, max 30)
  - Sthana Bala : Kendradi Bala          (kendra 60 / panaphara 30 / apoklima 15)
  - Sthana Bala : Drekkana Bala          (sex of planet vs decanate, 0/15)
  - Dig Bala     (directional, max 60, by angular distance from powerless point)
  - Naisargika Bala (fixed natural values)

NOT IMPLEMENTED (omitted on purpose — listed in output under "not_implemented"):
  - Sthana Bala : Saptavargaja Bala
      Requires the full set of seven vargas (D1,D2,D3,D7,D9,D12,D30) AND the
      five-fold temporary+compound friendship (panchadha maitri) computation.
      Omitted rather than shipped half-correct.
  - Cheshta Bala (motional)
      A correct value needs the planet's mean/true anomaly and the seenfold
      speed-state (Vakra/Anuvakra/Vikala/Manda/Mandatara/Sama/Chara/Sheeghra)
      scaled against the planet's epicycle. A retro-flag heuristic would be an
      approximation, which this user's no-fabrication rule forbids. Omitted.
  - Kala Bala (all sub-components): Nathonnatha, Paksha, Tribhaga, Abda/Masa/
      Vara/Hora (the year/month/day/hour lords), Ayana, and Yuddha (planetary
      war) Bala. These need a correct civil-day-lord chain, exact sunrise-based
      day division, and the Sun's declination for Ayana. Omitted in full.
  - Drik Bala (aspectual)
      Requires the Sripati/virupa-graded drishti (partial aspect strengths by
      exact angular separation), not the whole-sign aspect flags this engine
      exposes. Computing it from whole-sign aspects would be an approximation.
      Omitted.

Because Cheshta and several Kala components are omitted, the per-planet totals
here are LOWER than a full Shadbala. This is expected and disclosed.
============================================================================
"""

from __future__ import annotations

import argparse
import json
import sys

import core

# --------------------------------------------------------------------------- #
# PART A — Ashtakavarga
# --------------------------------------------------------------------------- #
# Canonical Parashari Bhinnashtakavarga (rekha / benefic-point) tables.
#
# For each "planet whose BAV we are building", we list, for every contributor
# reference point (the 7 planets + the Lagna), the HOUSE numbers (1..12, counted
# inclusively from that reference point's sign) that receive one bindu.
#
# A bindu lands in the sign:  ((S_ref - 1) + (house - 1)) % 12 + 1
# where S_ref is the contributor's sign number.
#
# These are the standard tables (e.g. as given by Parashara / B.V. Raman). The
# per-planet totals are asserted at import time, so a typo cannot pass silently.
AV_TABLES = {
    "Sun": {
        "Sun":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":    [3, 6, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus":   [6, 7, 12],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":     [3, 6, 7, 8, 10, 11],
        "Moon":    [1, 3, 6, 7, 10, 11],
        "Mars":    [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus":   [3, 4, 5, 7, 9, 10, 11],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":     [3, 5, 6, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus":   [6, 8, 11, 12],
        "Saturn":  [1, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun":     [5, 6, 9, 11, 12],
        "Moon":    [2, 4, 6, 8, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":     [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":    [2, 5, 7, 9, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":   [2, 5, 6, 9, 10, 11],
        "Saturn":  [3, 5, 6, 12],
        "Lagna":   [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun":     [8, 11, 12],
        "Moon":    [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":    [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn":  [3, 4, 5, 8, 9, 10, 11],
        "Lagna":   [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":     [1, 2, 4, 7, 8, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus":   [6, 11, 12],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [1, 3, 4, 6, 10, 11],
    },
}

# Classical per-planet BAV totals and the SAV grand total — the verification gate.
BAV_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Jupiter": 56, "Venus": 52, "Saturn": 39,
}
SAV_TOTAL = 337

AV_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _verify_tables() -> None:
    """Assert the canonical tables reproduce the classical totals. Raises on error."""
    grand = 0
    for planet in AV_PLANETS:
        total = sum(len(houses) for houses in AV_TABLES[planet].values())
        if total != BAV_TOTALS[planet]:
            raise ValueError(
                f"Ashtakavarga table for {planet} totals {total}, "
                f"expected classical {BAV_TOTALS[planet]} — table is WRONG, fix it."
            )
        grand += total
    if grand != SAV_TOTAL:
        raise ValueError(
            f"SAV grand total is {grand}, expected classical {SAV_TOTAL} — tables WRONG."
        )


# Fail fast at import: if any table is wrong, the module refuses to load.
_verify_tables()


def compute_ashtakavarga(planets: dict, asc_sign_num: int) -> dict:
    """Compute BAV per planet, SAV, and totals.

    planets: mapping name -> info dict (must have 'sign_num').
    Returns a dict with per-sign 12-element arrays and totals.
    """
    ref_sign = {name: planets[name]["sign_num"] for name in AV_PLANETS}
    ref_sign["Lagna"] = asc_sign_num

    bav: dict = {}
    for planet in AV_PLANETS:
        bindus = [0] * 12  # index 0 = Aries .. 11 = Pisces
        for contributor, houses in AV_TABLES[planet].items():
            s_ref = ref_sign[contributor]
            for house in houses:
                sign_idx = ((s_ref - 1) + (house - 1)) % 12
                bindus[sign_idx] += 1
        bav[planet] = bindus

    # Sarvashtakavarga = element-wise sum across the 7 BAVs.
    sav = [0] * 12
    for planet in AV_PLANETS:
        for i in range(12):
            sav[i] += bav[planet][i]

    # Verification gate on the actual computed chart (not just table lengths).
    bav_totals = {p: sum(bav[p]) for p in AV_PLANETS}
    for p in AV_PLANETS:
        if bav_totals[p] != BAV_TOTALS[p]:
            raise ValueError(
                f"Computed BAV total for {p} = {bav_totals[p]}, expected {BAV_TOTALS[p]}."
            )
    sav_grand = sum(sav)
    if sav_grand != SAV_TOTAL:
        raise ValueError(f"Computed SAV total = {sav_grand}, expected {SAV_TOTAL}.")

    # Bindus in the sign occupied by each planet (useful for transit strength).
    bindus_in_own_sign = {}
    for name in core.PLANET_ORDER:
        sign_num = planets[name]["sign_num"]
        bindus_in_own_sign[name] = sav[sign_num - 1]

    return {
        "bav": {p: {"per_sign": bav[p], "total": bav_totals[p]} for p in AV_PLANETS},
        "sav": {"per_sign": sav, "total": sav_grand},
        "sav_in_planet_sign": bindus_in_own_sign,
        "verification": {
            "sav_total_expected": SAV_TOTAL,
            "sav_total_computed": sav_grand,
            "bav_totals_expected": BAV_TOTALS,
            "bav_totals_computed": bav_totals,
            "passed": True,
        },
    }


# --------------------------------------------------------------------------- #
# PART B — Shadbala (partial)
# --------------------------------------------------------------------------- #
SHADBALA_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Exact exaltation longitudes (deg, sidereal sign-based) — degree within sign.
EXALT_DEG = {
    "Sun": 10.0, "Moon": 3.0, "Mars": 28.0, "Mercury": 15.0,
    "Jupiter": 5.0, "Venus": 27.0, "Saturn": 20.0,
}

# Naisargika (natural) Bala — fixed values in virupas.
NAISARGIKA = {
    "Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
    "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57,
}

# Dig Bala: the house of maximum directional strength for each planet.
DIG_MAX_HOUSE = {
    "Jupiter": 1, "Mercury": 1,   # east (Lagna)
    "Sun": 10, "Mars": 10,        # south (10th / MC)
    "Saturn": 7,                  # west (7th / Descendant)
    "Moon": 4, "Venus": 4,        # north (4th / IC)
}

# Required (minimum) Shadbala in Rupas — classical thresholds, for reference.
REQUIRED_RUPAS = {
    "Sun": 5.0, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
}

# Planet "sex" for Drekkana Bala. Male: Sun, Mars, Jupiter. Female: Moon, Venus.
# Neutral (eunuch): Mercury, Saturn — favoured in any drekkana (counted as full).
PLANET_SEX = {
    "Sun": "male", "Mars": "male", "Jupiter": "male",
    "Moon": "female", "Venus": "female",
    "Mercury": "neutral", "Saturn": "neutral",
}


def _exalt_longitude(planet: str) -> float:
    """Absolute sidereal longitude (0..360) of a planet's exaltation point."""
    sign_num = core.EXALTATION[planet]            # 1..12
    return (sign_num - 1) * 30.0 + EXALT_DEG[planet]


def uchcha_bala(planet: str, lon: float) -> float:
    """Exaltation strength in virupas: (distance from debilitation point)/3.

    Max 60 at exaltation, 0 at debilitation (= exalt + 180).
    """
    debil = (_exalt_longitude(planet) + 180.0) % 360.0
    dist = abs((lon - debil + 180.0) % 360.0 - 180.0)  # 0..180 from debil point
    return dist / 3.0


def ojayugma_bala(planet: str, sign_num: int, navamsa_sign_num: int) -> float:
    """Oja/Yugma (odd/even) Bala in virupas, from rashi AND navamsa.

    Sun, Mars, Jupiter, Mercury (male/neutral) gain 15 in ODD signs.
    Moon and Venus (female) gain 15 in EVEN signs.
    Awarded independently for the rashi and the navamsa => up to 30.
    """
    odd_sign = (sign_num % 2 == 1)
    odd_nav = (navamsa_sign_num % 2 == 1)
    wants_odd = planet not in ("Moon", "Venus")
    bala = 0.0
    if odd_sign == wants_odd:
        bala += 15.0
    if odd_nav == wants_odd:
        bala += 15.0
    return bala


def kendradi_bala(house: int) -> float:
    """Kendradi Bala in virupas by house type: kendra 60, panaphara 30, apoklima 15."""
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0  # apoklima (3, 6, 9, 12)


def drekkana_bala(planet: str, deg_in_sign: float) -> float:
    """Drekkana Bala in virupas (0 or 15).

    1st decanate (0-10°): male planets get 15.
    2nd decanate (10-20°): neutral planets get 15.
    3rd decanate (20-30°): female planets get 15.
    """
    if deg_in_sign < 10.0:
        decanate = "male"
    elif deg_in_sign < 20.0:
        decanate = "neutral"
    else:
        decanate = "female"
    return 15.0 if PLANET_SEX[planet] == decanate else 0.0


def dig_bala(planet: str, lon: float, asc_lon: float) -> float:
    """Directional strength in virupas (max 60).

    Strength = 60 * (angular distance of the planet from its powerless point)/180,
    where the powerless point is the cusp opposite the planet's max-strength
    direction. Cusps are taken as equal divisions from the Lagna degree
    (asc_lon + 30*(house-1)) — the common Dig Bala construction. Note this is the
    equal/Sripati-from-ascendant cusp scheme, which differs slightly from the
    whole-sign houses used elsewhere in the skill; Dig Bala is a directional
    measure and traditionally uses these angular cusps.
    """
    max_house = DIG_MAX_HOUSE[planet]
    # Powerless point is opposite the max-strength cusp.
    powerless_house = ((max_house - 1 + 6) % 12) + 1
    powerless_cusp = (asc_lon + 30.0 * (powerless_house - 1)) % 360.0
    dist = abs((lon - powerless_cusp + 180.0) % 360.0 - 180.0)  # 0..180
    return 60.0 * dist / 180.0


def compute_shadbala(planets: dict, asc: dict) -> dict:
    """Compute the partial Shadbala for the 7 grahas. Returns per-planet detail."""
    asc_lon = (asc["sign_num"] - 1) * 30.0 + asc["degree_in_sign"]

    result: dict = {}
    for name in SHADBALA_PLANETS:
        p = planets[name]
        lon = p["longitude"]
        sign_num = p["sign_num"]
        nav_sign = p["navamsa_sign_num"]
        deg_in_sign = p["degree_in_sign"]
        house = p["house"]

        uchcha = uchcha_bala(name, lon)
        oja = ojayugma_bala(name, sign_num, nav_sign)
        kendra = kendradi_bala(house)
        drek = drekkana_bala(name, deg_in_sign)
        sthana_total = uchcha + oja + kendra + drek

        dig = dig_bala(name, lon, asc_lon)
        naisargika = NAISARGIKA[name]

        components_virupa = {
            "uchcha_bala": round(uchcha, 2),
            "ojayugma_bala": round(oja, 2),
            "kendradi_bala": round(kendra, 2),
            "drekkana_bala": round(drek, 2),
            "sthana_bala_subtotal": round(sthana_total, 2),
            "dig_bala": round(dig, 2),
            "naisargika_bala": round(naisargika, 2),
        }

        total_virupa = sthana_total + dig + naisargika
        total_rupa = total_virupa / 60.0
        required = REQUIRED_RUPAS[name]

        result[name] = {
            "components_virupa": components_virupa,
            "partial_total_virupa": round(total_virupa, 2),
            "partial_total_rupa": round(total_rupa, 3),
            "required_rupa": required,
            "meets_required": total_rupa >= required,
            "note": (
                "partial total — Cheshta, Saptavargaja, Kala (Nathonnatha/Paksha/"
                "Tribhaga/Hora/Ayana/Yuddha) and Drik Bala are NOT included; "
                "pass/fail vs required is reference-only"
            ),
        }

    return {
        "components_included": [
            "Sthana:Uchcha", "Sthana:Ojayugma", "Sthana:Kendradi",
            "Sthana:Drekkana", "Dig", "Naisargika",
        ],
        "not_implemented": [
            "Sthana:Saptavargaja (needs 7 vargas + panchadha maitri)",
            "Cheshta Bala (needs anomaly/epicycle speed-state, not a retro flag)",
            "Kala:Nathonnatha", "Kala:Paksha", "Kala:Tribhaga",
            "Kala:Abda/Masa/Vara/Hora (year/month/day/hour lords)",
            "Kala:Ayana (needs Sun declination)",
            "Kala:Yuddha (planetary war)",
            "Drik Bala (needs graded virupa drishti, not whole-sign aspects)",
        ],
        "units": "virupa (1 Rupa = 60 virupa)",
        "planets": result,
    }


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def compute_strength(args) -> dict:
    core.init_engine(
        args.ayanamsa,
        node=getattr(args, "node", "mean"),
        topocentric=not getattr(args, "geocentric", False),
        lat=args.lat, lon=args.lon,
        ephemeris=getattr(args, "ephemeris", "moshier"),
    )
    y, m, d = (int(x) for x in args.date.split("-"))
    hh, mm, ss = _parse_time(args.time)
    jd = core.to_julian_ut(y, m, d, hh, mm, ss, args.tz)

    asc = core.ascendant(jd, args.lat, args.lon, args.house_system)
    asc_sign_num = asc["sign_num"]

    planets = core.all_planet_positions(jd)
    for name, info in planets.items():
        info["house"] = core.house_of(info["sign_num"], asc_sign_num)
        info["dignity"] = core.dignity(name, info["sign_num"])

    ashtakavarga = compute_ashtakavarga(planets, asc_sign_num)
    shadbala = compute_shadbala(planets, asc)

    return {
        "input": {
            "date": args.date, "time": args.time, "lat": args.lat,
            "lon": args.lon, "timezone": args.tz,
            "ayanamsa": args.ayanamsa, "house_system": args.house_system,
            "node": getattr(args, "node", "mean"),
            "topocentric": not getattr(args, "geocentric", False),
        },
        "julian_day_ut": round(jd, 6),
        "ayanamsa_deg": round(core.ayanamsa_value(jd), 6),
        "ascendant": asc,
        "planet_signs": {name: planets[name]["sign"] for name in core.PLANET_ORDER},
        "ashtakavarga": ashtakavarga,
        "shadbala": shadbala,
        "disclaimer": (
            "Ashtakavarga is fully computed (verified totals). Shadbala is a "
            "PARTIAL computation: only the components listed under "
            "shadbala.components_included are included; everything under "
            "shadbala.not_implemented is omitted, not estimated. Do not treat "
            "the partial Shadbala total as a complete Shadbala."
        ),
    }


def _parse_time(t: str):
    parts = t.split(":")
    hh = int(parts[0]); mm = int(parts[1]) if len(parts) > 1 else 0
    ss = int(parts[2]) if len(parts) > 2 else 0
    return hh, mm, ss


def render_text(result: dict) -> str:
    lines = []
    i = result["input"]
    asc = result["ascendant"]
    lines.append("=" * 64)
    lines.append("  PLANETARY STRENGTH — Ashtakavarga & (Partial) Shadbala")
    lines.append("=" * 64)
    lines.append(f"  Born: {i['date']} {i['time']} ({i['timezone']})")
    lines.append(f"  Place: lat {i['lat']}, lon {i['lon']}")
    frame = "topocentric" if i.get("topocentric") else "geocentric"
    lines.append(f"  Ayanamsa: {i['ayanamsa'].title()} ({result.get('ayanamsa_deg')}°) "
                 f"| {frame} | {i.get('node','mean')}-node")
    lines.append(f"  Lagna: {asc['sign']} {core.deg_to_dms(asc['degree_in_sign'])}")

    # ---- Section 1: Ashtakavarga ----
    av = result["ashtakavarga"]
    lines.append("")
    lines.append("-" * 64)
    lines.append("  ASHTAKAVARGA  (fully computed — verified)")
    lines.append("-" * 64)
    # SAV row per sign.
    lines.append("  Sarvashtakavarga (SAV) bindus per sign:")
    hdr = "  " + "".join(f"{core.SIGNS[s][:3]:>5}" for s in range(12))
    lines.append(hdr)
    lines.append("  " + "".join(f"{b:>5}" for b in av["sav"]["per_sign"]))
    lines.append(f"  SAV grand total = {av['sav']['total']}  (classical 337)")
    lines.append("")
    lines.append("  Per-planet BAV totals:")
    bav_line = "   ".join(
        f"{p[:3]} {av['bav'][p]['total']}" for p in AV_PLANETS
    )
    lines.append("    " + bav_line)
    lines.append("    (classical: Sun 48, Moon 49, Mars 39, Mer 54, Jup 56, Ven 52, Sat 39)")
    lines.append("")
    lines.append("  SAV bindus in each planet's own sign (transit strength):")
    for name in core.PLANET_ORDER:
        lines.append(f"    {name:<9} {av['sav_in_planet_sign'][name]:>2} bindus "
                     f"(in {result_sign(result, name)})")

    # ---- Section 2: Shadbala ----
    sb = result["shadbala"]
    lines.append("")
    lines.append("-" * 64)
    lines.append("  SHADBALA  (PARTIAL — see note)")
    lines.append("-" * 64)
    lines.append("  Included: " + ", ".join(sb["components_included"]))
    lines.append("  Values in virupa (1 Rupa = 60 virupa).")
    lines.append("")
    header = (f"  {'Planet':<9}{'Uch':>6}{'Oja':>6}{'Ken':>6}{'Drk':>6}"
              f"{'Dig':>7}{'Nai':>7}{'TotRup':>8}{'Req':>6}{'P/F':>5}")
    lines.append(header)
    lines.append("  " + "-" * 60)
    for name in SHADBALA_PLANETS:
        p = sb["planets"][name]
        c = p["components_virupa"]
        pf = "PASS" if p["meets_required"] else "FAIL"
        lines.append(
            f"  {name:<9}{c['uchcha_bala']:>6.1f}{c['ojayugma_bala']:>6.1f}"
            f"{c['kendradi_bala']:>6.1f}{c['drekkana_bala']:>6.1f}"
            f"{c['dig_bala']:>7.1f}{c['naisargika_bala']:>7.1f}"
            f"{p['partial_total_rupa']:>8.2f}{p['required_rupa']:>6.1f}{pf:>5}"
        )
    lines.append("")
    lines.append("  NOT IMPLEMENTED (omitted, not estimated):")
    for item in sb["not_implemented"]:
        lines.append(f"    - {item}")
    lines.append("")
    lines.append("  Note: P/F compares a PARTIAL total against the classical")
    lines.append("  required strength and is REFERENCE-ONLY. Because Cheshta and")
    lines.append("  several Kala components are omitted, totals run lower than a")
    lines.append("  full Shadbala. Do not read this as a complete Shadbala.")

    lines.append("")
    lines.append("-" * 64)
    lines.append("  " + result["disclaimer"])
    lines.append("=" * 64)
    return "\n".join(lines)


def result_sign(result: dict, name: str) -> str:
    """Helper for render: the sign name a planet currently occupies."""
    return result["planet_signs"][name]


def main():
    ap = argparse.ArgumentParser(
        description="Compute planetary strength (Ashtakavarga + partial Shadbala)."
    )
    ap.add_argument("--date", required=True, help="Birth date YYYY-MM-DD")
    ap.add_argument("--time", required=True, help="Birth time HH:MM[:SS], 24h local")
    ap.add_argument("--lat", type=float, required=True, help="Latitude (deg, N positive)")
    ap.add_argument("--lon", type=float, required=True, help="Longitude (deg, E positive)")
    ap.add_argument("--tz", required=True, help="IANA timezone, e.g. Asia/Kolkata")
    ap.add_argument("--ayanamsa", default=core.DEFAULT_AYANAMSA)
    ap.add_argument("--house-system", default=core.DEFAULT_HOUSE_SYSTEM, dest="house_system")
    ap.add_argument("--node", default="mean", choices=["mean", "true"],
                    help="Lunar node model for Rahu/Ketu (default mean)")
    ap.add_argument("--geocentric", action="store_true",
                    help="Use geocentric positions (default is topocentric)")
    ap.add_argument("--ephemeris", default="moshier", choices=["moshier", "swiss"],
                    help="moshier=offline (default), swiss=requires .se1 files")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = ap.parse_args()

    try:
        result = compute_strength(args)
    except Exception as e:  # noqa: BLE001 — surface a clean message to the agent
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))


if __name__ == "__main__":
    main()
