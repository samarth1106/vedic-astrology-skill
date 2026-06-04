# 🪔 Vedic Astrology & Numerology — Claude Code Skills (Jyotish + Ank Jyotish)

Offline **Vedic / Hindu astrology** and **numerology** skills for
[Claude Code](https://claude.com/claude-code). Cast a birth chart, compute dasha
periods, generate the daily panchang (with Rahu Kaal & sunrise), detect classical
yogas, score planetary strength (Ashtakavarga + Shadbala), match horoscopes
(36-point Guna Milan), scan for doshas (Manglik, Kaal Sarpa), and run a full
numerology profile — entirely on your machine, **with no API keys and no network
calls**.

This repo ships **two sibling skills**: `vedic-astrology/` (ephemeris-based) and
`numerology/` (pure arithmetic), plus a bundled offline **city geocoder**.

All planetary math is done with the [Swiss Ephemeris](https://www.astro.com/swisseph/)
in **sidereal (Vedic) mode**, using the **Lahiri ayanamsa** by default.

> ⚠️ **For cultural, educational, and entertainment use only.** Vedic astrology
> is not a scientifically validated predictive method. Do not use it for medical,
> financial, legal, or other consequential decisions.

---

## ✨ Features

| Command | What it computes |
|---------|------------------|
| **Kundli** (`kundli.py`) | D1 Rashi chart — sidereal positions, signs, whole-sign houses, Lagna, nakshatra + pada, **D9 navamsa**, dignity, **vargottama** & **combustion** flags, retrogrades |
| **Vimshottari Dasha** (`dasha.py`) | 120-year Mahadasha / Antardasha / **Pratyantardasha** timeline from the Moon's nakshatra |
| **Dasha Effects** (`dasha_predict.py`) | **Chart-aware interpretation** of the *currently running* period — effects on daily life, mind, career, money, marriage, health, family, enemies, education & spirituality. Personalised by house placement, lordship, dignity, combustion & the Maha↔Antar relationship |
| **Panchang** (`panchang.py`) | The five limbs (Tithi, Nakshatra, Yoga, Karana, **sunrise-based Vara**) plus **sunrise/sunset, Rahu Kaal, Yamaganda, Gulika, Abhijit muhurta** |
| **Yogas** (`yogas.py`) | **Aspect-aware** detection (Vedic drishti, not just conjunction): Gajakesari, Budhaditya, Chandra-Mangala, the five Pancha Mahapurusha, Raja yoga |
| **Strength** (`strength.py`) | **Ashtakavarga** (BAV + SAV, verified to 337) and **Shadbala** (partial — components honestly labelled) |
| **Matching** (`matching.py`) | **Guna Milan** (36-point Ashtakoot), **Manglik** (Mangal Dosha), **Kaal Sarpa Dosha** |
| **Geocoder** (`geocode.py`) | Offline city → latitude / longitude / IANA timezone (bundled GeoNames dataset) |
| **Numerology** (`numerology/`) | Moolank, Bhagyank, Naamank (Chaldean + Pythagorean), Lo Shu grid, compatibility, personal year, name-correction hints |

Configurable **ayanamsa** (Lahiri / Raman / KP / Yukteshwar / Fagan-Bradley),
**house system** (Whole Sign / Placidus / Equal), **node** (mean / true), and
**topocentric** positions by default (geocentric optional).

---

## 📦 Installation

### 1. Install as a Claude Code skill

Copy the `vedic-astrology/` folder into your Claude Code skills directory:

```bash
git clone https://github.com/<your-username>/vedic-astrology-skill.git
cp -r vedic-astrology-skill/vedic-astrology ~/.claude/skills/
```

(Or, for a single project, drop it in `.claude/skills/` inside that project.)

### 2. Install the Python dependencies

```bash
cd ~/.claude/skills/vedic-astrology
pip install -r requirements.txt        # pyswisseph + pytz
```

That's it. The skill activates automatically when you ask Claude about a kundli,
horoscope, dasha, panchang, etc.

### Use the scripts directly (no Claude needed)

```bash
cd vedic-astrology/scripts

python3 kundli.py   --date 1990-08-15 --time 14:30:00 --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata
python3 dasha.py    --date 1990-08-15 --time 14:30:00 --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --levels 2
python3 dasha_predict.py --date 1990-08-15 --time 14:30:00 --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata --on 2026-06-04
python3 panchang.py --date 2026-06-04                  --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata
python3 yogas.py    --date 1990-08-15 --time 14:30:00 --lat 28.6139 --lon 77.2090 --tz Asia/Kolkata

# add --json to any command for machine-readable output
```

---

## 🗣️ Talking to Claude

Once installed, just ask naturally:

> "Cast my kundli — born 15 Aug 1990, 2:30 PM, in New Delhi."
>
> "What's my current Vimshottari dasha?"
>
> "I'm in Mercury–Venus dasha — how will it affect my career, money, and marriage?"
>
> "Give me today's panchang for Mumbai."
>
> "Which yogas are in this chart?"

Claude will ask for any missing birth details (it needs **date, exact local time,
latitude, longitude, and IANA timezone**) and then run the right script.

---

## 📥 Inputs explained

| Input | Format | Example | Notes |
|-------|--------|---------|-------|
| Date | `YYYY-MM-DD` | `1990-08-15` | Local birth date |
| Time | `HH:MM[:SS]` (24h) | `14:30:00` | **Local clock time at the birthplace.** The ascendant moves ~1° every 4 minutes, so accuracy matters. |
| Latitude | decimal degrees | `28.6139` | North positive |
| Longitude | decimal degrees | `77.2090` | **East positive, West negative** |
| Timezone | IANA name | `Asia/Kolkata` | Not a numeric offset like `+5:30` |

**Unknown birth time?** The Moon sign, dasha, and houses become unreliable. Use a
noon default only for sign-level information, and treat the Lagna/houses as invalid.

---

## 🧮 How it works

```
vedic-astrology-skill/         # git repo (push this)
├── README.md  LICENSE  NOTICE  .gitignore
├── examples/sample-output.md
├── tests/test_cli.py           # golden-value regression suite
├── .github/workflows/ci.yml    # CI: pytest on py3.10–3.12
├── vedic-astrology/            # SKILL 1 — copy into ~/.claude/skills/
│   ├── SKILL.md
│   ├── requirements.txt        # pyswisseph, pytz
│   ├── data/cities.csv         # bundled GeoNames geocoder dataset
│   ├── scripts/
│   │   ├── core.py             # the ONLY place Swiss Ephemeris is configured
│   │   ├── kundli.py  dasha.py  dasha_predict.py  panchang.py  yogas.py
│   │   ├── strength.py         # Ashtakavarga + Shadbala
│   │   ├── matching.py         # Guna Milan + doshas
│   │   └── geocode.py          # offline city lookup
│   └── references/             # nakshatras, yogas, interpretation
└── numerology/                 # SKILL 2 — stdlib only, no ephemeris
    ├── SKILL.md
    ├── scripts/numerology.py
    └── references/numbers.md
```

## ✅ Tests

```bash
pip install pytest
pytest -q          # 11 golden-value checks (SAV=337, BAV totals, dasha closure,
                   # sign placements, Guna Milan bounds, weekday, geocoder…)
```

CI runs the suite on Python 3.10–3.12 on every push and PR.

- **`core.py` owns the engine.** Sidereal mode, ayanamsa, planet IDs, nakshatra
  and dasha constants, and local→UT time conversion all live in one file. It uses
  the built-in **Moshier ephemeris**, so no large `.se1` data files are needed.
- Longitudes are **sidereal**. Tithi uses the Moon−Sun difference (ayanamsa-independent);
  nakshatra and yoga use sidereal longitudes (ayanamsa-dependent).
- **Ketu** = Rahu + 180°; **Rahu** uses the mean lunar node.

### Accuracy & scope notes

- Yoga detection is a **curated subset**, not exhaustive — see `references/yogas.md`.
- Panchang elements change through the day; the tool reports values at the given
  clock time. Vara (weekday) uses the civil date (Vedic days run sunrise-to-sunrise).
- Divisional charts beyond D1 (e.g. D9 Navamsa), ashtakavarga, and transit/gochar
  analysis are **not** in v1.

---

## 📜 License

Licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** — see
[`LICENSE`](LICENSE).

**Why AGPL and not MIT?** This skill depends on the Swiss Ephemeris, which is
dual-licensed under AGPL-3.0 *or* a paid commercial license. To stay
license-compatible, this project is AGPL-3.0. If you want to use it in a
closed-source or commercial product without AGPL obligations, obtain a
[Swiss Ephemeris Professional License](https://www.astro.com/swisseph/swephinfo_e.htm)
from Astrodienst AG. See [`NOTICE`](NOTICE) for full attribution.

*This licensing summary is provided in good faith and is not legal advice.*

---

## 🙏 Acknowledgements

- [Swiss Ephemeris](https://www.astro.com/swisseph/) by Astrodienst AG
- [pyswisseph](https://github.com/astrorigin/pyswisseph) Python binding
- The Lahiri ayanamsa follows the Indian government's Rashtriya Panchang standard.

## 🤝 Contributing

Issues and PRs welcome — especially additional yogas, divisional charts, and
sunrise-accurate panchang. By contributing you agree your contributions are
licensed under AGPL-3.0.
