# -*- coding: utf-8 -*-
"""天命降临 v26：修正不合理数值（人口/海军攻击/征兵率/政治点）"""
import json, os, sys, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008

def call(m, p, body=None):
    d = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(BASE + p, data=d, method=m)
    r.add_header("Content-Type", "application/json; charset=utf-8")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "x")
    try:
        x = urllib.request.urlopen(r, timeout=90)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

# 轻/中/重新值
ADJ = {
    "recruitable_population_factor": (0.15, 0.45, 1.50),
    "weekly_manpower": (50, 150, 400),
    "conscription": (0.03, 0.08, 0.15),
    "naval_damage_factor": (0.10, 0.25, 0.60),
    "navy_capital_ship_attack_factor": (0.10, 0.25, 0.60),
    "navy_capital_ship_defence_factor": (0.10, 0.25, 0.60),
    "navy_screen_attack_factor": (0.10, 0.25, 0.60),
    "navy_screen_defence_factor": (0.10, 0.25, 0.60),
    "navy_submarine_attack_factor": (0.10, 0.25, 0.60),
    "political_power_gain": (0.5, 1.5, 4.0),
}
TIERS = {"player_assist_light_idea": 0, "player_assist_medium_idea": 1, "player_assist_heavy_idea": 2}

_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for iid, iint in IDEA_IDS.items():
    if iid not in TIERS:
        continue
    t = TIERS[iid]
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    for k, vals in ADJ.items():
        cur[k] = vals[t]
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": cur})
    print(f"PUT {iid} ->", s, (str(b2)[:120] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea",)) if isinstance(b, dict) else "?")
