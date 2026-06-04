---
name: vedic-astrology
description: Compute Vedic (Hindu/jyotish) astrology charts and almanac data offline from birth details. Generates a Kundli birth chart (D1 Rashi — planets, signs, whole-sign houses, Lagna/ascendant, nakshatras and padas, retrogrades), the Vimshottari Dasha timeline (Mahadasha/Antardasha periods), the daily Panchang (tithi, nakshatra, yoga, karana, vara), and detects classical yogas (Gajakesari, Budhaditya, Raja, Pancha Mahapurusha). Uses the Swiss Ephemeris in sidereal mode with a configurable ayanamsa (Lahiri default). Use when the user says vedic astrology, jyotish, kundli, janam kundali, birth chart, horoscope, rashi, nakshatra, dasha, mahadasha, vimshottari, panchang, tithi, muhurta, lagna, ascendant, ayanamsa, or asks to cast/read a Hindu astrology chart.
license: AGPL-3.0
---

# Vedic Astrology (Jyotish)

Offline Vedic astrology computation engine. All math runs locally via the Swiss
Ephemeris — no API keys, no network. Sidereal (Vedic) zodiac with a configurable
ayanamsa (default **Lahiri / Chitrapaksha**).

> **Disclaimer — state this to the user when presenting results.** This skill is
> for cultural, educational, and entertainment purposes. Astrological readings are
> not scientifically validated and must not be used for medical, financial, legal,
> or other consequential decisions.

## Setup (once)

```bash
pip install -r requirements.txt   # pyswisseph + pytz
```

If the import fails, tell the user to run that command. The skill cannot compute
anything without `pyswisseph`.

## Required inputs

Before running any birth-chart command (kundli, dasha, yogas), you MUST have:

| Input | Format | Example | Notes |
|-------|--------|---------|-------|
| Date  | `YYYY-MM-DD` | `1990-08-15` | Birth date (local) |
| Time  | `HH:MM[:SS]` 24h | `14:30:00` | **Local clock time at birthplace.** Critical — the Lagna shifts ~1°/4min. |
| Lat   | decimal deg | `28.6139` | North positive |
| Lon   | decimal deg | `77.2090` | **East positive, West negative** |
| TZ    | IANA name | `Asia/Kolkata` | NOT an offset like +5:30 |

**If birth time is unknown:** warn the user that the ascendant, houses, and
Moon-based dasha timing will be unreliable. Offer to proceed with a noon default
*only* for sign-level (not house-level) information, and label it clearly.

**If only a city is given:** ask for, or look up, its latitude/longitude and IANA
timezone before running. Do not guess coordinates silently.

## Routing — which script to run

All scripts live in `scripts/` and accept `--json` for machine-readable output.
Run them with the working directory set to `scripts/` (they import `core`).

| User wants… | Script | 
|-------------|--------|
| Birth chart / kundli / planets / houses / lagna / rashi | `kundli.py` |
| Life periods / dasha / mahadasha / antardasha / timeline | `dasha.py` |
| Daily almanac / panchang / tithi / Rahu Kaal / sunrise / muhurta | `panchang.py` |
| Yogas / chart combinations / raj yoga | `yogas.py` |
| Planetary strength / Ashtakavarga / Shadbala / bindus | `strength.py` |
| Marriage matching / Guna Milan / kundli milan / 36 gunas / Manglik / Kaal Sarpa | `matching.py` |
| Look up a city's coordinates + timezone | `geocode.py` |

**Tip:** if the user gives a city instead of coordinates, run
`python3 geocode.py "<city>"` first to resolve `--lat --lon --tz`, then feed those
into the chart commands. For numerology (life path / moolank / lo shu), use the
sibling **`numerology`** skill, not these scripts.

### Examples

```bash
cd scripts

# Kundli (birth chart)
python3 kundli.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Vimshottari dasha (--levels 1 = Mahadasha only, 2 = + Antardasha)
python3 dasha.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --levels 2

# Panchang for a date (no birth data needed; --time defaults to noon)
python3 panchang.py --date 2026-06-04 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Yogas (aspect-aware)
python3 yogas.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Planetary strength: Ashtakavarga (full) + partial Shadbala
python3 strength.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Marriage matching (Guna Milan, 36 gunas) + Manglik for both
python3 matching.py --mode milan \
  --boy-date 1990-08-15 --boy-time 14:30:00 --boy-lat 28.61 --boy-lon 77.21 --boy-tz Asia/Kolkata \
  --girl-date 1992-03-10 --girl-time 09:15:00 --girl-lat 19.07 --girl-lon 72.88 --girl-tz Asia/Kolkata

# Dosha scan for one chart (Manglik + Kaal Sarpa)
python3 matching.py --mode dosha --date 1990-08-15 --time 14:30:00 \
  --lat 28.61 --lon 77.21 --tz Asia/Kolkata
```

### Optional flags

- `--ayanamsa` — `lahiri` (default), `raman`, `kp`, `yukteshwar`, `fagan_bradley`
- `--house-system` — `whole_sign` (default), `placidus`, `equal` (kundli/yogas)
- `--node` — `mean` (default) or `true` lunar node for Rahu/Ketu
- `--geocentric` — opt out of the default **topocentric** positions (birth charts
  are topocentric by default — important for the Moon and therefore the dasha)
- `--ephemeris` — `moshier` (default, offline) or `swiss` (needs `.se1` files)
- `--levels` (dasha) — `1` Mahadasha, `2` +Antardasha (default), `3` +Pratyantardasha
- `--json` — emit JSON for further processing instead of the formatted text table

## Presenting results

1. Run the script; it prints a clean text table by default — you can relay that
   directly, or use `--json` and reformat.
2. **Always restate the disclaimer** when giving an interpretation.
3. For interpretation depth (what a planet-in-house or nakshatra *means*), load
   `references/interpretation.md`. For yoga definitions and caveats, load
   `references/yogas.md`. For nakshatra details, `references/nakshatras.md`.
   Load these on demand — do not preload them.
4. Be honest about scope: yoga detection is a **curated subset**, not exhaustive;
   panchang reports values at the given clock time (elements change through the day);
   the weekday uses the civil date (Vedic days run sunrise-to-sunrise).

## How it works (for debugging)

- `scripts/core.py` owns ALL Swiss Ephemeris setup: sidereal mode, ayanamsa,
  the Moshier ephemeris flag (so no `.se1` data files are needed), planet IDs,
  nakshatra/sign/dasha constants, and time conversion. The four command scripts
  import from it. If positions look wrong, check `core.init_engine()` and the
  ayanamsa first.
- Longitudes are sidereal. Tithi uses the Moon−Sun difference (ayanamsa-independent);
  nakshatra and yoga use sidereal longitudes (ayanamsa-dependent).
- Ketu is computed as Rahu + 180°; Rahu uses the mean lunar node.

## Common failures

| Symptom | Cause / fix |
|---------|-------------|
| `ModuleNotFoundError: swisseph` | `pip install -r requirements.txt` |
| `pytz.UnknownTimeZoneError` | TZ must be an IANA name (`Asia/Kolkata`), not `+5:30` |
| Ascendant looks 23° off | Likely a tropical-vs-sidereal mix-up; confirm `--ayanamsa` |
| Wrong houses | Confirm `--house-system`; Vedic default is `whole_sign` |
| Lagna seems wrong | Almost always wrong birth time or timezone — re-confirm with user |
