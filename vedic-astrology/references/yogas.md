# Yogas — Definitions and Caveats

A **yoga** is a specific planetary combination said to produce a defined effect.
Classical texts (Brihat Parashara Hora Shastra, Phaladeepika, Saravali, etc.)
describe hundreds, often with overlapping or conflicting rules. This skill detects
a **small, unambiguous subset** computable from the D1 (Rashi) chart. Absence of a
yoga here does **not** mean none exist — it means none from this set were found.

## Detected in v1

### Gajakesari Yoga
- **Rule used:** Jupiter occupies a kendra (1st, 4th, 7th, or 10th house) *counted
  from the Moon*.
- **Tradition:** intelligence, good reputation, respect.
- **Caveat:** stricter versions require Jupiter to be strong/unafflicted.

### Budhaditya Yoga
- **Rule used:** Sun and Mercury in the same sign/house (conjunction).
- **Tradition:** intellect, communication, analytical skill.
- **Caveat:** some texts discount it if Mercury is combust (too close to the Sun).
  The skill does not test combustion in v1.

### Chandra-Mangala Yoga
- **Rule used:** Moon and Mars in the same sign/house.
- **Tradition:** financial drive, enterprise.

### Pancha Mahapurusha Yogas
Five "great person" yogas, one per non-luminary classical planet:

| Yoga | Planet | Rule used |
|------|--------|-----------|
| Ruchaka | Mars | Mars exalted or in own sign **and** in a kendra |
| Bhadra | Mercury | Mercury exalted or own sign **and** in a kendra |
| Hamsa | Jupiter | Jupiter exalted or own sign **and** in a kendra |
| Malavya | Venus | Venus exalted or own sign **and** in a kendra |
| Sasa | Saturn | Saturn exalted or own sign **and** in a kendra |

- **Tradition:** pronounced strength of that planet's significations.

### Raja Yoga (simplified)
- **Rule used:** a **kendra lord** (lord of house 1/4/7/10) is conjunct a **trikona
  lord** (lord of house 1/5/9), counted from the Lagna.
- **Tradition:** status, authority, success.
- **Caveat — important:** real Raja-yoga analysis also counts mutual aspects, sign
  exchange (parivartana), and placement. v1 detects **conjunction only**, so it
  will miss aspect-based and exchange-based Raja yogas and may over-simplify.

## Dignity reference (used by Mahapurusha detection)

| Planet | Exalted in | Own sign(s) | Debilitated in |
|--------|-----------|-------------|----------------|
| Sun | Aries | Leo | Libra |
| Moon | Taurus | Cancer | Scorpio |
| Mars | Capricorn | Aries, Scorpio | Cancer |
| Mercury | Virgo | Gemini, Virgo | Pisces |
| Jupiter | Cancer | Sagittarius, Pisces | Capricorn |
| Venus | Pisces | Taurus, Libra | Virgo |
| Saturn | Libra | Capricorn, Aquarius | Aries |

## Not yet implemented (candidates for v2)

Neecha Bhanga Raja Yoga (debilitation cancellation), Vipreet Raja yogas,
Kemadruma, Kala Sarpa, Dhana yogas via 2/11 lords, aspect- and exchange-based
Raja yogas, and Mahapurusha combustion/aspect refinements.

> All effects listed are traditional cultural associations, not predictions of
> real-life outcomes.
