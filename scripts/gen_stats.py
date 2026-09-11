#!/usr/bin/env python3
"""gen_stats.py — regenerate assets/stats.svg with live numbers from the GitHub API.
Runs in GitHub Actions (GITHUB_TOKEN available) or locally."""
import json
import os
import sys
import urllib.request

USER = "LucioDev404"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HDRS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HDRS["Authorization"] = f"Bearer {TOKEN}"

def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    return json.load(urllib.request.urlopen(req, timeout=30))

user = get(f"https://api.github.com/users/{USER}")
repos_n = user["public_repos"]
followers = user["followers"]
created = user.get("created", "2023")[:4]

# total commits across public repos (commit search)
try:
    commits = get(f"https://api.github.com/search/commits?q=author:{USER}+is:public&per_page=1")["total_count"]
except Exception:
    commits = 0
commits_s = f"{commits}+" if commits >= 100 else str(commits)

# total stars across own (non-fork) public repos
try:
    stars = 0
    page = 1
    while True:
        batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}")
        stars += sum(r["stargazers_count"] for r in batch if not r["fork"])
        if len(batch) < 100:
            break
        page += 1
except Exception:
    stars = 0

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="830" height="130" viewBox="0 0 830 130" font-family="ui-monospace, 'Cascadia Code', 'SF Mono', Menlo, Consolas, monospace">
  <defs>
    <linearGradient id="sbar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#58A6FF"/>
      <stop offset="1" stop-color="#BC8CFF"/>
    </linearGradient>
    <filter id="sglow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect x="1" y="1" width="828" height="128" rx="12" fill="#0D1117" stroke="#21262D"/>
  <rect x="1" y="1" width="828" height="3" rx="2" fill="url(#sbar)"/>

  <text x="415" y="34" text-anchor="middle" font-size="13" fill="#58A6FF" letter-spacing="4">STATS</text>

  <text x="185" y="82" text-anchor="middle" font-size="30" fill="#E6EDF3" filter="url(#sglow)">{commits_s}<tspan fill="#58A6FF">+</tspan></text>
  <text x="185" y="106" text-anchor="middle" font-size="12" fill="#8B949E">public commits</text>

  <rect x="330" y="55" width="1.5" height="55" fill="#21262D"/>

  <text x="415" y="82" text-anchor="middle" font-size="30" fill="#E6EDF3" filter="url(#sglow)">{repos_n}</text>
  <text x="415" y="106" text-anchor="middle" font-size="12" fill="#8B949E">public repos</text>

  <rect x="500" y="55" width="1.5" height="55" fill="#21262D"/>

  <text x="585" y="82" text-anchor="middle" font-size="30" fill="#E6EDF3" filter="url(#sglow)">{stars}<tspan fill="#BC8CFF">&#9733;</tspan></text>
  <text x="585" y="106" text-anchor="middle" font-size="12" fill="#8B949E">stars earned</text>

  <rect x="668" y="55" width="1.5" height="55" fill="#21262D"/>

  <text x="750" y="82" text-anchor="middle" font-size="30" fill="#28C840" filter="url(#sglow)">&#9679;</text>
  <text x="750" y="106" text-anchor="middle" font-size="12" fill="#8B949E">active now</text>
</svg>
'''

with open("assets/stats.svg", "w") as f:
    f.write(svg)
print(f"stats.svg regenerated: commits={commits} repos={repos_n} stars={stars} since={created}")
