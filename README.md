# Sound Bites

368 places to eat within one mile of Harbor Steps (1st & University), Seattle. Pike Place Market, the 1st Ave corridor, downtown core, Belltown, Denny Triangle, Pioneer Square, Chinatown-International District, and the waterfront. Live open/closed status, walk times, what to order, a map, and a share button. Ratings and hours refresh themselves on the 1st and 15th of each month.

Live site: https://michaelbegley.github.io/sound-bites/

## How it works

- `index.html` is the whole app. It ships with a built-in copy of the data so it works even if the fetch fails.
- `data/places.json` holds the current rating, review count, hours, and open/closed status for each place. The app fetches this file on load and overrides the built-in numbers.
- `scripts/update.py` pulls fresh numbers from Google Places and rewrites `data/places.json`.
- `.github/workflows/update.yml` runs that script on the 1st and 15th and commits the result. GitHub Pages redeploys automatically.

## One-time setup (about 15 minutes)

### 1. Put it on GitHub Pages
1. Create a new repo called `sound-bites` (public).
2. Upload everything in this folder, keeping the folder structure (`data/`, `scripts/`, `.github/workflows/`).
3. Settings → Pages → Source: **Deploy from a branch** → Branch: `main`, folder `/ (root)` → Save.
4. In a minute the site is at https://michaelbegley.github.io/sound-bites/

### 2. Get a Google Places API key
1. Go to https://console.cloud.google.com and create a project (any name).
2. Enable billing on the project. A card is required, but this stays within Google's free monthly threshold. See Cost below.
3. APIs & Services → Library → search **Places API (New)** → Enable.
4. APIs & Services → Credentials → Create credentials → API key. Copy it.
5. Click the key to edit it. Under **API restrictions** choose **Restrict key** and tick only **Places API (New)**. Save. This means the key can't be used for anything else if it leaks.

### 3. Give the key to GitHub
1. In the repo: Settings → Secrets and variables → Actions → **New repository secret**.
2. Name: `GOOGLE_PLACES_KEY`. Value: paste the key. Save.

### 4. Turn on the weekly job
1. Actions tab → if it asks, click **I understand my workflows, go ahead and enable them**.
2. Open **Refresh ratings and hours** → **Run workflow** → Run. That's a manual first run to prove it works.
3. Check the log. You should see lines like `~ Lands of Origin: 5.0/673 -> 5.0/681` and `done: N changed, 0 errors`.
4. From then on it runs itself on the 1st and 15th. The date in the app header updates to match.

## Cost

Rating and review count are "Enterprise" fields in Google's Places API (New). Google's free monthly threshold for Enterprise SKUs is 1,000 calls. At 368 places, the job is already set to run twice a month (the 1st and 15th), which is about 736 calls and stays free. A weekly run would be roughly 1,600 calls, about 600 over the threshold and a few dollars a month. The tail of the list barely moves week to week, so fortnightly is plenty. Daily would be about 10,500 calls a month and is not worth it. Check Google's pricing page before changing the schedule.

## Changing things

- **Add a place:** find its Place ID (https://developers.google.com/maps/documentation/places/web-service/place-id has a finder tool), add an entry to the `P` array in `index.html` and to `data/places.json`. The next Monday run fills in the numbers.
- **Change the schedule:** edit the `cron` line in `.github/workflows/update.yml`. Cron is in UTC.
- **Change the weighting:** `PRIOR_W`, `PRIOR_M`, and `FLOOR` near the top of the script in `index.html`.
- **Move the home point:** `HOME` in `index.html`.

## What the update does not touch

The "what to get" tips, cuisine tags, price levels, happy hour times, line warnings, and the glossary are hand-written and live in `index.html`. They stay put unless you edit them.
