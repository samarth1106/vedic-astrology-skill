---
name: vedic-astrology
description: Compute Vedic (Hindu/jyotish) astrology charts and almanac data offline from birth details. Generates a Kundli birth chart (D1 Rashi — planets, signs, whole-sign houses, Lagna/ascendant, nakshatras and padas, retrogrades), the Vimshottari Dasha timeline (Mahadasha/Antardasha periods) plus a chart-aware interpretation of what the currently running dasha means across daily life, career, money, marriage, health, family, and enemies, the daily Panchang (tithi, nakshatra, yoga, karana, vara), and detects classical yogas (Gajakesari, Budhaditya, Raja, Pancha Mahapurusha). Uses the Swiss Ephemeris in sidereal mode with a configurable ayanamsa (Lahiri default). Use when the user says vedic astrology, jyotish, kundli, janam kundali, birth chart, horoscope, rashi, nakshatra, dasha, mahadasha, vimshottari, panchang, tithi, muhurta, lagna, ascendant, ayanamsa, divisional chart, varga, navamsa, dasamsha D9/D10, transit, gochar, Sade Sati, dhaiya, house/bhava analysis, remedy, upaya, gemstone, mantra, asks what their current dasha/mahadasha means or how a period will affect their life/career/money/marriage/health, asks to draw/visualise a kundli, or asks to cast/read a Hindu astrology chart.
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
| What the CURRENT dasha *means* — effects on life, career, money, marriage, health, family, enemies | `dasha_predict.py` |
| Daily almanac / panchang / tithi / Rahu Kaal / sunrise / muhurta | `panchang.py` |
| Yogas / chart combinations / raj yoga | `yogas.py` |
| Planetary strength / Ashtakavarga / Shadbala / bindus | `strength.py` |
| Divisional charts / vargas / D9 navamsa / D10 dasamsha / career-children-wealth chart | `varga.py` |
| Transits / gochar / Sade Sati / dhaiya / "what's Saturn doing now" / current sky | `gochar.py` |
| House-by-house / bhava report / "read my 7th/10th house" / house lords | `houses.py` |
| Remedies / upaya / gemstone / mantra / which planet to strengthen | `remedies.py` |
| Draw / visualise the chart / North or South Indian kundli diagram | `chart.py` |
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

# What the running dasha MEANS, across 10 life areas (chart-aware; --on defaults to today)
python3 dasha_predict.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --on 2026-06-04

# Panchang for a date (no birth data needed; --time defaults to noon)
python3 panchang.py --date 2026-06-04 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Yogas (aspect-aware)
python3 yogas.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Planetary strength: Ashtakavarga (full) + partial Shadbala
python3 strength.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Divisional charts (vargas): D9 marriage, D10 career, cross-varga strength
python3 varga.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --charts D9,D10   # or --charts all

# Transits + Sade Sati (gochar from natal Moon; --on defaults to today)
python3 gochar.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --on 2026-06-04

# Bhava (house-by-house) report; --house N for one house
python3 houses.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --house 10

# Traditional remedies for the dasha lord + weak/afflicted planets
python3 remedies.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# Draw the chart (South + North Indian ASCII); --varga D9 for navamsa
python3 chart.py --date 1990-08-15 --time 14:30:00 \
  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --style both --varga D1

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
   For how `dasha_predict.py` builds its life-area reading (the karaka → chart →
   blend model), load `references/dasha-effects.md`. For divisional charts (which
   varga reads which life area, and the honest caveat on the strength numbers),
   load `references/vargas.md`. For transits and Sade Sati, load
   `references/gochar.md`. Load these on demand — do not preload them.
4. **`dasha_predict.py` is the go-to when the user asks "what does my current
   dasha mean / how will this period affect me".** It already personalises the
   reading to the chart (house placement, lordship, dignity, combustion, and the
   Maha↔Antar relationship), so present its output as a *backdrop of
   probabilities, not a prediction.* Use `--on <date>` to read a past or future
   period.
5. **Pair dasha with transits.** For timing questions ("is this a good year",
   "what's happening now"), run `dasha_predict.py` (the backdrop) AND `gochar.py`
   (the trigger), and read them together. `gochar.py` also answers Sade Sati.
6. **Confirm life-area questions in the right varga.** Career → D10, marriage →
   D9, children → D7, wealth → D2 via `varga.py`; don't judge them from D1 alone.
7. **`remedies.py` output is TRADITIONAL/CULTURAL ONLY.** Always present it with
   the disclaimer that it is not advice and has no demonstrated effect, and never
   encourage spending money on gemstones or rituals.
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
