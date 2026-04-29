# Handover for `plugin.video.sporthdme` maintenance

> Paste this whole file (or its first half plus the “Resume prompt” block at the
> bottom) to the next LLM session and they should be able to pick up where we
> left off.

---

## TL;DR

The user is **bugatsinho**, maintainer of a Kodi repository at
`/Users/elianaalfaro/PycharmProjects/bugatsinho.github.io` (also linked from a
second workspace path that points at the same content). They want help keeping
**`plugin.video.sporthdme`** working, especially the resolvers, since the
upstream sites rotate domains and player implementations on a regular cadence.

In this session we:

1. **Set up a working maintenance toolchain** under `tools/` (all stdlib-only
   so it runs anywhere without `pip install`).
2. **Diagnosed the live state** of every part of the addon.
3. **Cracked the new obfuscation** used by `glisco.link` / `sansat.link` —
   we can extract the m3u8 URL purely in Python.
4. **Got stuck** on a final layer: the m3u8 from the decoded config returns
   HTTP 404 from every IP we tried (US ISP and a Cyprus-ish VPN — `156.67.94.23`).
   This needs a final piece of evidence (a working capture from a real user
   browser session) before the resolver can ship.

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
├── plugin.video.sporthdme/    # the addon source (current ver 0.1.84)
│   ├── addon.xml
│   ├── default.py             # 707 lines, all logic (events + resolve2)
│   └── resources/modules/     # client.py, control.py, cache.py, jsunpack.py,
│                              # jsUnwiser.py, jsontools.py, econfig.py (NEW)
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

## What we changed in this session

### Code

* `plugin.video.sporthdme/default.py` — single in-flight edit:
  ```python
  # was:
  Live_url = 'https://super.league.do'
  # now:
  Live_url = 'https://super.league.st'  # was super.league.do; domain rotated 2026
  ```
  The user confirmed the live events list URL rotated. Diagnose confirmed
  47 matches parse cleanly with the existing `window.matches=JSON.parse(...)`
  regex on the new domain.

* **New module** `plugin.video.sporthdme/resources/modules/econfig.py` —
  pure-stdlib decoder for `window._econfig` blobs. Public API:
  ```python
  from resources.modules import econfig
  m3u8, cfg = econfig.extract_stream_from_html(html_text)
  # cfg keys: swarm_id, stream_url, stream_url_nop2p, p2p, p2p_tracker,
  # domainlocked, autoplay, alt_domain, hframes, ...
  ```
  Verified working against fresh captures from `fisherman.click` and
  `wilderness.click`.

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
  pushing a tag like `plugin.video.sporthdme-0.1.85` or via workflow_dispatch.
  Commits the result to `master` and uploads the new zip as a GitHub Release
  asset.

* `tools/diagnose.py` — `events`, `channels`, `resolve <url>`, `all`
  subcommands. Default events URL: `https://super.league.st`. Saves bodies
  to `/tmp/sporthd_*.html` when parsing fails.

### Things we **did not** ship yet

* No version bump (still 0.1.84 in the repo).
* No new commit. The Live_url change is uncommitted.
* No resolver fix in `default.py` for `glisco.link` / `sansat.link`. The
  current `resolve2()` in default.py does not match the new player markup, so
  these channels do nothing (or throw an unhandled exception) in production.

---

## The resolver puzzle (where we got stuck)

### Site flow (verified live)

```
super.league.st                          ← events list page (HTML, JSON-in-script)
   └── window.matches = JSON.parse(`[...]`)
        └── channel.links = [
              "https://glisco.link/ch?id=N",
              "https://sansat.link/ch?id=N"
            ]
              └── GET that URL  →  big anti-debug HTML (irrelevant)
              └── GET https://<host>/api/player.php?id=N
                  → JSON: {"url": "https://fisherman.click/e/<slug>"}
                  (sansat.link → wilderness.click,
                   glisco.link  → fisherman.click)
                    └── GET that URL
                        → HTML containing
                          <script id="config">window._econfig='<huge b64>'</script>
                          <script src="/assets/stream.js?_v=0.0.13">
                          (stream.js is webpack-obfuscated)
                            └── _econfig decodes to JSON with stream_url_nop2p
                                = https://<random-prefix>.28585519.net:8443/hls/<slug>.m3u8?s=...&e=...
                                  ↑ random-prefix changes per region/IP (CDN routing)
                                  ↑ s= is HMAC-style sig, e= is unix-seconds expiry
                                    (typically 6 hours forward)
                                ← THIS IS WHAT WE COULDN'T FETCH
```

### `_econfig` decoding (cracked, in `econfig.py`)

Reverse-engineered from `/assets/stream.js`, function `_0x89331a` near offset
78050. The plain-Python algorithm:

```python
def decode_econfig(b64):
    layer1 = base64.b64decode(b64 + '=' * (-len(b64) % 4)).decode('latin-1')
    chunk = len(layer1) // 4
    chunks = [layer1[i*chunk:(i+1)*chunk] for i in range(4)]
    out = [None]*4
    for i, target_idx in enumerate([2, 0, 3, 1]):
        c = chunks[i]
        c = c[:3] + c[4:]                    # drop char at index 3
        out[target_idx] = base64.b64decode(c + '=' * (-len(c) % 4)).decode('latin-1')
    final_b64 = ''.join(out)
    return json.loads(base64.b64decode(final_b64 + '=' * (-len(final_b64) % 4)).decode('latin-1'))
```

This produces a dict like:

```json
{
  "swarm_id": "xs_cdr6b5ma6gg40",
  "stream_url": "https://<prefix>.28585519.net:8443/hls/cd4vgvhakbwy8.m3u8?s=...&e=1777491315",
  "stream_url_nop2p": "https://<prefix>.28585519.net:8443/hls/cd4vgvhakbwy8.m3u8?s=...&e=1777491315",
  "p2p": true,
  "p2p_tracker": "wss://hlspatch.net:3000",
  "domainlocked": false,
  "autoplay": true,
  "play_3_secs": false,
  "sandbox_block": true,
  "devtools_block": true,
  "hframes_inject_secs": 3,
  "pop1": true,
  "debug": true,
  "alt_domain": "1",
  "pops": ["<obfuscated JS string for popunders>"],
  "hframes": ["https://lernodydenknow.info/redirect?...", "https://ns.clypeiescapes.com/..."]
}
```

### The unsolved bit

> **⚠ MOST LIKELY EXPLANATION (added by user after the test run):**
> The user pointed out that when we ran our tests, **no live matches were
> being broadcast**. These streams only carry data while a game is on. A
> live-stream CDN that has no segments to serve responds with HTTP 404 for
> the manifest URL even when the signature is perfectly valid. This matches
> exactly what we observed: every channel returned 404 simultaneously
> regardless of IP/UA, but `/auth` returned 403 (= the server exists),
> non-Chrome UAs returned 403 (= edge filter, never reached the manifest),
> and Chrome UAs returned 404 (= reached the manifest layer, no content
> there yet).
>
> **Recommended first action for the next session: do nothing about
> "missing tokens" yet.** Instead, wait until a live match is on (check
> `https://super.league.st` for an event in green / "LIVE"), then re-run
> `tools/diagnose.py resolve <a-glisco-or-sansat-url>` and see if the m3u8
> now returns `#EXTM3U`. If yes, the decoder + the resolver branch in
> "Recommended next steps" #2 below will Just Work and the only thing left
> is shipping 0.1.85.
>
> If it still 404s during a confirmed live match, fall back to the cookie /
> WS-tracker hypotheses below.

Fetching the resulting `stream_url_nop2p` from Python returns:

| User-Agent                          | Status |
|-------------------------------------|--------|
| Chrome desktop                      | 404    |
| iPad / curl / Kodi / VLC / minimal  | 403    |
| Any UA, with parent origin headers  | 404 (Chrome) / 403 (others) |

Headers tried (none worked): `Referer: https://fisherman.click/`,
`Referer: https://glisco.link/`, `Referer: https://super.league.st/`,
no Referer, with Origin, without Origin, with `hf1=1` cookie, with HEAD first,
URL transformations (drop `:8443`, replace `/hls/` with `/live/` or `/p2p/`,
strip `.m3u8`, etc.). All consistently 404.

`Access-Control-Allow-Origin: *` is set on responses, so this is **not** CORS.
The 404 vs 403 split is suspicious -- it implies the server treats Chrome and
non-Chrome differently, but neither path reaches the actual stream.

We tested from the user's regular IP and from a VPN that landed at
`156.67.94.23`. Different CDN sub-domain prefixes were assigned per IP
(`esljcbdw.28585519.net` vs `yesllahq.28585519.net`), confirming the routing
*is* IP-aware. But neither IP unlocked playback.

### What is most likely missing

Best guesses (in order):

1. **A JS-set cookie** — `stream.js` (webpack-bundled) probably sets a
   document.cookie value computed at runtime, which then needs to be sent on
   the m3u8 GET. Static analysis didn't surface this because the bundler
   indirection (`_0xdf6f` string lookups) hides the assignment. Worth running
   stream.js in Node + jsdom and inspecting `document.cookie` after init.
2. **Per-session token via WebSocket** — the config has
   `p2p_tracker: "wss://hlspatch.net:3000"`. Maybe the player must register
   with that tracker first, and only then is the IP allowed to fetch the
   manifest. This would explain the 404 (until you register, the path is
   genuinely "not found" for you).
3. **Geo-restriction beyond what we tested** — plain residential GR/IT IPs
   may be required. The user reported this addon used to work for users in
   Greece; the VPN we tested likely landed elsewhere
   (`156.67.94.23` reverses to colocation hosting).
4. **TLS/HTTP fingerprint check** — Cloudflare-style ja3 fingerprinting on the
   CDN. urllib's TLS stack would mismatch real Chrome, returning custom errors.
   Less likely given the consistent 404 even with different UAs.

### What evidence would unblock this

The single most useful thing would be a **HAR file** captured from a real
browser session that successfully plays a stream:

1. Open DevTools → Network tab, "Preserve log" on, "Disable cache" on.
2. Open `https://super.league.st`, click any live event, pick a `glisco`
   or `sansat` channel.
3. As soon as the player starts buffering, save All as HAR.

From the HAR we can read:
- the exact order of network calls (any extra auth/init request?),
- exact request headers Chrome sent for the m3u8 GET (including any `Cookie`),
- whether there was a 30x redirect chain we missed.

A `wireshark` PCAP would also work but HAR is simpler.

---

## Live findings worth remembering

* Channels source `https://one.sporthd.me/api/trpc/...` (the 24/7 channels
  `BASEURL + 'api/trpc/.../mutual.getAllChannels'`) is **dead** —
  `one.sporthd.me` no longer resolves. **The user chose to disable / hide the
  feature but keep the code** (option `comment_out`). That edit is also still
  pending — `default.py` still calls `fetch_and_store_channel_data()` from
  `router('events')`.

* Today only **two stream hosts** appear in events payload: `glisco.link`
  (83 stream URLs) and `sansat.link` (83 stream URLs). The other 9 in the
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

0. **Re-test during a confirmed live match first.** This is the highest-prior
   action. Per the user's own observation, the 404s we saw probably just mean
   "no broadcast right now". Open `https://super.league.st`, pick an event
   that is currently LIVE (green badge / inside its time window), grab one of
   its `glisco.link` / `sansat.link` URLs, and run:
   ```bash
   python3 tools/diagnose.py resolve "https://glisco.link/ch?id=N"
   ```
   If the final m3u8 GET returns `#EXTM3U`, **skip step 1** entirely and go
   straight to step 2.

1. **Only if step 0 still fails on a confirmed live match**, dig into the
   missing-token hypothesis:
   - Run `stream.js` in Node + jsdom (`npm i jsdom`) on a captured
     `_econfig`. Snapshot `document.cookie` and any `XHR/fetch` calls
     before hls.js touches the manifest. That tells us the missing piece.
   - OR ask the user for a HAR file (see “What evidence would unblock this”
     above) — much faster.
   - Encode the missing piece into `econfig.py` as additional steps before
     returning the URL, OR (more likely) into `default.py` as additional
     headers/cookies for the final request.

2. **Wire the new resolver into `default.py`**. Do this surgically — DO NOT
   refactor `resolve2()`. Add a new branch right after the existing
   `elif '//dabac' in url:` block:
   ```python
   elif '//glisco' in url or '//sansat' in url:
       Dialog.notification(NAME, "[COLOR skyblue]Attempting To Resolve Link Now[/COLOR]", ICON, 2000, False)
       referer = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
       chan_id = url.split('id=')[-1]
       api_resp = six.ensure_text(
           client.request(referer + 'api/player.php?id=' + chan_id, referer=url)
       )
       frame = json.loads(api_resp)['url']
       html = six.ensure_text(client.request(frame, referer=url))
       from resources.modules import econfig as _econfig
       flink, _cfg = _econfig.extract_stream_from_html(html)
       if not flink:
           raise Exception('econfig extraction failed for ' + url)
       # Origin / Referer must match the iframe (fisherman.click / wilderness.click)
       frame_origin = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(frame))
       stream_headers = {
           'Referer': frame_origin + '/',
           'Origin': frame_origin,
           'User-Agent': ua_win,
           # TODO: add the missing piece here once we know what it is
       }
       stream_url = xbmc_curl_encode(flink, stream_headers)
   ```

3. **Hide the 24/7 Channels entry**. In `Main_menu()` keep only the
   `LIVE EVENTS` plus settings/clear/version items. In `router()` remove the
   `if time_to_update(): fetch_and_store_channel_data()` call (or wrap in a
   no-op) so the broken `one.sporthd.me` request is never made.

4. **Cut release 0.1.85** with `tools/release.py`. Suggested news block:
   ```
   - update Live_url to super.league.st
   - new resolver path for glisco/sansat (econfig decoder)
   - hide non-functional 24/7 Channels entry until upstream returns
   ```

5. **Have the user test**. If a stream still doesn't play, ask the user to
   send the HAR mentioned above. Then iterate.

---

## Resume prompt (paste this verbatim to a fresh LLM)

> I'm bugatsinho, maintainer of a Kodi repository at
> `/Users/elianaalfaro/PycharmProjects/bugatsinho.github.io`.  I'm picking up
> a maintenance task on `plugin.video.sporthdme` that another agent
> (Claude Opus 4.7) was working on. Please **read
> `tools/HANDOVER.md`** in the repo first — it has the full state of where we
> are, what works, and what still needs doing. The unsolved problem is that
> after decoding `window._econfig` we get a clean m3u8 URL, but fetching it
> directly returns HTTP 404 from every IP we tested (Chrome UA → 404,
> non-Chrome UAs → 403). The most likely missing piece is a cookie/token set
> by the obfuscated `stream.js`, or a registration ping with
> `wss://hlspatch.net:3000`. Please continue from step 1 of "Recommended
> next steps". Use Greek when chatting with me. Don't strip `six`/Python 2
> support — Kodi 18 is still in scope.

---

_Written: 2026-04-29 by Claude Opus 4.7. Last verified live request:
`156.67.94.23` (VPN) at 13:44 UTC -- still 404 on m3u8 fetch._
