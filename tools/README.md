# Maintenance tools

Scripts that help update and release the addons in this repository.
All scripts use only the Python 3 standard library (no `pip install` needed).

## release.py

Bumps version, builds zip, updates root `addons.xml`, refreshes
`addons.xml.md5`, copies assets to `_zips/<addon-id>/`. Works for any addon
in the repo.

```bash
# Dry run first (recommended)
python3 tools/release.py --addon plugin.video.sporthdme --version 0.1.85 --dry-run

# Real release
python3 tools/release.py --addon plugin.video.sporthdme --version 0.1.85

# With news entry
python3 tools/release.py --addon plugin.video.sporthdme --version 0.1.85 \
    --news "- fix Live_url to super.league.st\n- update s2watch resolver"

# Just refresh the md5 file (after a manual edit of addons.xml)
python3 tools/release.py --refresh-md5
```

The script does **not** commit. It prints suggested git commands at the end.

### Bash wrapper

```bash
./tools/release.sh plugin.video.sporthdme 0.1.85
./tools/release.sh plugin.video.sporthdme 0.1.85 "- changelog line 1\n- line 2"
./tools/release.sh plugin.video.sporthdme 0.1.85 --dry-run
```

## diagnose.py

Live HTTP probes against the upstream sites used by `plugin.video.sporthdme`.
Reports which scraping/resolver patterns still match. Use it before and after
fixing things.

```bash
# Hit super.league.st/events and check both event-extraction regexes
python3 tools/diagnose.py events

# Hit one.sporthd.me tRPC endpoint for the 24/7 channels list
python3 tools/diagnose.py channels

# Probe an individual stream URL and see which player signature matches
python3 tools/diagnose.py resolve "https://example.host/embed/stream-1"

# Both events + channels in one run
python3 tools/diagnose.py all

# Override defaults
python3 tools/diagnose.py events --live-url https://super.league.st
python3 tools/diagnose.py channels --base-url https://one.sporthd.me/
```

When the events page can't be parsed, the body is dumped to
`/tmp/sporthd_events_body.html` so you can inspect what changed.

## CI release (GitHub Actions)

`.github/workflows/release.yml` runs the same `release.py` flow in CI. Two
trigger options:

1. **Push a tag** like `plugin.video.sporthdme-0.1.85`:

   ```bash
   git tag plugin.video.sporthdme-0.1.85
   git push origin plugin.video.sporthdme-0.1.85
   ```

   The workflow parses the tag, runs the release pipeline, commits the
   updated files back to `master`, and uploads the new zip as a
   GitHub Release asset.

2. **Manual dispatch** from the Actions tab: pick the addon id, version,
   and optional news text.

For a strictly-local workflow (e.g. you don't want CI to push commits),
just keep using `tools/release.py` and commit/push yourself.

## Typical maintenance loop for `plugin.video.sporthdme`

1. `python3 tools/diagnose.py all` to see what the upstream looks like today.
2. Patch `plugin.video.sporthdme/default.py` (or modules under `resources/`).
3. `python3 tools/diagnose.py events` again to confirm the parser still
   accepts the live HTML.
4. Probe a few stream URLs with `python3 tools/diagnose.py resolve <url>`
   to catch broken resolvers.
5. `python3 tools/release.py --addon plugin.video.sporthdme --version <next>`.
6. Review with `git diff` and push.
