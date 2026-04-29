import json
import re
import urllib.request
import time

url = "https://super.league.st"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    body = resp.read().decode("utf-8", errors="replace")

match = re.search(r'window\.matches\s*=\s*JSON\.parse\(`(\[.+?\])`\)', body, re.DOTALL)
data = json.loads(match.group(1))

now = time.time()
print(f"Current time: {now}")
for event in data:
    start = event.get("startTimestamp", 0) / 1000
    duration = event.get("duration", 120) * 60
    end = start + duration
    if start <= now <= end:
        print(f"LIVE Event: {event.get('team1')} vs {event.get('team2')} (Start: {start}, End: {end})")
        for channel in event.get("channels", []):
            for link in channel.get("links", []):
                if "glisco.link" in link or "sansat.link" in link:
                    print(f"  -> {link}")
