#!/usr/bin/env python3
"""
Live diagnostics for plugin.video.sporthdme.

Hits the real upstream sites and reports which scraping/resolver patterns
still match. Pure stdlib (urllib only), so it can run anywhere.

Usage:
    # Full scan: events page + tRPC channels + a couple of stream pages
    python3 tools/diagnose.py all

    # Individual checks
    python3 tools/diagnose.py events
    python3 tools/diagnose.py channels
    python3 tools/diagnose.py resolve <stream-url>

    # Override the events URL temporarily
    python3 tools/diagnose.py events --live-url https://super.league.st

Each check prints PASS / WARN / FAIL plus a short reason and a snippet of
evidence so you can paste it back into a chat without sharing the full HTML.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

DEFAULT_BASE_URL = "https://one.sporthd.me/"
DEFAULT_LIVE_URL = "https://super.league.st"

UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
UA_MOBILE = (
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36"
)

# Patterns the addon currently relies on. Keep these in sync with default.py.
EVENTS_PATTERN_NEW = r'window\.matches\s*=\s*JSON\.parse\(`(\[.+?\])`\)'
EVENTS_PATTERN_OLD = r'"matches"\s*\:\s*(\[.+?])}]]}]n'

# Resolver host fragments from default.py: resolved[]
RESOLVER_HOSTS = [
    "//dabac",
    "//sansat",
    "//istorm",
    "//zvision",
    "//glisco",
    "//bedsport",
    "//coolrea",
    "//evfancy",
    "//s2watch",
    "//vuen",
    "//gopst",
]

# Player-page signatures used inside resolve2() in default.py.
PLAYER_SIGNATURES = {
    "fid_pattern": r"<script>fid=['\"](.+?)['\"]",
    "next_iframe": r"<iframe[^>]+src=\"([^\"]+)",
    "h_t_t_p_join": r'\["h","t","t","p"',
    "player_src": r"player\.src\(\{src:",
    "hlsjsConfig": r"hlsjsConfig",
    "new_clappr": r"new Clappr",
    "player_setSrc": r"player\.setSrc\(",
    "new_player_paren": r"new Player\(",
    "channel_key_const": r'const\s+CHANNEL_KEY\s*=',
    "bundle_const": r'const\s+BUNDLE\s*=',
    "m3u8_inline": r"https?://[^\s\"']+\.m3u8",
    "data_page_app": r'data-page=',
}


# --------------------------------------------------------------------------- #
# HTTP helper
# --------------------------------------------------------------------------- #

@dataclass
class HttpResult:
    url: str
    status: int
    final_url: str
    body: str
    error: Optional[str] = None


def http_get(
    url: str,
    *,
    headers: Optional[dict[str, str]] = None,
    timeout: float = 20.0,
) -> HttpResult:
    headers = dict(headers or {})
    headers.setdefault("User-Agent", UA_DESKTOP)
    headers.setdefault("Accept", "*/*")
    headers.setdefault("Accept-Language", "en-US,en;q=0.9")

    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            try:
                body = raw.decode("utf-8", errors="replace")
            except Exception:
                body = raw.decode("latin-1", errors="replace")
            return HttpResult(url=url, status=resp.status, final_url=resp.geturl(), body=body)
    except urllib.error.HTTPError as exc:
        return HttpResult(url=url, status=exc.code, final_url=url, body="", error=str(exc))
    except (urllib.error.URLError, socket.timeout, ConnectionError) as exc:
        return HttpResult(url=url, status=0, final_url=url, body="", error=str(exc))


# --------------------------------------------------------------------------- #
# Reporting helpers
# --------------------------------------------------------------------------- #

def line(label: str, status: str, detail: str = "") -> None:
    icon = {"PASS": "[ OK ]", "WARN": "[WARN]", "FAIL": "[FAIL]", "INFO": "[INFO]"}.get(status, "[ ?? ]")
    msg = f"{icon} {label}"
    if detail:
        msg += f" -- {detail}"
    print(msg)


def shorten(text: str, n: int = 160) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= n else text[:n] + "..."


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_events(live_url: str) -> int:
    # Note: default.py does requests.get(Live_url) without appending any path,
    # so we hit the bare URL exactly the way the addon does.
    print(f"\n=== events  ({live_url}) ===")
    target = live_url
    res = http_get(target, headers={"Referer": live_url + "/"})

    if res.error or res.status >= 400 or not res.body:
        line(target, "FAIL", f"status={res.status} err={res.error or 'empty body'}")
        return 1

    line(target, "PASS", f"status={res.status}, body={len(res.body)} bytes, final={res.final_url}")

    new_match = re.findall(EVENTS_PATTERN_NEW, res.body, re.DOTALL)
    if new_match:
        try:
            data = json.loads(new_match[0])
            line("EVENTS_PATTERN_NEW (window.matches=JSON.parse)", "PASS", f"{len(data)} matches")
        except Exception as exc:
            line("EVENTS_PATTERN_NEW", "WARN", f"matched but JSON parse failed: {exc}")
    else:
        line("EVENTS_PATTERN_NEW (window.matches=JSON.parse)", "FAIL", "regex did not match")

    old_match = re.findall(EVENTS_PATTERN_OLD, res.body.replace(",false", ""), re.DOTALL)
    if old_match:
        line('EVENTS_PATTERN_OLD ("matches": [...]}]]}]n)', "PASS", "regex matched")
    else:
        line('EVENTS_PATTERN_OLD ("matches": [...]}]]}]n)', "WARN", "regex did not match (only relevant if NEW also failed)")

    if not new_match and not old_match:
        # Save body for inspection.
        snippet_path = "/tmp/sporthd_events_body.html"
        try:
            with open(snippet_path, "w", encoding="utf-8") as fh:
                fh.write(res.body)
            line("debug", "INFO", f"raw body saved to {snippet_path} for offline inspection")
        except OSError:
            pass
        return 1

    if new_match:
        # Extract distinct stream-host hints so we know which resolvers matter today.
        all_links = re.findall(r"https?://[^\s\"'`\\]+", new_match[0])
        hosts: dict[str, int] = {}
        for url in all_links:
            try:
                netloc = urllib.parse.urlparse(url).netloc
            except Exception:
                continue
            if not netloc:
                continue
            hosts[netloc] = hosts.get(netloc, 0) + 1
        if hosts:
            top = sorted(hosts.items(), key=lambda kv: -kv[1])[:15]
            print("    top stream hosts in events payload:")
            for h, n in top:
                marker = ""
                for frag in RESOLVER_HOSTS:
                    if frag.lstrip("/") in h:
                        marker = f"   <- known resolver fragment {frag}"
                        break
                print(f"      {n:>4}  {h}{marker}")

    return 0


def check_channels(base_url: str) -> int:
    print(f"\n=== channels  ({base_url}) ===")
    url = (
        base_url.rstrip("/")
        + "/api/trpc/mutual.getTopTeams,saves.getAllUserSaves,mutual.getFooterData,"
        "mutual.getAllChannels,mutual.getWebsiteConfig"
        '?batch=1&input={"0":{"json":null,"meta":{"values":["undefined"]}},'
        '"1":{"json":null,"meta":{"values":["undefined"]}},'
        '"2":{"json":null,"meta":{"values":["undefined"]}},'
        '"3":{"json":null,"meta":{"values":["undefined"]}},'
        '"4":{"json":null,"meta":{"values":["undefined"]}}}'
    )
    res = http_get(url, headers={"User-Agent": UA_MOBILE, "Referer": base_url})
    if res.error or res.status >= 400 or not res.body:
        line(url, "FAIL", f"status={res.status} err={res.error or 'empty body'}")
        return 1

    try:
        data = json.loads(res.body)
    except json.JSONDecodeError as exc:
        line(url, "WARN", f"non-JSON response: {exc}; body starts: {shorten(res.body)}")
        return 1

    found = None
    for entry in data:
        try:
            channels = entry["result"]["data"]["json"]["allChannels"]
            found = channels
            break
        except (KeyError, TypeError):
            continue

    if not found:
        line("allChannels", "FAIL", "tRPC payload missing result.data.json.allChannels")
        return 1

    line("allChannels", "PASS", f"{len(found)} channels returned")
    if found:
        sample = found[0]
        keys = sorted(sample.keys())
        line("channel schema", "INFO", f"sample keys: {keys}")
    return 0


def check_resolver(stream_url: str) -> int:
    print(f"\n=== resolve  ({stream_url}) ===")
    res = http_get(stream_url, headers={"Referer": "https://super.league.st/"})
    if res.error or res.status >= 400 or not res.body:
        line(stream_url, "FAIL", f"status={res.status} err={res.error or 'empty body'}")
        return 1

    line(stream_url, "PASS", f"status={res.status}, body={len(res.body)} bytes")

    # Tally which player signatures match.
    matched: list[str] = []
    for name, pat in PLAYER_SIGNATURES.items():
        if re.search(pat, res.body, re.DOTALL):
            matched.append(name)
    if matched:
        line("player signatures", "PASS", ", ".join(matched))
    else:
        line("player signatures", "FAIL", "no known signature matched -- resolver needs an update")

    # Hint: which iframe the page redirects to.
    iframes = re.findall(r"<iframe[^>]+src=[\"']([^\"']+)[\"']", res.body)
    if iframes:
        line("iframes", "INFO", f"{len(iframes)} iframe(s); first: {shorten(iframes[0], 140)}")
    return 0 if matched else 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_events = sub.add_parser("events", help="check events scraping")
    p_events.add_argument("--live-url", default=DEFAULT_LIVE_URL)

    p_channels = sub.add_parser("channels", help="check 24/7 channels tRPC endpoint")
    p_channels.add_argument("--base-url", default=DEFAULT_BASE_URL)

    p_resolve = sub.add_parser("resolve", help="probe a stream URL and see which player signature matches")
    p_resolve.add_argument("url")

    p_all = sub.add_parser("all", help="run events + channels checks")
    p_all.add_argument("--live-url", default=DEFAULT_LIVE_URL)
    p_all.add_argument("--base-url", default=DEFAULT_BASE_URL)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.cmd == "events":
        return check_events(args.live_url)
    if args.cmd == "channels":
        return check_channels(args.base_url)
    if args.cmd == "resolve":
        return check_resolver(args.url)
    if args.cmd == "all":
        rc1 = check_events(args.live_url)
        rc2 = check_channels(args.base_url)
        return rc1 or rc2
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
