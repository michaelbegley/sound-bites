#!/usr/bin/env python3
"""
Refresh data/places.json from Google Places API (New).

Fetches rating, review count, weekly hours, and business status for every place id.
Keeps the previous value for any place that errors, so one bad call never blanks a row.

Cost: rating + userRatingCount are Enterprise-tier fields. Google's free monthly
threshold for Enterprise SKUs is 1,000 calls (as of 2025-2026 pricing). 146 places
x ~4.4 weekly runs = ~640 calls/month, so this stays free on its own.

Env: GOOGLE_PLACES_KEY (set as a GitHub Actions secret).
"""
import json, os, sys, time, urllib.request, urllib.error
from collections import Counter
from datetime import date

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "places.json")
KEY = os.environ.get("GOOGLE_PLACES_KEY")
FIELDS = "rating,userRatingCount,regularOpeningHours,businessStatus"
DK = ["u", "m", "t", "w", "r", "f", "s"]  # Google day 0=Sunday ... 6=Saturday


def fetch(place_id):
    req = urllib.request.Request(
        f"https://places.googleapis.com/v1/places/{place_id}",
        headers={"X-Goog-Api-Key": KEY, "X-Goog-FieldMask": FIELDS},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def hours_to_compact(roh):
    """Convert Google regularOpeningHours.periods to the app's compact format.
    string  -> same every day, e.g. "11-22"
    object  -> {"d": default, "m": override, ...}; "x" = closed; times in 24h decimal, >24 = past midnight
    """
    if not roh or "periods" not in roh:
        return None
    per_day = {k: [] for k in DK}
    for p in roh["periods"]:
        o, c = p.get("open"), p.get("close")
        if not o:
            continue
        if c is None:  # open 24 hours
            per_day[DK[o["day"]]].append("0-24")
            continue
        s = o["hour"] + o.get("minute", 0) / 60
        e = c["hour"] + c.get("minute", 0) / 60
        if c["day"] != o["day"]:
            e += 24
        per_day[DK[o["day"]]].append(f"{fmt(s)}-{fmt(e)}")
    days = {k: (",".join(v) if v else "x") for k, v in per_day.items()}
    vals = list(days.values())
    if len(set(vals)) == 1:
        return vals[0]
    default = Counter(vals).most_common(1)[0][0]
    out = {"d": default}
    out.update({k: v for k, v in days.items() if v != default})
    return out


def fmt(x):
    return str(int(x)) if x == int(x) else f"{x:.2f}".rstrip("0")


def main():
    if not KEY:
        sys.exit("GOOGLE_PLACES_KEY not set")
    with open(DATA, encoding="utf-8") as f:
        doc = json.load(f)
    changed = errors = 0
    for e in doc["places"]:
        try:
            g = fetch(e["id"])
        except urllib.error.HTTPError as ex:
            errors += 1
            print(f"  ! {e['name']}: HTTP {ex.code}", file=sys.stderr)
            continue
        except Exception as ex:
            errors += 1
            print(f"  ! {e['name']}: {ex}", file=sys.stderr)
            continue
        new = {
            "rating": g.get("rating", e.get("rating")),
            "count": g.get("userRatingCount", e.get("count")),
            "hours": hours_to_compact(g.get("regularOpeningHours")) or e.get("hours"),
            "status": g.get("businessStatus", e.get("status", "OPERATIONAL")),
        }
        if any(e.get(k) != v for k, v in new.items()):
            changed += 1
            print(f"  ~ {e['name']}: {e.get('rating')}/{e.get('count')} -> {new['rating']}/{new['count']}")
        e.update(new)
        time.sleep(0.15)  # be polite to the rate limit
    doc["updated"] = date.today().isoformat()
    doc["source"] = "Google Places API (New)"
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"done: {changed} changed, {errors} errors, {len(doc['places'])} places")
    if errors > len(doc["places"]) // 2:
        sys.exit("more than half the calls failed; check the API key and quota")


if __name__ == "__main__":
    main()
