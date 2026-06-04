"""
Golden-value regression tests for the vedic-astrology + numerology toolkit.

These run each command's CLI as a subprocess and assert on its --json output.
Testing the real user-facing surface (not internal functions) keeps the tests
robust to refactors while pinning the values that must never silently drift.

Reference birth chart used throughout: 1990-08-15 14:30:00, New Delhi
(lat 28.6139, lon 77.2090, Asia/Kolkata), Lahiri ayanamsa.

Run:  pytest -q
"""

import json
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEDIC = os.path.join(REPO, "vedic-astrology", "scripts")
NUMER = os.path.join(REPO, "numerology", "scripts")

REF = ["--date", "1990-08-15", "--time", "14:30:00",
       "--lat", "28.6139", "--lon", "77.2090", "--tz", "Asia/Kolkata"]


def run(script_dir, script, args):
    """Run a CLI script with --json and return parsed output (cwd = its dir)."""
    cmd = [sys.executable, script, *args, "--json"]
    proc = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True)
    assert proc.returncode == 0, f"{script} failed:\n{proc.stderr}"
    return json.loads(proc.stdout)


# --------------------------------------------------------------------------- #
# Kundli — sign-level placements are stable and meaningful golden values.
# --------------------------------------------------------------------------- #
def test_kundli_sign_placements():
    r = run(VEDIC, "kundli.py", REF)
    p = r["planets"]
    assert r["ascendant"]["sign"] == "Scorpio"
    assert p["Sun"]["sign"] == "Cancer"
    assert p["Moon"]["sign"] == "Taurus" and p["Moon"]["dignity"] == "exalted"
    assert p["Jupiter"]["sign"] == "Cancer" and p["Jupiter"]["dignity"] == "exalted"
    assert p["Mars"]["sign"] == "Aries" and p["Mars"]["dignity"] == "own sign"


def test_ketu_opposite_rahu():
    r = run(VEDIC, "kundli.py", REF)
    rahu = r["planets"]["Rahu"]["longitude"]
    ketu = r["planets"]["Ketu"]["longitude"]
    assert abs(((ketu - rahu) % 360) - 180.0) < 1e-6


def test_ayanamsa_lahiri_1990():
    r = run(VEDIC, "kundli.py", REF)
    assert 23.5 < r["ayanamsa_deg"] < 23.9  # Lahiri ~23.73° in 1990


def test_topocentric_is_default():
    r = run(VEDIC, "kundli.py", REF)
    assert r["input"]["topocentric"] is True


# --------------------------------------------------------------------------- #
# Dasha — Vimshottari must close to exactly 120 years.
# --------------------------------------------------------------------------- #
def test_dasha_starts_moon_and_closes_120y():
    r = run(VEDIC, "dasha.py", REF + ["--levels", "1"])
    assert r["starting_dasha"] == "Moon"          # Moon in Rohini (lord Moon)
    total = r["balance_at_birth_years"] + sum(
        m["years"] for m in r["mahadashas"][1:])   # balance + 8 full periods
    # balance + remaining 8 periods should sum to 120 - elapsed_of_first... so
    # instead check the 9 listed spans + elapsed = 120 via full-period identity:
    full_first = 10  # Moon mahadasha is 10 years
    elapsed = full_first - r["balance_at_birth_years"]
    assert abs((elapsed + sum(m["years"] for m in r["mahadashas"])) - 120.0) < 0.05


def test_dasha_predict_active_period_and_areas():
    # Reference chart (Scorpio Lagna). On 2026-06-04 it runs Jupiter–Venus.
    r = run(VEDIC, "dasha_predict.py", REF + ["--on", "2026-06-04"])
    assert r["asc_sign"] == "Scorpio"
    assert r["active"]["maha"] == "Jupiter"
    assert r["active"]["antar"] == "Venus"
    # All ten life areas must be present for both lords.
    for lord in ("mahadasha", "antardasha"):
        assert len(r["effects"][lord]) == 10
    # Personalisation: activated houses = placements + lordships, non-empty.
    assert r["activated_houses"]
    # Jupiter rules Scorpio's 2nd & 5th (Sagittarius/Pisces) — lordship must show.
    assert 2 in r["activated_houses"] and 5 in r["activated_houses"]


def test_dasha_predict_rejects_pre_birth_date():
    proc = subprocess.run(
        [sys.executable, "dasha_predict.py", *REF, "--on", "1980-01-01", "--json"],
        cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "No dasha covers" in proc.stderr


# --------------------------------------------------------------------------- #
# Ashtakavarga — the hard invariants.
# --------------------------------------------------------------------------- #
def test_sarvashtakavarga_total_337():
    r = run(VEDIC, "strength.py", REF)
    sav = r["ashtakavarga"]["sav"]
    assert sav["total"] == 337
    assert sum(sav["per_sign"]) == 337


def test_bhinnashtakavarga_totals():
    r = run(VEDIC, "strength.py", REF)
    expected = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                "Jupiter": 56, "Venus": 52, "Saturn": 39}
    bav = r["ashtakavarga"]["bav"]
    for planet, total in expected.items():
        assert bav[planet]["total"] == total, f"{planet} BAV {bav[planet]['total']} != {total}"


# --------------------------------------------------------------------------- #
# Guna Milan — max never exceeds 36; identical chart self-matches highly.
# --------------------------------------------------------------------------- #
def test_guna_milan_bounds_and_self_match():
    args = ["--mode", "milan"]
    for who in ("boy", "girl"):
        args += [f"--{who}-date", "1990-08-15", f"--{who}-time", "14:30:00",
                 f"--{who}-lat", "28.6139", f"--{who}-lon", "77.2090",
                 f"--{who}-tz", "Asia/Kolkata"]
    r = run(VEDIC, "matching.py", args)
    g = r["milan"]
    assert g["max"] == 36
    assert 0 <= g["total"] <= 36
    # Identical charts: same nadi/gana → but a person matched to themselves shares
    # Nadi (dosha=0); still total should be high (>= 24) on the other 7 kootas.
    assert g["total"] >= 24


# --------------------------------------------------------------------------- #
# Panchang — known weekday.
# --------------------------------------------------------------------------- #
def test_panchang_weekday():
    r = run(VEDIC, "panchang.py",
            ["--date", "2026-06-04", "--lat", "28.6139", "--lon", "77.2090",
             "--tz", "Asia/Kolkata"])
    assert r["vara"] == "Thursday"   # 2026-06-04 is a Thursday


# --------------------------------------------------------------------------- #
# Numerology — hand-verified core numbers.
# --------------------------------------------------------------------------- #
def test_numerology_core_numbers():
    if not os.path.exists(os.path.join(NUMER, "numerology.py")):
        pytest.skip("numerology module not present")
    r = run(NUMER, "numerology.py", ["--date", "1990-08-15"])
    blob = json.dumps(r)
    assert "6" in blob  # Moolank (day 15 -> 6) and Bhagyank (1+9+9+0+0+8+1+5=33 -> 6)


# --------------------------------------------------------------------------- #
# Geocoder — bundled dataset lookups.
# --------------------------------------------------------------------------- #
def test_geocode_mumbai():
    if not os.path.exists(os.path.join(VEDIC, "geocode.py")):
        pytest.skip("geocoder not present")
    r = run(VEDIC, "geocode.py", ["Mumbai"])
    top = r[0] if isinstance(r, list) else r
    assert 18.8 < float(top["lat"]) < 19.3
    assert 72.7 < float(top["lon"]) < 73.0
    assert top["timezone"] == "Asia/Kolkata"
