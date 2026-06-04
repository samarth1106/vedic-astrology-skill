#!/usr/bin/env python3
"""
numerology.py — Compute a numerology report from birth date (and optional name).

Pure Python standard library only — no ephemeris, no network, no dependencies.
Covers Moolank (psychic/birth number), Bhagyank (destiny/life-path number),
Naamank (name number, Chaldean and/or Pythagorean), ruling planets, number
compatibility (planetary friendships), the Lo Shu grid with arrows, an optional
personal-year theme, lucky attributes, and a name-correction hint.

Usage:
    python numerology.py --date 1990-08-15 [--name "Full Name"] \\
        [--system chaldean|pythagorean|both] [--year YYYY] \\
        [--keep-master] [--json]

For cultural/educational/entertainment use only. Not predictive.
"""

from __future__ import annotations

import argparse
import json
import sys

# --- Constant lookups ------------------------------------------------------

RULING_PLANET = {
    1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury",
    6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars",
}

# Chaldean letter values (no letter is assigned 9 in the Chaldean system).
CHALDEAN_MAP = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

# Pythagorean letter values (A=1..I=9, J=1..R=9, S=1..Z=8).
PYTHAGOREAN_MAP = {
    "A": 1, "J": 1, "S": 1,
    "B": 2, "K": 2, "T": 2,
    "C": 3, "L": 3, "U": 3,
    "D": 4, "M": 4, "V": 4,
    "E": 5, "N": 5, "W": 5,
    "F": 6, "O": 6, "X": 6,
    "G": 7, "P": 7, "Y": 7,
    "H": 8, "Q": 8, "Z": 8,
    "I": 9, "R": 9,
}

# Friendship matrix among single digits 1-9 (planetary friendships, Cheiro/Indian).
# Entries list explicit friends and enemies; any unlisted pair is neutral.
FRIENDS = {
    1: {1, 2, 3, 9},
    2: {1, 2, 5, 7},
    3: {1, 2, 3, 9},
    4: {1, 5, 6, 7},
    5: {1, 2, 3, 4, 5, 6, 7, 8, 9},  # Mercury — friendly to all generally
    6: {4, 5, 6, 8},
    7: {1, 2, 4, 7},
    8: {5, 6, 8},
    9: {1, 3, 9},
}
ENEMIES = {
    1: {8, 4, 7},
    2: {8, 9},
    3: {6},
    4: {2, 9},
    5: set(),
    6: {3},
    7: set(),
    8: {1, 2},
    9: {4},
}

# Lo Shu grid layout (row-major).
LO_SHU_LAYOUT = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

LO_SHU_LINES = [
    ((4, 9, 2), "Arrow of Intellect / Mental Plane"),
    ((3, 5, 7), "Arrow of Emotional Balance"),
    ((8, 1, 6), "Arrow of Practicality / Action"),
    ((4, 3, 8), "Arrow of Planning / Thought"),
    ((9, 5, 1), "Arrow of Will / Determination"),
    ((2, 7, 6), "Arrow of Activity"),
    ((4, 5, 6), "Arrow of Compassion (the Golden / Kindness)"),
    ((2, 5, 8), "Arrow of Spirituality / Emotional"),
]

NUMBER_THEME = {
    1: "Independence, leadership, new beginnings, initiative.",
    2: "Cooperation, partnership, sensitivity, patience.",
    3: "Creativity, expression, optimism, social growth.",
    4: "Foundation, hard work, structure, discipline.",
    5: "Change, freedom, travel, adaptability.",
    6: "Responsibility, home, service, relationships.",
    7: "Introspection, study, spirituality, analysis.",
    8: "Ambition, power, finances, material achievement.",
    9: "Completion, compassion, humanitarianism, release.",
}

LUCKY_ATTRIBUTES = {
    "Sun": {"gemstone": "Ruby", "days": "Sunday & Monday", "colors": "Gold, orange"},
    "Moon": {"gemstone": "Pearl", "days": "Monday", "colors": "White, cream, silver"},
    "Jupiter": {"gemstone": "Yellow Sapphire", "days": "Thursday", "colors": "Yellow"},
    "Rahu": {"gemstone": "Hessonite (Gomed)", "days": "Varies", "colors": "Grey, khaki, electric blue"},
    "Mercury": {"gemstone": "Emerald", "days": "Wednesday", "colors": "Green"},
    "Venus": {"gemstone": "Diamond / Opal", "days": "Friday", "colors": "White, pastels"},
    "Ketu": {"gemstone": "Cat's Eye", "days": "Varies", "colors": "Smoky, grey"},
    "Saturn": {"gemstone": "Blue Sapphire", "days": "Saturday", "colors": "Black, dark blue"},
    "Mars": {"gemstone": "Red Coral", "days": "Tuesday", "colors": "Red"},
}

DISCLAIMER = "For cultural/educational/entertainment use only. Not predictive."


# --- Core helpers ----------------------------------------------------------

def reduce_to_single(n: int, keep_master: bool = False) -> int:
    """Repeatedly sum the digits of n until a single digit remains.

    If keep_master is True and an intermediate sum is a master number
    (11, 22, 33), stop there and return it unreduced.
    """
    n = abs(int(n))
    if keep_master and n in (11, 22, 33):
        return n
    while n > 9:
        n = sum(int(c) for c in str(n))
        if keep_master and n in (11, 22, 33):
            return n
    return n


def _letters(name: str) -> str:
    """Uppercase letters of name only (ignore digits, spaces, punctuation)."""
    return "".join(ch for ch in name.upper() if ch.isalpha())


def relation(a: int, b: int) -> str:
    """Symmetric friendship relation between two single digits 1-9.

    Returns "friend", "neutral", or "enemy". A pair is a friend if either
    side lists the other as a friend (and neither lists it as an enemy);
    an enemy if either side lists the other as an enemy and neither as a
    friend; otherwise neutral (including mixed signals).
    """
    a, b = int(a), int(b)
    a_friend = b in FRIENDS.get(a, set())
    b_friend = a in FRIENDS.get(b, set())
    a_enemy = b in ENEMIES.get(a, set())
    b_enemy = a in ENEMIES.get(b, set())

    friend = a_friend or b_friend
    enemy = a_enemy or b_enemy

    if friend and not enemy:
        return "friend"
    if enemy and not friend:
        return "enemy"
    if friend and enemy:
        return "neutral"  # mixed signals -> neutral
    return "neutral"


# --- Section computations --------------------------------------------------

def compute_moolank(day: int, keep_master: bool) -> dict:
    return {
        "day_of_birth": day,
        "number": reduce_to_single(day, keep_master),
        "ruling_planet": RULING_PLANET[reduce_to_single(day, False)],
    }


def compute_bhagyank(date_str: str, keep_master: bool) -> dict:
    digits = [int(c) for c in date_str if c.isdigit()]
    total = sum(digits)
    number = reduce_to_single(total, keep_master)
    chain = "+".join(str(d) for d in digits) + f"={total}"
    if total != number:
        chain += f"->{number}"
    return {
        "digit_sum": total,
        "number": number,
        "chain": chain,
        "ruling_planet": RULING_PLANET[reduce_to_single(total, False)],
    }


def compute_naamank(name: str, system: str, keep_master: bool) -> dict:
    letters = _letters(name)
    if not letters:
        return {}
    table = CHALDEAN_MAP if system == "chaldean" else PYTHAGOREAN_MAP
    values = [table[ch] for ch in letters if ch in table]
    compound = sum(values)
    number = reduce_to_single(compound, keep_master)
    return {
        "system": system,
        "letters": letters,
        "compound": compound,
        "number": number,
        "ruling_planet": RULING_PLANET[reduce_to_single(compound, False)],
    }


def compute_compatibility(naamank: int, moolank: int, bhagyank: int) -> dict:
    to_moolank = relation(naamank, moolank)
    to_bhagyank = relation(naamank, bhagyank)
    if to_moolank == "enemy" or to_bhagyank == "enemy":
        rec = ("Name number is in conflict with at least one core number; "
               "consider a name vibration friendly to both.")
    elif to_moolank == "friend" and to_bhagyank == "friend":
        rec = "Name number harmonizes well with both core numbers."
    else:
        rec = "Name number is broadly compatible (neutral or friendly)."
    return {
        "naamank_to_moolank": to_moolank,
        "naamank_to_bhagyank": to_bhagyank,
        "recommendation": rec,
    }


def compute_lo_shu(date_str: str) -> dict:
    digits = [int(c) for c in date_str if c.isdigit() and c != "0"]
    counts = {n: digits.count(n) for n in range(1, 10)}
    present = {n for n in range(1, 10) if counts[n] > 0}
    missing = sorted(n for n in range(1, 10) if counts[n] == 0)

    strength_arrows = []
    weakness_arrows = []
    for line, label in LO_SHU_LINES:
        cells = set(line)
        if cells <= present:
            strength_arrows.append(label)
        elif not (cells & present):
            weakness_arrows.append(label)

    return {
        "digits_used": digits,
        "counts": counts,
        "present": sorted(present),
        "missing": missing,
        "arrows_of_strength": strength_arrows,
        "arrows_of_weakness": weakness_arrows,
    }


def compute_personal_year(month: int, day: int, year: int) -> dict:
    base = month + day + reduce_to_single(year)
    number = reduce_to_single(base)
    return {
        "year": year,
        "number": number,
        "theme": NUMBER_THEME[number],
    }


def compute_lucky(planet: str) -> dict:
    attrs = LUCKY_ATTRIBUTES[planet]
    return {"ruling_planet": planet, **attrs}


def compute_name_correction(naamank: int, moolank: int, bhagyank: int) -> dict:
    to_moolank = relation(naamank, moolank)
    to_bhagyank = relation(naamank, bhagyank)
    harmonizes = to_moolank in ("friend", "neutral") and to_bhagyank in ("friend", "neutral")
    targets = sorted(
        n for n in range(1, 10)
        if relation(n, moolank) == "friend" and relation(n, bhagyank) == "friend"
    )
    if harmonizes:
        hint = ("Current name vibration harmonizes with your core numbers — "
                "no correction needed.")
    else:
        hint = ("Current name vibration conflicts with a core number. Aim for a "
                "Naamank that is a friend of BOTH your Moolank and Bhagyank. "
                "Adjust spelling toward one of the target numbers below "
                "(principle only — choose a spelling you like that reaches one of them).")
    return {
        "harmonizes": harmonizes,
        "target_numbers": targets,
        "hint": hint,
    }


# --- Top-level orchestration -----------------------------------------------

def compute(args) -> dict:
    y, m, d = (int(x) for x in args.date.split("-"))
    if not (1 <= m <= 12) or not (1 <= d <= 31):
        raise ValueError(f"invalid date: {args.date}")

    moolank = compute_moolank(d, args.keep_master)
    bhagyank = compute_bhagyank(args.date, args.keep_master)

    # Reduced (single-digit) forms used for relation math.
    moolank_s = reduce_to_single(d, False)
    bhagyank_s = reduce_to_single(sum(int(c) for c in args.date if c.isdigit()), False)

    systems = ["chaldean", "pythagorean"] if args.system == "both" else [args.system]

    naamank = {}
    compatibility = {}
    name_correction = {}
    if args.name:
        for sysname in systems:
            naamank[sysname] = compute_naamank(args.name, sysname, args.keep_master)
        # Use the first requested system for relation/correction logic.
        primary = naamank[systems[0]]
        if primary:
            naamank_s = reduce_to_single(primary["compound"], False)
            compatibility = compute_compatibility(naamank_s, moolank_s, bhagyank_s)
            name_correction = compute_name_correction(naamank_s, moolank_s, bhagyank_s)

    result = {
        "input": {
            "date": args.date,
            "name": args.name,
            "system": args.system,
            "year": args.year,
            "keep_master": args.keep_master,
        },
        "moolank": moolank,
        "bhagyank": bhagyank,
        "naamank": naamank,
        "compatibility": compatibility,
        "lo_shu": compute_lo_shu(args.date),
        "lucky": compute_lucky(moolank["ruling_planet"]),
        "name_correction": name_correction,
        "disclaimer": DISCLAIMER,
    }
    if args.year is not None:
        result["personal_year"] = compute_personal_year(m, d, args.year)
    return result


# --- Text rendering --------------------------------------------------------

def render_text(result: dict) -> str:
    i = result["input"]
    lines = []
    lines.append("=" * 60)
    lines.append("  NUMEROLOGY REPORT (Ank Jyotish)")
    lines.append("=" * 60)
    lines.append(f"  Date of birth: {i['date']}")
    if i["name"]:
        lines.append(f"  Name: {i['name']}")
    lines.append(f"  System(s): {i['system']} | keep-master: {i['keep_master']}")
    lines.append("-" * 60)

    mo = result["moolank"]
    lines.append(f"  MOOLANK (Psychic / Birth number): {mo['number']}")
    lines.append(f"    Day of birth {mo['day_of_birth']} -> {mo['number']} "
                 f"| Ruling planet: {mo['ruling_planet']}")

    bh = result["bhagyank"]
    lines.append(f"  BHAGYANK (Destiny / Life Path): {bh['number']}")
    lines.append(f"    {bh['chain']} | Ruling planet: {bh['ruling_planet']}")

    if result["naamank"]:
        lines.append("-" * 60)
        lines.append("  NAAMANK (Name number)")
        for sysname, na in result["naamank"].items():
            if not na:
                continue
            lines.append(f"    {sysname.title():<12} compound {na['compound']} "
                         f"-> {na['number']} | Ruling planet: {na['ruling_planet']}")

    if result["compatibility"]:
        c = result["compatibility"]
        lines.append("-" * 60)
        lines.append("  NUMBER COMPATIBILITY (Naamank vs core numbers)")
        lines.append(f"    Naamank vs Moolank:  {c['naamank_to_moolank']}")
        lines.append(f"    Naamank vs Bhagyank: {c['naamank_to_bhagyank']}")
        lines.append(f"    {c['recommendation']}")

    ls = result["lo_shu"]
    lines.append("-" * 60)
    lines.append("  LO SHU GRID")
    for row in LO_SHU_LAYOUT:
        cells = []
        for n in row:
            cnt = ls["counts"][n]
            cells.append(f"{n}x{cnt}" if cnt else " . ")
        lines.append("    " + "  ".join(f"{c:<4}" for c in cells))
    lines.append(f"    Missing numbers: {ls['missing'] or 'none'}")
    lines.append(f"    Arrows of Strength: {ls['arrows_of_strength'] or ['none']}")
    lines.append(f"    Arrows of Weakness: {ls['arrows_of_weakness'] or ['none']}")

    if "personal_year" in result:
        py = result["personal_year"]
        lines.append("-" * 60)
        lines.append(f"  PERSONAL YEAR {py['year']}: {py['number']}")
        lines.append(f"    {py['theme']}")

    lk = result["lucky"]
    lines.append("-" * 60)
    lines.append(f"  LUCKY ATTRIBUTES (Moolank ruler: {lk['ruling_planet']})")
    lines.append(f"    Gemstone: {lk['gemstone']} | Days: {lk['days']} | Colors: {lk['colors']}")

    if result["name_correction"]:
        nc = result["name_correction"]
        lines.append("-" * 60)
        lines.append("  NAME-CORRECTION HINT")
        lines.append(f"    {nc['hint']}")
        lines.append(f"    Target Naamank numbers (friend of both): {nc['target_numbers'] or 'none'}")

    lines.append("=" * 60)
    lines.append(f"  {result['disclaimer']}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Compute a numerology report.")
    ap.add_argument("--date", required=True, help="Date of birth YYYY-MM-DD")
    ap.add_argument("--name", default=None, help="Full name (optional)")
    ap.add_argument("--system", default="both",
                    choices=["chaldean", "pythagorean", "both"],
                    help="Name-number system (default both)")
    ap.add_argument("--year", type=int, default=None,
                    help="Year for personal-year calc (optional)")
    ap.add_argument("--keep-master", action="store_true", dest="keep_master",
                    help="Keep master numbers 11/22/33 unreduced where noted")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = ap.parse_args()

    try:
        result = compute(args)
    except Exception as e:  # noqa: BLE001 — surface a clean message to the agent
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))


if __name__ == "__main__":
    main()
