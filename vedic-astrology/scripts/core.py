"""
core.py — Shared Swiss Ephemeris engine for the vedic-astrology skill.

This module owns ALL interaction with Swiss Ephemeris (via pyswisseph) and the
shared Vedic constants. Every command script (kundli, dasha, panchang, yogas)
imports from here so that sidereal mode, ayanamsa, and ephemeris flags are
configured in exactly one place.

Design notes:
- We use the Moshier ephemeris (swe.FLG_MOSEPH), which is analytical and built
  into the Swiss Ephemeris C library. This means NO external .se1 data files are
  required — the skill runs fully offline after `pip install pyswisseph`.
  Accuracy is ~arc-second for modern dates, far beyond what jyotish needs.
- Sidereal (Vedic) mode is enforced globally. Default ayanamsa is Lahiri.
- All longitudes returned are sidereal, in degrees [0, 360).

Licensing: depends on pyswisseph / Swiss Ephemeris (AGPL-3.0 or commercial).
See the repository LICENSE and NOTICE files.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

import pytz
import swisseph as swe

# --------------------------------------------------------------------------- #
# Ayanamsa registry — maps friendly names to Swiss Ephemeris sidereal modes.
# --------------------------------------------------------------------------- #
AYANAMSA = {
    "lahiri": swe.SIDM_LAHIRI,          # Chitrapaksha — Indian govt standard (default)
    "raman": swe.SIDM_RAMAN,
    "kp": swe.SIDM_KRISHNAMURTI,        # Krishnamurti Paddhati
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar": swe.SIDM_YUKTESHWAR,
    "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
}
DEFAULT_AYANAMSA = "lahiri"

# House systems we expose. Whole Sign ('W') is the Vedic default.
HOUSE_SYSTEMS = {
    "whole_sign": b"W",
    "placidus": b"P",
    "equal": b"E",
}
DEFAULT_HOUSE_SYSTEM = "whole_sign"

# Base ephemeris flags: sidereal + speed (for retrograde) + Moshier (offline).
_BASE_FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_MOSEPH

# --------------------------------------------------------------------------- #
# Vedic reference data
# --------------------------------------------------------------------------- #
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign lord (rashi adhipati), 1-indexed by sign number 1..12.
SIGN_LORD = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

# 27 Nakshatras in order. Each spans 13°20' = 13.3333°.
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Vimshottari dasha lords cycle (repeats every 9 nakshatras) and their years.
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}  # total = 120

# Planet name -> Swiss Ephemeris body id. Ketu is derived (Rahu + 180).
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,   # Mean lunar node (north). Ketu = Rahu + 180.
}

NAKSHATRA_SPAN = 360.0 / 27.0       # 13.3333...
PADA_SPAN = NAKSHATRA_SPAN / 4.0    # 3.3333...

# Exaltation / own-sign tables for dignity & Mahapurusha yogas (sign numbers 1..12).
EXALTATION = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7,
}
OWN_SIGNS = {
    "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
    "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11],
}


# --------------------------------------------------------------------------- #
# Engine init & time conversion
# --------------------------------------------------------------------------- #
def init_engine(ayanamsa: str = DEFAULT_AYANAMSA) -> None:
    """Configure Swiss Ephemeris for sidereal (Vedic) calculation.

    Must be called once before any calc. Idempotent.
    """
    key = ayanamsa.strip().lower()
    if key not in AYANAMSA:
        raise ValueError(
            f"Unknown ayanamsa '{ayanamsa}'. Choose from: {', '.join(sorted(AYANAMSA))}"
        )
    swe.set_sid_mode(AYANAMSA[key], 0, 0)


def to_julian_ut(
    year: int, month: int, day: int,
    hour: int, minute: int, second: int,
    tz_name: str,
) -> float:
    """Convert a *local* civil datetime + IANA timezone to a Julian Day (UT).

    Example tz_name: 'Asia/Kolkata', 'America/New_York', 'UTC'.
    Raises pytz.UnknownTimeZoneError on a bad timezone string.
    """
    tz = pytz.timezone(tz_name)
    local_dt = tz.localize(datetime(year, month, day, hour, minute, second))
    utc_dt = local_dt.astimezone(pytz.utc)
    ut_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour, swe.GREG_CAL)


# --------------------------------------------------------------------------- #
# Position helpers
# --------------------------------------------------------------------------- #
def sidereal_longitude(jd: float, body: int) -> Tuple[float, float]:
    """Return (longitude_deg, speed_deg_per_day) for a body, sidereal frame.

    Negative speed => retrograde.
    """
    pos, _ = swe.calc_ut(jd, body, _BASE_FLAGS)
    return pos[0] % 360.0, pos[3]


def all_planet_positions(jd: float) -> Dict[str, dict]:
    """Compute sidereal positions for all 9 grahas including Rahu/Ketu.

    Returns a dict keyed by planet name with longitude, sign, degree-in-sign,
    nakshatra, pada, and retrograde flag.
    """
    out: Dict[str, dict] = {}
    for name, body in PLANETS.items():
        lon, speed = sidereal_longitude(jd, body)
        retro = speed < 0
        # Nodes are always retrograde in mean-node model; flag explicitly.
        if name == "Rahu":
            retro = True
        out[name] = _describe_point(lon, retrograde=retro)
    # Ketu is exactly opposite Rahu.
    ketu_lon = (out["Rahu"]["longitude"] + 180.0) % 360.0
    out["Ketu"] = _describe_point(ketu_lon, retrograde=True)
    return out


def _describe_point(lon: float, retrograde: bool = False) -> dict:
    """Decompose a sidereal longitude into sign/nakshatra/pada components."""
    sign_num = int(lon // 30) + 1            # 1..12
    deg_in_sign = lon % 30.0
    nak_index = int(lon // NAKSHATRA_SPAN)   # 0..26
    pada = int((lon % NAKSHATRA_SPAN) // PADA_SPAN) + 1  # 1..4
    return {
        "longitude": round(lon, 4),
        "sign": SIGNS[sign_num - 1],
        "sign_num": sign_num,
        "degree_in_sign": round(deg_in_sign, 4),
        "nakshatra": NAKSHATRAS[nak_index],
        "nakshatra_lord": DASHA_SEQUENCE[nak_index % 9],
        "pada": pada,
        "retrograde": retrograde,
    }


def ascendant(jd: float, lat: float, lon: float, house_system: str = DEFAULT_HOUSE_SYSTEM) -> dict:
    """Compute the sidereal Lagna (ascendant) and its sign."""
    if house_system not in HOUSE_SYSTEMS:
        raise ValueError(
            f"Unknown house system '{house_system}'. Choose from: {', '.join(HOUSE_SYSTEMS)}"
        )
    _, ascmc = swe.houses_ex(jd, lat, lon, HOUSE_SYSTEMS[house_system], swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360.0
    return _describe_point(asc_lon)


def house_of(planet_sign_num: int, asc_sign_num: int) -> int:
    """Whole-sign house number (1..12) of a planet given the ascendant sign.

    In whole-sign houses, the ascendant's sign is house 1 and each subsequent
    sign is the next house.
    """
    return ((planet_sign_num - asc_sign_num) % 12) + 1


def deg_to_dms(deg: float) -> str:
    """Format a degree-in-sign value as Dd Mm Ss for human-readable output."""
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = int((m_full - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""
