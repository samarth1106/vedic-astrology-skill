# 🪔 Vedic Astrology — a Claude Code Skill (Jyotish)

An offline **Vedic / Hindu astrology** computation skill for
[Claude Code](https://claude.com/claude-code). It casts a birth chart, computes
dasha periods, generates the daily panchang, and detects classical yogas —
entirely on your machine, **with no API keys and no network calls**.

All planetary math is done with the [Swiss Ephemeris](https://www.astro.com/swisseph/)
in **sidereal (Vedic) mode**, using the **Lahiri ayanamsa** by default.

> ⚠️ **For cultural, educational, and entertainment use only.** Vedic astrology
> is not a scientifically validated predictive method. Do not use it for medical,
> financial, legal, or other consequential decisions.

---

## ✨ Features

| Command | What it computes |
|---------|------------------|
| **Kundli** (`kundli.py`) | D1 Rashi birth chart — planetary sidereal positions, signs, whole-sign houses, the Lagna (ascendant), nakshatra + pada per planet, dignities, and retrograde flags |
| **Vimshottari Dasha** (`dasha.py`) | The 120-year Mahadasha / Antardasha timeline, computed from the Moon's nakshatra at birth |
| **Panchang** (`panchang.py`) | The five limbs for any date + place — Tithi, Nakshatra, Yoga, Karana, Vara |
| **Yogas** (`yogas.py`) | Detects common classical yogas (Gajakesari, Budhaditya, Chandra-Mangala, the five Pancha Mahapurusha, and a simplified Raja yoga) with plain-language notes |

Configurable **ayanamsa** (Lahiri / Raman / KP / Yukteshwar / Fagan-Bradley) and
**house system** (Whole Sign / Placidus / Equal).

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
vedic-astrology/
├── SKILL.md              # Claude's directive + routing layer
├── requirements.txt
├── scripts/
│   ├── core.py           # the ONLY place Swiss Ephemeris is configured
│   ├── kundli.py         # birth chart
│   ├── dasha.py          # vimshottari dasha
│   ├── panchang.py       # daily almanac
│   └── yogas.py          # yoga detection + interpretation
└── references/
    ├── nakshatras.md     # 27 nakshatras, lords, padas
    ├── yogas.md          # yoga rules + caveats
    └── interpretation.md # planets, houses, signs (cultural meanings)
```

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
