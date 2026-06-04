---
name: numerology
description: Compute a numerology report offline from a birth date (and optional full name). Generates the Moolank (psychic/birth number), Bhagyank (destiny/life-path number), Naamank (name number in Chaldean and/or Pythagorean systems), ruling planets, number compatibility via planetary friendships, the Lo Shu grid with strength/weakness arrows, an optional personal-year theme, lucky attributes (gemstone/day/colors), and a name-correction hint. Pure Python standard library — no ephemeris, no network, no dependencies. Use when the user says numerology, ank jyotish, life path number, destiny number, moolank, bhagyank, naamank, name number, lo shu grid, lucky number, numerology report, personal year, Chaldean, Pythagorean, or name correction.
license: AGPL-3.0
---

# Numerology (Ank Jyotish)

Offline numerology calculator. All math runs locally in pure Python — **only the
standard library, no ephemeris, no API keys, no network**. This module inherits
the repository's **AGPL-3.0** license.

> **Disclaimer — state this to the user when presenting results.** This skill is
> for cultural, educational, and entertainment purposes only. It is **not
> predictive** and must not be used for medical, financial, legal, or other
> consequential decisions.

## Required & optional inputs

| Input | Format | Required | Notes |
|-------|--------|----------|-------|
| Date  | `YYYY-MM-DD` | **Yes** | Date of birth. Drives Moolank, Bhagyank, Lo Shu. |
| Name  | `"Full Name"` | No | Enables Naamank, compatibility, name-correction. |
| Year  | `YYYY` | No | Enables the personal-year theme. |

Only the date is required. Everything else degrades gracefully when omitted.

## The two name-number systems

- **Chaldean** — ancient system, values 1–8 only (no letter is assigned 9).
  Reports the *compound* number first, then reduces to a single digit.
- **Pythagorean** — modern A=1…I=9, J=1…R=9, S=1…Z=8 system.

Default `--system both` reports both. The first requested system is used for the
compatibility and name-correction logic.

## Routing — running the script

One script, `scripts/numerology.py`. It prints a clean text report by default and
accepts `--json` for machine-readable output.

```bash
cd scripts

# Full report (date + name + personal year, both systems)
python3 numerology.py --date 1990-08-15 --name "Albert Einstein" \
  --system both --year 2026

# Minimal (date only)
python3 numerology.py --date 1990-08-15

# Chaldean only, keep master numbers 11/22/33 unreduced where noted
python3 numerology.py --date 2000-02-29 --system chaldean --keep-master

# JSON output for further processing
python3 numerology.py --date 1990-08-15 --name "Albert Einstein" --json
```

### Flags

- `--date YYYY-MM-DD` — **required**, date of birth.
- `--name "Full Name"` — optional; enables name-based sections.
- `--system chaldean|pythagorean|both` — default `both`.
- `--year YYYY` — optional; adds the personal-year theme.
- `--keep-master` — keep 11/22/33 unreduced in Moolank/Bhagyank/Naamank where the
  reduction would otherwise pass through a master number. Ruling-planet lookups
  still use the fully reduced single digit.
- `--json` — emit JSON instead of the formatted text report.

## What the report contains

1. **Moolank** (psychic / birth number) — reduced day of birth, with ruling planet.
2. **Bhagyank** (destiny / life-path) — reduced sum of all DOB digits, shows the chain.
3. **Naamank** (name number) — compound + reduced, per requested system.
4. **Ruling planet** — Sun/Moon/Jupiter/Rahu/Mercury/Venus/Ketu/Saturn/Mars for 1–9.
5. **Compatibility** — whether the Naamank is friend/neutral/enemy to the Moolank
   and Bhagyank, using planetary friendships, with a recommendation.
6. **Lo Shu grid** — digit placement, counts, missing numbers, and detected
   arrows of strength (line fully present) and weakness (line fully absent).
7. **Personal year** (only with `--year`) — the 1–9 theme for that year.
8. **Lucky attributes** — gemstone, days, and colors for the Moolank's ruler.
9. **Name-correction hint** — if the name conflicts with a core number, the target
   single-digit Naamank values that are friends of *both* core numbers (principle
   only — the skill does not auto-generate spellings).

## Presenting results

1. Run the script; relay the text table directly or use `--json` and reformat.
2. **Always restate the disclaimer** — this is non-predictive, cultural content.
3. For per-number meanings (keywords, strengths, challenges, lucky attributes) and
   the master-number notes, load `references/numbers.md` on demand.
4. Be honest about scope: numerology is a traditional symbolic system, not a
   measurement of anything. Name correction gives target *numbers* and the
   underlying principle, not specific spellings.
