# -*- coding: utf-8 -*-
"""天命降临 v16：指挥点增益全面化——每日获取 flat、指挥能力成本、上限 flat"""
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

# 新指挥点增益（轻/中/重）
NEW_CP = {
    "player_assist_light_idea": {"command_power_gain": 0.5, "command_abilities_cost_factor": -0.10, "max_command_power": 50},
    "player_assist_medium_idea": {"command_power_gain": 1.5, "command_abilities_cost_factor": -0.20, "max_command_power": 150},
    "player_assist_heavy_idea": {"command_power_gain": 4.0, "command_abilities_cost_factor": -0.40, "max_command_power": 400},
}
_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for iid, iint in IDEA_IDS.items():
    if iid not in NEW_CP:
        continue
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    cur.update(NEW_CP[iid])
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": cur})
    print(f"PUT {iid} ({len(cur)} mods) ->", s, (str(b2)[:120] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:160])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea",)) if isinstance(b, dict) else "?")
