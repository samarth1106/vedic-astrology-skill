#!/usr/bin/env python3
"""verify.py — reproduce / cross-check a chart from another source.

When a chart (JSON/PDF) comes from other software and you want to confirm it
against this engine, the usual surprise is that EVERY planet matches except the
Moon. Most Indian software computes geocentric positions; this skill defaults to
topocentric, and lunar parallax can shift the Moon up to ~1deg. This tool prints
each planet's sidereal longitude under BOTH conventions, highlights the Moon
delta, and — if you pass the external Moon longitude via --expect-moon — tells you
which convention the source used. It also reminds you that some sources encode
degrees as DD<degsym>MM, not decimal degrees.

For cultural/educational use only.
"""
import argparse
import json
import re

import core


def _parse_time(t):
    parts = t.split(":")
    hh = int(parts[0])
    mm = int(parts[1]) if len(parts) > 1 else 0
    ss = int(parts[2]) if len(parts) > 2 else 0
    return hh, mm, ss


def _positions(args, topocentric):
    core.init_engine(args.ayanamsa, node=args.node, topocentric=topocentric,
                     lat=args.lat, lon=args.lon, ephemeris=args.ephemeris)
    y, m, d = (int(x) for x in args.date.split("-"))
    hh, mm, ss = _parse_time(args.time)
    jd = core.to_julian_ut(y, m, d, hh, mm, ss, args.tz)
    return {n: p["longitude"] for n, p in core.all_planet_positions(jd).items()}


def _ang(a, b):
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def parse_longitude(text: str) -> float:
    """Parse an external Moon longitude given in any of the usual forms.

    Accepts decimal degrees ("198.2081"), or a sign name with degrees inside
    that sign ("Libra 18 12", "Libra 18d12m", "Libra 18\u00b012'30\"").
    Sign names are matched case-insensitively on a unique prefix, so "lib" and
    "Libra" both work. Raises ValueError with an instructive message rather
    than letting float() fail opaquely.
    """
    t = " ".join(str(text).split())
    try:
        return float(t) % 360.0                      # plain decimal degrees
    except ValueError:
        pass

    parts = re.split(r"[\s\u00b0'\"dms]+", t.strip())
    parts = [x for x in parts if x]
    if not parts:
        raise ValueError("--expect-moon is empty")

    word = parts[0].lower()
    matches = [i for i, nm in enumerate(core.SIGNS) if nm.lower().startswith(word)]
    if len(matches) != 1:
        raise ValueError(
            f"could not read --expect-moon {text!r}. Give decimal degrees "
            f"(e.g. 198.2081) or a sign with degrees inside it "
            f"(e.g. \"Libra 18 12\"). Signs: {', '.join(core.SIGNS)}")

    nums = []
    for x in parts[1:]:
        try:
            nums.append(float(x))
        except ValueError:
            raise ValueError(
                f"could not read {x!r} in --expect-moon {text!r} as a number. "
                f"Expected \"<Sign> <deg> [min] [sec]\".")
    if not nums:
        raise ValueError(
            f"--expect-moon {text!r} names the sign but gives no degrees. "
            f"A sign alone is 30\u00b0 wide \u2014 too coarse to compare. "
            f"Use e.g. \"{core.SIGNS[matches[0]]} 18 12\".")
    nums += [0.0, 0.0]
    deg, minute, sec = nums[0], nums[1], nums[2]
    if not 0 <= deg < 30:
        raise ValueError(f"degrees within a sign must be 0\u201330, got {deg}")
    return (matches[0] * 30.0 + deg + minute / 60.0 + sec / 3600.0) % 360.0


def compute(args):
    topo = _positions(args, True)
    geo = _positions(args, False)
    rows = []
    for name in core.PLANET_ORDER:
        rows.append({
            "planet": name,
            "topocentric": round(topo[name], 4),
            "geocentric": round(geo[name], 4),
            "delta_arcmin": round(_ang(topo[name], geo[name]) * 60.0, 2),
        })
    out = {
        "input": {"date": args.date, "time": args.time, "lat": args.lat, "lon": args.lon,
                  "timezone": args.tz, "ayanamsa": args.ayanamsa},
        "positions": rows,
        "note": "Only the Moon should differ materially (lunar parallax). DD.MM in a "
                "source may mean DDdeg MM' (e.g. 14.57 = 14deg57'), not decimal degrees.",
    }
    if args.expect_moon is not None:
        em = parse_longitude(args.expect_moon)
        dt = _ang(em, topo["Moon"]) * 60.0
        dg = _ang(em, geo["Moon"]) * 60.0
        out["moon_match"] = {
            "expected_moon": em,
            "delta_to_topocentric_arcmin": round(dt, 2),
            "delta_to_geocentric_arcmin": round(dg, 2),
            "source_appears": ("topocentric" if dt < dg else "geocentric"),
        }
    return out


def render_text(r):
    o = []
    A = o.append
    A("=" * 62)
    A("  VERIFY — topocentric vs geocentric cross-check")
    A("=" * 62)
    A("  Planet    Topocentric   Geocentric    delta (arcmin)")
    A("  " + "-" * 52)
    for p in r["positions"]:
        flag = "  <-- parallax" if p["delta_arcmin"] >= 5 else ""
        A(f"  {p['planet']:<8}  {p['topocentric']:>9.4f}   {p['geocentric']:>9.4f}"
          f"   {p['delta_arcmin']:>8.2f}{flag}")
    A("  " + "-" * 52)
    if "moon_match" in r:
        mm = r["moon_match"]
        A(f"  Expected Moon {mm['expected_moon']:.4f}  ->  source appears "
          f"{mm['source_appears'].upper()} "
          f"(topo {mm['delta_to_topocentric_arcmin']}' vs geo {mm['delta_to_geocentric_arcmin']}')")
    A("  " + r["note"])
    A("=" * 62)
    A("  For cultural/educational use only.")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(description="Cross-check a chart: topocentric vs geocentric.")
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--expect-moon", default=None, dest="expect_moon",
                    help="external Moon sidereal longitude to cross-check: decimal degrees (198.2081) or sign+degrees (\"Libra 18 12\")")
    ap.add_argument("--ayanamsa", default=core.DEFAULT_AYANAMSA)
    ap.add_argument("--node", default="mean", choices=["mean", "true"])
    ap.add_argument("--ephemeris", default="moshier", choices=["moshier", "swiss"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = compute(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))


if __name__ == "__main__":
    main()
