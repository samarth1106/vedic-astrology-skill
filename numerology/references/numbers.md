# Numerology Reference — Numbers 1–9 and Master Numbers

> **Cultural tradition, not prediction.** Everything below is traditional
> symbolism drawn from Indian (Cheiro-style) and Western numerology. None of it
> is scientifically validated; treat it as cultural/educational/entertainment
> content only.

## How the core numbers are derived

- **Moolank (Psychic / Birth number):** the day of the month of birth, reduced to
  a single digit (e.g. 15 → 1+5 = 6; 29 → 2+9 = 11 → 2).
- **Bhagyank (Destiny / Life Path):** the sum of *all* digits of the full date of
  birth (DD + MM + YYYY), reduced (e.g. 1990-08-15 → 1+9+9+0+0+8+1+5 = 33 → 6).
- **Naamank (Name number):** the sum of the letter values of the full name,
  reported as a compound number then reduced.

## Ruling planets (Cheiro / Indian)

| Number | Planet  |
|--------|---------|
| 1 | Sun |
| 2 | Moon |
| 3 | Jupiter |
| 4 | Rahu |
| 5 | Mercury |
| 6 | Venus |
| 7 | Ketu |
| 8 | Saturn |
| 9 | Mars |

## Number profiles

### 1 — Sun
- **Keywords / personality:** leadership, individuality, drive, originality.
- **Strengths:** initiative, confidence, ambition, pioneering spirit.
- **Challenges:** ego, stubbornness, domineering, impatience.
- **Friendly numbers:** 1, 2, 3, 9. **Enemy numbers:** 8 (4, 7 mild).
- **Lucky:** Sunday & Monday · gold/orange · Ruby.

### 2 — Moon
- **Keywords / personality:** sensitivity, diplomacy, intuition, cooperation.
- **Strengths:** empathy, partnership, adaptability, imagination.
- **Challenges:** moodiness, indecision, over-dependence, hypersensitivity.
- **Friendly numbers:** 1, 2, 5, 7. **Enemy numbers:** 8, 9 (mild).
- **Lucky:** Monday · white/cream/silver · Pearl.

### 3 — Jupiter
- **Keywords / personality:** creativity, expression, optimism, wisdom.
- **Strengths:** communication, generosity, ambition, teaching.
- **Challenges:** scattered focus, over-talkative, extravagance, pride.
- **Friendly numbers:** 1, 2, 3, 9. **Enemy numbers:** 6.
- **Lucky:** Thursday · yellow · Yellow Sapphire.

### 4 — Rahu
- **Keywords / personality:** structure, practicality, unconventional thinking.
- **Strengths:** discipline, endurance, system-building, reliability.
- **Challenges:** rigidity, rebellion, restlessness, sudden upheavals.
- **Friendly numbers:** 1, 5, 6, 7. **Enemy numbers:** 2, 9.
- **Lucky:** varies · grey/khaki/electric blue · Hessonite (Gomed).

### 5 — Mercury
- **Keywords / personality:** versatility, freedom, communication, curiosity.
- **Strengths:** adaptability, wit, networking, quick learning.
- **Challenges:** restlessness, inconsistency, nervous energy, over-indulgence.
- **Friendly numbers:** friendly to all (notably 1, 5, 6). **Enemy numbers:** few/none strong.
- **Lucky:** Wednesday · green · Emerald.

### 6 — Venus
- **Keywords / personality:** harmony, love, responsibility, beauty.
- **Strengths:** nurturing, artistic, devoted, hospitable.
- **Challenges:** over-attachment, indulgence, jealousy, people-pleasing.
- **Friendly numbers:** 4, 5, 6, 8. **Enemy numbers:** 3.
- **Lucky:** Friday · white/pastels · Diamond / Opal.

### 7 — Ketu
- **Keywords / personality:** introspection, spirituality, analysis, mysticism.
- **Strengths:** depth, research, intuition, independence.
- **Challenges:** isolation, skepticism, detachment, secrecy.
- **Friendly numbers:** 1, 2, 4, 7. **Enemy numbers:** none strong.
- **Lucky:** varies · smoky/grey · Cat's Eye.

### 8 — Saturn
- **Keywords / personality:** ambition, discipline, authority, material mastery.
- **Strengths:** perseverance, organization, justice, resilience.
- **Challenges:** delays, hardship, coldness, workaholism.
- **Friendly numbers:** 5, 6, 8. **Enemy numbers:** 1, 2.
- **Lucky:** Saturday · black/dark blue · Blue Sapphire.

### 9 — Mars
- **Keywords / personality:** energy, courage, compassion, completion.
- **Strengths:** determination, leadership, generosity, fearlessness.
- **Challenges:** aggression, impatience, impulsiveness, conflict.
- **Friendly numbers:** 1, 3, 9. **Enemy numbers:** 4.
- **Lucky:** Tuesday · red · Red Coral.

## Number compatibility (planetary friendships)

A Naamank that is a **friend** of both the Moolank and the Bhagyank is considered
harmonious; an **enemy** to either is considered a point of friction; otherwise
**neutral**. The relation is symmetric: a pair counts as friend if either side
lists the other as a friend (and neither as an enemy), enemy if either side lists
the other as an enemy (and neither as a friend), and neutral on mixed signals.

## Lo Shu grid

The full date of birth (DDMMYYYY, ignoring zeros) is mapped onto the fixed 3×3
Lo Shu square:

```
4 9 2
3 5 7
8 1 6
```

A **line fully present** across the person's digits is an *Arrow of Strength*; a
**line fully absent** is an *Arrow of Weakness*.

| Line | Cells | Name |
|------|-------|------|
| Top row | 4,9,2 | Arrow of Intellect / Mental Plane |
| Middle row | 3,5,7 | Arrow of Emotional Balance |
| Bottom row | 8,1,6 | Arrow of Practicality / Action |
| Left column | 4,3,8 | Arrow of Planning / Thought |
| Middle column | 9,5,1 | Arrow of Will / Determination |
| Right column | 2,7,6 | Arrow of Activity |
| Diagonal | 4,5,6 | Arrow of Compassion (the Golden / Kindness) |
| Diagonal | 2,5,8 | Arrow of Spirituality / Emotional |

## Personal year

`personal_year = reduce( birth_month + birth_day + reduce(year) )`, giving a 1–9
theme (see the number profiles above for the corresponding keywords).

## Master numbers 11, 22, 33

In some traditions the numbers **11, 22, and 33** are *master numbers* and are
left unreduced when they appear as an intermediate or final sum (use the
`--keep-master` flag). They are seen as carrying heightened, more demanding
versions of their reduced root (11 → 2, 22 → 4, 33 → 6):

- **11** — intuition, inspiration, spiritual insight (intensified 2).
- **22** — the "master builder": large-scale, practical manifestation (intensified 4).
- **33** — the "master teacher": compassion, healing, selfless service (intensified 6).

Ruling-planet, lucky-attribute, and compatibility lookups always use the fully
reduced single digit, even when a master number is displayed.

> Reminder: all of the above is traditional symbolism for cultural and
> entertainment use. It is **not predictive** and should not inform consequential
> decisions.
