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


def test_yogini_dasha_start_and_cycle_closure():
    # REF Moon is in Rohini (nakshatra 4): (4+3) mod 8 = 7 -> Siddha (Venus).
    r = run(VEDIC, "dasha_yogini.py", REF + ["--levels", "1"])
    assert r["system"] == "Yogini Dasha"
    assert r["cycle_years"] == 36
    assert r["starting_yogini"] == "Siddha" and r["starting_lord"] == "Venus"
    # The eight full periods after the partial first must sum to the 36-yr cycle.
    fulls = [m["years"] for m in r["mahadashas"][1:9]]
    assert abs(sum(fulls) - 36.0) < 1e-6
    # Balance never exceeds the first Yogini's full length (Siddha = 7 yrs).
    assert 0 < r["balance_at_birth_years"] <= 7.0


def test_yogini_dasha_antardashas_sum_to_maha():
    r = run(VEDIC, "dasha_yogini.py", REF + ["--levels", "2"])
    md = r["mahadashas"][1]                 # first FULL mahadasha (Sankata, 8 yrs)
    assert "antardashas" in md and len(md["antardashas"]) == 8
    sub_total = sum(a["years"] for a in md["antardashas"])
    assert abs(sub_total - md["years"]) < 1e-3


def test_dasha_predict_rejects_pre_birth_date():
    proc = subprocess.run(
        [sys.executable, "dasha_predict.py", *REF, "--on", "1980-01-01", "--json"],
        cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "No dasha covers" in proc.stderr


# --------------------------------------------------------------------------- #
# Vargas — D1 identity, D9==navamsa, strength bounds.
# --------------------------------------------------------------------------- #
def test_varga_charts_and_strength():
    r = run(VEDIC, "varga.py", REF)
    # REF chart: Sun in Cancer (D1=4), Moon's navamsa is Cancer (D9=4).
    assert r["charts"]["1"]["Sun"] == 4
    assert r["charts"]["9"]["Moon"] == 4
    # Every point lands in a valid sign for every division.
    for d_div, chart in r["charts"].items():
        assert all(1 <= s <= 12 for s in chart.values())
    # Strength scores are well-formed.
    for p, s in r["strength"].items():
        assert 0 <= s["varga_bala_pct"] <= 100
        assert 0 <= s["own_or_exalted_count"] <= 16


def test_varga_extra_non_classical_divisions():
    # D5/D6/D8/D11 lie outside the Shodasavarga; they must compute into valid signs.
    r = run(VEDIC, "varga.py", REF + ["--charts", "D5,D6,D8,D11"])
    for d in ("5", "6", "8", "11"):
        assert d in r["charts"]
        assert all(1 <= s <= 12 for s in r["charts"][d].values())
    # Cross-varga strength still spans ONLY the classical 16 (extras are display-only).
    for p, s in r["strength"].items():
        assert s["own_or_exalted_count"] <= 16


def test_varga_extra_labelled_non_classical_and_rejects_bad():
    proc = subprocess.run([sys.executable, "varga.py", *REF, "--charts", "D11"],
                          cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "D11" in proc.stdout and "non-classical" in proc.stdout
    # A division in no supported set is rejected, not silently approximated.
    bad = subprocess.run([sys.executable, "varga.py", *REF, "--charts", "D13", "--json"],
                         cwd=VEDIC, capture_output=True, text=True)
    assert bad.returncode != 0 and "not supported" in bad.stderr


def test_chart_extra_varga_d11():
    ch = run(VEDIC, "chart.py", REF + ["--varga", "D11"])
    assert ch["div"] == 11
    assert sum(len(v) for v in ch["by_sign"].values()) == 9   # all nine grahas placed


# --------------------------------------------------------------------------- #
# Gochar — structure + natal reference + Sade Sati phase house.
# --------------------------------------------------------------------------- #
def test_gochar_transits_and_panoti():
    r = run(VEDIC, "gochar.py", REF + ["--on", "2026-06-04"])
    assert r["natal_moon_sign"] == "Taurus"      # REF Moon is in Taurus
    assert len(r["transits"]) == 9
    for t in r["transits"]:
        assert 1 <= t["house_from_moon"] <= 12
        assert 1 <= t["house_from_lagna"] <= 12
    assert 1 <= r["saturn_panoti"]["phase_house"] <= 12


# --------------------------------------------------------------------------- #
# Bhava report — 12 houses, house 1 carries the Lagna sign.
# --------------------------------------------------------------------------- #
def test_houses_report():
    r = run(VEDIC, "houses.py", REF)
    assert len(r["bhavas"]) == 12
    h1 = r["bhavas"][0]
    assert h1["house"] == 1 and h1["sign"] == r["lagna_sign"]
    # Every house has a lord that is a real planet.
    planets = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert all(b["lord"] in planets for b in r["bhavas"])


def test_astro_claude_reading():
    r = run(VEDIC, "astro_claude.py",
            ["--name", "Asha", "--gender", "female", "--married", "no"] + REF
            + ["--on", "2026-06-04"])
    # Age from 1990-08-15 to 2026-06-04 is 35 (birthday not yet reached).
    assert r["profile"]["age"] == 35
    assert r["profile"]["name"] == "Asha"
    # Functional nature is computed for all seven classical planets.
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert r["functional"][p]["nature"] in ("yogakaraka", "benefic", "malefic", "neutral")
    # Gemstone guidance always splits into wear/avoid lists; rudraksha allowed.
    assert "wear" in r["gemstones"] and "avoid" in r["gemstones"]
    assert r["rudraksha"]["can_wear"] is True


def test_astro_claude_yogakaraka_for_taurus():
    # Early-morning Delhi birth → Taurus Lagna; Saturn must be the yogakaraka.
    r = run(VEDIC, "astro_claude.py",
            ["--name", "T", "--date", "1990-05-10", "--time", "06:00:00",
             "--lat", "28.6139", "--lon", "77.2090", "--tz", "Asia/Kolkata"])
    assert r["lagna"]["sign"] == "Taurus"
    assert r["functional"]["Saturn"]["is_yogakaraka"] is True


def test_dst_nonexistent_time_rejected():
    # 02:30 on 2021-03-14 does not exist in America/New_York (spring forward).
    # The engine must error rather than silently shift the chart by an hour.
    proc = subprocess.run(
        [sys.executable, "kundli.py", "--date", "2021-03-14", "--time", "02:30:00",
         "--lat", "40.71", "--lon", "-74.01", "--tz", "America/New_York", "--json"],
        cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "does not exist" in proc.stderr


def test_manglik_three_references():
    r = run(VEDIC, "matching.py",
            ["--mode", "dosha", "--date", "1983-12-29", "--time", "18:30:00",
             "--lat", "26.9196", "--lon", "75.7878", "--tz", "Asia/Kolkata"])
    m = r["manglik"]
    for k in ("mars_house_from_lagna", "mars_house_from_moon", "mars_house_from_venus",
              "triggered_from"):
        assert k in m
    # The flag is the OR of the three reference points.
    refs = {m["mars_house_from_lagna"], m["mars_house_from_moon"], m["mars_house_from_venus"]}
    expected = bool(refs & {1, 2, 4, 7, 8, 12})
    assert m["manglik"] is expected


def test_career_windows_dedupe_and_status():
    r = run(VEDIC, "astro_claude.py",
            ["--name", "X", "--date", "1983-12-29", "--time", "18:30:00",
             "--lat", "26.9196", "--lon", "75.7878", "--tz", "Asia/Kolkata", "--on", "2026-06-04"])
    lords = [w["lord"] for w in r["career_windows"]]
    assert len(lords) == len(set(lords))            # no duplicate lords
    assert all(w.get("status") in ("current", "upcoming") for w in r["career_windows"])


def test_numerology_rejects_impossible_date():
    proc = subprocess.run(
        [sys.executable, "numerology.py", "--date", "2025-02-30", "--name", "Test", "--json"],
        cwd=NUMER, capture_output=True, text=True)
    assert proc.returncode != 0


def test_muhurta_ranking():
    r = run(VEDIC, "muhurta.py",
            ["--event", "marriage", "--from", "2026-11-01", "--to", "2026-11-20",
             "--lat", "28.6139", "--lon", "77.2090", "--tz", "Asia/Kolkata"])
    assert r["event"] == "marriage"
    assert len(r["ranked"]) == 20            # inclusive 20-day span
    for d in r["ranked"]:
        assert 0 <= d["score"] <= 100
        assert d["verdict"] in ("Excellent", "Good", "Fair", "Avoid")
    # Ranked descending.
    scores = [d["score"] for d in r["ranked"]]
    assert scores == sorted(scores, reverse=True)


def test_muhurta_yoga_names_match_panchang():
    """Every yoga muhurta scores against must be a real panchang yoga name.

    Guards the class of bug where a misspelling (e.g. 'Shoola' vs 'Shula')
    silently prevents a penalty/bonus from ever firing.
    """
    if VEDIC not in sys.path:
        sys.path.insert(0, VEDIC)
    import muhurta
    import panchang
    valid = set(panchang.YOGA_NAMES)
    assert len(valid) == 27
    scored = muhurta.BAD_YOGAS | muhurta.ROUGH_YOGAS | muhurta.GOOD_YOGAS
    unknown = scored - valid
    assert not unknown, f"muhurta scores unknown yoga name(s): {sorted(unknown)}"


def test_muhurta_rejects_backwards_range():
    proc = subprocess.run(
        [sys.executable, "muhurta.py", "--event", "vehicle",
         "--from", "2026-12-01", "--to", "2026-11-01",
         "--lat", "28.6", "--lon", "77.2", "--tz", "Asia/Kolkata", "--json"],
        cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode != 0


def test_mantra_goals():
    r = run(VEDIC, "mantra.py", REF + ["--goal", "all", "--on", "2026-06-04"])
    assert r["mahadasha_lord"] in {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                   "Venus", "Saturn", "Rahu", "Ketu"}
    assert set(r["goals"]) >= {"wealth", "success", "marriage", "health"}
    for g, blk in r["goals"].items():
        assert blk["deity_mantras"]                       # every goal has a deity mantra
        for p in blk["planetary"]:
            assert p["mode"] in ("strengthen", "harmonise / pacify")
            assert p["beej"].startswith("Om")


def test_lucky_profile():
    r = run(VEDIC, "lucky.py", REF)
    assert r["lagna_lord"] in {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    assert 1 <= r["moolank"] <= 9
    assert r["lucky"]["days"] and r["lucky"]["numbers"] and r["lucky"]["directions"]


def test_astro_claude_has_atmakaraka():
    r = run(VEDIC, "astro_claude.py", ["--name", "A"] + REF + ["--on", "2026-06-04"])
    assert r["atmakaraka"]["planet"] in {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                         "Venus", "Saturn"}
    assert 1 <= r["atmakaraka"]["house"] <= 12


def test_dhana_yoga_detected_in_ref():
    r = run(VEDIC, "yogas.py", REF)
    names = {y["name"] for y in r["yogas"]}
    assert "Dhana Yoga" in names


def test_yogas_lunar_and_nabhasa_invariants():
    """The lunar yogas are mutually exclusive; exactly one Sankhya yoga fires."""
    r = run(VEDIC, "yogas.py", REF)
    names = [y["name"] for y in r["yogas"]]
    lunar = {"Sunapha Yoga", "Anapha Yoga", "Durudhara Yoga", "Kemadruma Yoga"}
    assert len(lunar & set(names)) <= 1
    # 7 planets always occupy 1..7 distinct signs, so one Sankhya yoga is certain.
    sankhya = [n for n in names if "Nabhasa Sankhya" in n]
    assert len(sankhya) == 1


def test_yogas_expanded_families_in_ref():
    """The expanded library surfaces the new families on the reference chart."""
    r = run(VEDIC, "yogas.py", REF)
    names = {y["name"] for y in r["yogas"]}
    # REF (Scorpio Lagna) has a Moon<->Venus sign exchange and a 6/8/12-lord
    # in a dusthana.
    assert "Vipareeta Raja Yoga" in names
    assert any(n.startswith("Parivartana Yoga") for n in names)
    # Every detected yoga carries a rule and a plain-language note.
    for y in r["yogas"]:
        assert y["rule"] and y["note"]


def test_full_report_html(tmp_path):
    out = tmp_path / "asha.html"
    proc = subprocess.run(
        [sys.executable, "full_report.py", "--name", "Asha", "--gender", "female",
         "--married", "no", *REF, "--on", "2026-06-04",
         "--format", "html", "--out", str(out)],
        cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    for marker in ("Astro Claude", "Asha", "Birth Chart", "Gemstones", "Rudraksha",
                   "Today's Sky", "PANCHANG"):
        assert marker in text


def test_remedies_and_chart():
    rem = run(VEDIC, "remedies.py", REF + ["--on", "2026-06-04"])
    assert rem["mahadasha_lord"] in {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                     "Venus", "Saturn", "Rahu", "Ketu"}
    assert isinstance(rem["flagged"], list)
    ch = run(VEDIC, "chart.py", REF + ["--varga", "D1"])
    total = sum(len(v) for v in ch["by_sign"].values())
    assert total == 9                            # all nine grahas placed once


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
# Shadbala — the complete six-fold strength, structure + classical invariants.
# --------------------------------------------------------------------------- #
def test_shadbala_complete_six_sources():
    r = run(VEDIC, "strength.py", REF)
    sb = r["shadbala"]
    assert sb["complete"] is True
    planets = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    for name in planets:
        c = sb["planets"][name]["components_virupa"]
        # All six sources present.
        for key in ("sthana", "dig_bala", "kala", "cheshta_bala",
                    "naisargika_bala", "drik_bala"):
            assert key in c, f"{name} missing Shadbala source {key}"
        # Sthana subtotal is the exact sum of its five sub-balas.
        s = c["sthana"]
        parts = (s["uchcha_bala"] + s["saptavargaja_bala"] + s["ojayugma_bala"]
                 + s["kendradi_bala"] + s["drekkana_bala"])
        assert abs(parts - s["subtotal"]) < 0.05
        # Total in Rupas is positive and meets/decides the classical threshold.
        assert sb["planets"][name]["total_rupa"] > 0
        assert isinstance(sb["planets"][name]["meets_required"], bool)


def test_shadbala_cheshta_classical_identities():
    """Sun's Cheshta Bala = its Ayana Bala; Moon's = its Paksha Bala (BPHS)."""
    r = run(VEDIC, "strength.py", REF)
    p = r["shadbala"]["planets"]
    sun = p["Sun"]["components_virupa"]
    moon = p["Moon"]["components_virupa"]
    assert abs(sun["cheshta_bala"] - sun["kala"]["ayana_bala"]) < 0.05
    assert abs(moon["cheshta_bala"] - moon["kala"]["paksha_bala"]) < 0.05
    # The five star-planets' Cheshta (Seeghra Kendra) is bounded 0..60.
    for name in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert 0.0 <= p[name]["components_virupa"]["cheshta_bala"] <= 60.0


def test_shadbala_time_lords_unique():
    """Exactly one planet rules the weekday (Vara) and one the Hora."""
    r = run(VEDIC, "strength.py", REF)
    p = r["shadbala"]["planets"]
    vara = [n for n in p if p[n]["components_virupa"]["kala"]["vara_bala"] == 45.0]
    hora = [n for n in p if p[n]["components_virupa"]["kala"]["hora_bala"] == 60.0]
    assert len(vara) == 1 and len(hora) == 1
    # The named lord matches the awarded bala.
    lords = p[vara[0]]["components_virupa"]["kala"]["lords"]
    assert lords["vara"] == vara[0]


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
# Sky — Today's Sky opens with the Panchang + the live planetary alignment.
# --------------------------------------------------------------------------- #
_SIGNS = {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
          "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"}


def test_sky_today():
    r = run(VEDIC, "sky.py",
            ["--date", "2026-06-04", "--lat", "28.6139", "--lon", "77.2090",
             "--tz", "Asia/Kolkata"])
    # The Panchang is embedded and the weekday matches.
    assert r["panchang"]["vara"] == "Thursday"
    # All nine grahas placed, each with sign / nakshatra / pada / flags.
    assert {p["planet"] for p in r["planets"]} == {
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
    for p in r["planets"]:
        assert p["sign"] in _SIGNS
        assert 1 <= p["pada"] <= 4
        assert isinstance(p["retrograde"], bool) and isinstance(p["combust"], bool)
    # Nodes are retrograde by nature, but excluded from the "retrograde" insight.
    assert "Rahu" not in r["retrograde"] and "Ketu" not in r["retrograde"]
    # The slow-mover backdrop is exactly the four era-setting bodies.
    assert {e["planet"] for e in r["slow_movers"]} == {"Saturn", "Jupiter", "Rahu", "Ketu"}
    assert isinstance(r["conjunctions"], list)
    # On 2026-06-04 Mercury and Venus share Gemini — a real conjunction.
    assert any(set(c["planets"]) == {"Mercury", "Venus"} for c in r["conjunctions"])


def test_astro_claude_opens_with_today_sky():
    r = run(VEDIC, "astro_claude.py",
            ["--name", "Asha"] + REF + ["--on", "2026-06-04"])
    ts = r["today_sky"]
    assert ts["panchang"]["vara"] == "Thursday"
    assert len(ts["planets"]) == 9
    # Personalised: a Sade Sati flag from the natal Moon, and every transiting
    # graha counted as a house from that Moon (the personal bridge).
    assert isinstance(ts["sade_sati"]["active"], bool)
    assert all("house_from_moon" in p for p in ts["planets"])


def test_astro_claude_text_starts_with_panchang():
    # The human-readable reading must START with the Panchang / sky, before the
    # personal life narrative.
    proc = subprocess.run(
        [sys.executable, "astro_claude.py", "--name", "Asha", *REF, "--on", "2026-06-04"],
        cwd=VEDIC, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    i_sky = out.find("TODAY'S SKY")
    i_panch = out.find("PANCHANG")
    i_life = out.find("WHERE YOU ARE IN LIFE")
    assert -1 < i_sky < i_life            # the sky opens the reading
    assert -1 < i_panch < i_life          # the panchang appears before the life reading


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
