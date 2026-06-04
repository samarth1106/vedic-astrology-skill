# Divisional charts (Vargas)

`varga.py` computes the **Shodasavarga** — the 16 classical divisions — for all
nine grahas and the Lagna, plus a cross-varga strength view.

## What each division is read for

| Dn | Name | Life area |
|----|------|-----------|
| D1 | Rashi | the whole life, body, self |
| D2 | Hora | wealth & resources (only Cancer/Leo possible) |
| D3 | Drekkana | siblings, courage, longevity |
| D4 | Chaturthamsa | fortune, property, home |
| D7 | Saptamsha | children & progeny |
| D9 | Navamsa | spouse, marriage, dharma, inner strength |
| D10 | Dasamsha | **career, status, karma** |
| D12 | Dwadasamsa | parents & lineage |
| D16 | Shodasamsa | vehicles, comforts, happiness |
| D20 | Vimsamsa | spiritual practice & worship |
| D24 | Chaturvimsamsa | education & learning |
| D27 | Bhamsa | strengths & weaknesses |
| D30 | Trimsamsa | misfortunes, troubles, health |
| D40 | Khavedamsa | maternal-line results |
| D45 | Akshavedamsa | paternal-line, character |
| D60 | Shashtiamsa | past-life karma, finest layer |

## How to read them

- **Confirm the D1 promise in the relevant varga.** A strong 10th-house promise
  in D1 only delivers if the same planets/lords are also strong in **D10**.
  Marriage is judged in **D9**, children in **D7**, career in **D10**.
- **Vargottama** (a planet in the same sign in D1 and D9) is a notable strength —
  the `kundli.py` output already flags it.
- **Cross-varga strength.** The script reports, per planet: how many of the 16
  vargas it is own/exalted in (more = steady), how many it is debilitated in, a
  transparent **VargaBala %**, and a **Shadvarga score /20**.

## Honesty note on the strength numbers

- **VargaBala %** is the *skill's own transparent scheme*, NOT the classical
  Vimshopaka Bala. It scores each varga by the planet's dignity there
  (own/exalted 1.0, friend 0.66, neutral 0.5, enemy 0.33, debilitated 0.0) and
  averages over all 16. Use it as a relative comparison, not an absolute.
- **Shadvarga /20** uses the one well-established weighting (D1=6, D2=2, D3=4,
  D9=5, D12=2, D30=1) applied to the same dignity score. It approximates — does
  not reproduce — a full classical Shadvarga Vimshopaka.
- The **own/exalted and debilitated counts** are exact and unambiguous; lead with
  those when judging a planet's varga strength.

## Engine

All amsa mappings follow the standard Parashari rules and live in
`core.varga_sign(lon, D)`. D9 is verified to equal `core.navamsa_sign` across the
whole zodiac. For cultural/educational use only.
