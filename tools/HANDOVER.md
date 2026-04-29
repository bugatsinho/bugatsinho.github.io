# Handover for `plugin.video.sporthdme` maintenance

> Paste this whole file (or its first half plus the “Resume prompt” block at the
> bottom) to the next LLM session and they should be able to pick up where we
> left off.

---

## TL;DR

The user is **bugatsinho**, maintainer of a Kodi repository at
`/Users/elianaalfaro/PycharmProjects/bugatsinho.github.io`. They want help keeping
**`plugin.video.sporthdme`** working, especially the resolvers, since the
upstream sites rotate domains and player implementations on a regular cadence.

In the previous sessions we:

1. **Set up a working maintenance toolchain** under `tools/` (all stdlib-only
   so it runs anywhere without `pip install`).
2. **Diagnosed the live state** of every part of the addon.
3. **Cracked the new obfuscation** used by `glisco.link` / `sansat.link` —
   we can extract the m3u8 URL purely in Python using `econfig.py`.
4. **Fixed the final resolver blocker**: The `fisherman.click` iframe sets a
   cookie (`hf1=1`) which *must* be passed to the final `.m3u8` request,
   otherwise the CDN returns 403 Forbidden. We modified `default.py` to use
   `requests.get` for the iframe, extract the cookies, and pass them to Kodi.
5. **Released 0.1.85.1** which is now live and working.
6. **Created a symlink** `kodi_addon_link` in the workspace pointing to the
   live Kodi addons folder (`~/Library/Application Support/Kodi/addons/plugin.video.sporthdme`)
   for rapid local development.
7. **Gradual modernization (started)**: `default.py` now has unified `log_debug`,
   `log_warning`, `log_error` helpers; bare `except:` replaced with `except Exception`
   where appropriate; top-level `try/except` around `router()` logs and shows
   `control.infoDialog` on unhandled errors.

The user runs **Kodi 18, 19, 20, 21**. Do NOT remove `six`/Python 2 compat —
Kodi 18 still ships Python 2.

---

## Current state of the repo

```
bugatsinho.github.io/
├── addons.xml                 # hand-maintained manifest (do NOT regenerate
│                              # from scratch -- surgically update only the
│                              # <addon id="..."> block being released)
├── addons.xml.md5             # md5(addons.xml). 32 chars, no newline.
├── _zips/<addon-id>/          # release artifacts; keep all old zips
│   ├── <addon-id>-<ver>.zip
│   ├── addon.xml              # latest copy of the addon's xml
│   ├── icon.png, fanart.jpg
├── plugin.video.sporthdme/    # the addon source (current ver 0.1.85.1)
│   ├── addon.xml
│   ├── default.py             # 707 lines, all logic (events + resolve2)
│   └── resources/modules/     # client.py, control.py, cache.py, jsunpack.py,
│                              # jsUnwiser.py, jsontools.py, econfig.py (NEW)
├── kodi_addon_link/           # NEW. Symlink to ~/Library/Application Support/Kodi/addons/plugin.video.sporthdme
├── tools/                     # NEW. Stdlib-only maintenance helpers.
│   ├── release.py             # version bump + zip + addons.xml + md5
│   ├── release.sh             # bash wrapper around release.py
│   ├── diagnose.py            # live HTTP probes + resolver pattern checks
│   ├── README.md              # short usage docs
│   └── HANDOVER.md            # this file
└── .github/workflows/release.yml   # CI release pipeline (tag-driven)
```

`addons.xml` includes `<addon id="plugin.video.sporthdme" ...>` at lines ~444-471.

---

## What we changed recently

### Code

* `plugin.video.sporthdme/default.py`:
  * `Live_url` updated to `https://super.league.st`
  * 24/7 Channels feature commented out (`fetch_and_store_channel_data()` call removed from `router`) because `one.sporthd.me` is dead.
  * Added a new branch in `resolve2()` for `//glisco` and `//sansat` that uses `requests.get` to fetch the iframe, extracts the `hf1=1` cookie, decodes the `_econfig` blob using the new `econfig.py` module, and passes the cookie + Origin + Referer to Kodi via `xbmc_curl_encode`.

* **New module** `plugin.video.sporthdme/resources/modules/econfig.py` —
  pure-stdlib decoder for `window._econfig` blobs.

### Tooling (all new)

* `tools/release.py` — argparse CLI. Does:
  1. bump `version="..."` in `<addon-id>/addon.xml`
  2. surgically update the same attribute inside the `<addon ...>` block of
     root `addons.xml` (regex on the opening tag; preserves the rest of the
     hand-maintained file 1:1)
  3. optionally rewrite the `<news>` block in both files
  4. zip the addon source into `_zips/<addon-id>/<addon-id>-<ver>.zip`
     (top-level dir = `<addon-id>/`, excludes `__pycache__`, `.DS_Store`,
     `.git`, `.idea`, `*.pyc`, `*.pyo`)
  5. copy `addon.xml` + `icon.png` + `fanart.jpg` into `_zips/<addon-id>/`
  6. regenerate `addons.xml.md5`
  7. print suggested git commands. **Does NOT commit.**
  Supports `--dry-run` and `--refresh-md5` standalone modes.

* `tools/release.sh` — thin bash wrapper.

* `.github/workflows/release.yml` — CI mirror of the same flow, triggered by
  pushing a tag like `plugin.video.sporthdme-0.1.85.1` or via workflow_dispatch.
  Commits the result to `master` and uploads the new zip as a GitHub Release
  asset.

* `tools/diagnose.py` — `events`, `channels`, `resolve <url>`, `all`
  subcommands. Default events URL: `https://super.league.st`. Saves bodies
  to `/tmp/sporthd_*.html` when parsing fails.

---

## Live findings worth remembering

* Channels source `https://one.sporthd.me/api/trpc/...` (the 24/7 channels
  `BASEURL + 'api/trpc/.../mutual.getAllChannels'`) is **dead** —
  `one.sporthd.me` no longer resolves. **The user chose to disable / hide the
  feature but keep the code** (option `comment_out`).

* Today only **two stream hosts** appear in events payload: `glisco.link`
  and `sansat.link`. The other 9 in the
  `resolved` array of `default.py` (`dabac, istorm, zvision, bedsport,
  coolrea, evfancy, s2watch, vuen, gopst`) do NOT appear today. Per the user
  these rotate, so do not delete them.

* `oldLinks` in the events JSON points at `nrdrse.link/ch.php?id=N` — same
  scheme, similar player. Not used today but worth keeping the legacy path.

* The match struct keys today are: `channel, channels, duration, important,
  league, matchDate, matchText, matchstr, slug, sport, startTimestamp,
  team1, team2, time`. Notably **missing**: `team1Img`, `livetvtimestr`.
  The current default.py `.get('team1Img', ICON)` is fine. The fallback path
  in `get_events()` that reads `match['livetvtimestr']` would crash if it
  ever ran, but it doesn't run today because `startTimestamp` exists.

---

## Recommended next steps (in order)

1. **Gradual Modernization (continue)**:
   - First slice done: logging helpers, `except Exception`, top-level error handler in `default.py`.
   - Next ideas (when you have time): same patterns in `resources/modules/*.py`; small
     helper for `requests.get` timeout + ensure_text responses; avoid duplicate resolver logic.
   - *Crucial*: test via `kodi_addon_link` before release.

2. **Monitor Resolvers**:
   Keep an eye on the other resolvers in the `resolved` list. When they become active again, they might need similar reverse-engineering.

---

## Resume prompt (paste this verbatim to a fresh LLM)

> I'm bugatsinho, maintainer of a Kodi repository at
> `/Users/elianaalfaro/PycharmProjects/bugatsinho.github.io`. I'm picking up
> a maintenance task on `plugin.video.sporthdme` that another agent
> was working on. Please **read `tools/HANDOVER.md`** in the repo first — it has
> the full state of where we are and what works. The critical resolver bug (403 Forbidden)
> is FIXED (it was a missing `hf1=1` cookie from the iframe). Version 0.1.85.1 is live.
> We also have a `kodi_addon_link` symlink for rapid local testing.
> Please continue with the "Gradual Modernization" step mentioned in the handover.
> Use Greek when chatting with me. Don't strip `six`/Python 2 support — Kodi 18 is still in scope.

---

_Written: 2026-04-29 by Claude Opus 4.7. Last verified live request:
`glisco.link` resolver working perfectly with cookie injection._
