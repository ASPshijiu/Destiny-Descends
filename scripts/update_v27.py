# -*- coding: utf-8 -*-
"""天命降临 v27：整体数值翻倍（三档 ×2，钳制项/上限项保持）"""
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

# 不翻倍的项（钳制线 / 游戏上限 / 特殊）
KEEP = {
    "army_leader_start_level",  # 等级上限 5
}
# 已到 -1.0 钳制线的不动（检测值 < -0.99 时保持）

def scale(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        if v <= 1:  # 0 或 1 的特殊 flat（如 navy_invasion_capacity=1? 保留）
            return v
        return int(v * 2)
    # float
    if v <= -0.99:
        return v  # 已钳制
    return round(v * 2, 2)

_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for iid, iint in IDEA_IDS.items():
    if not iid.startswith("player_assist_"):
        continue
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    new = {k: (v if k in KEEP else scale(v)) for k, v in cur.items()}
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": new})
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

# 打印重档关键值
_, b = call("GET", f"/api/projects/{PID}/ideas")
for d in b if isinstance(b, list) else []:
    if d["idea_id"] == "player_assist_heavy_idea":
        m = d.get("modifier") or {}
        print("\n=== 重档关键值（翻倍后）===")
        for k in ["research_speed_factor", "stability_factor", "war_support_factor", "political_power_factor",
                  "production_speed_buildings_factor", "industrial_capacity_factory", "army_attack_factor",
                  "recruitable_population_factor", "weekly_manpower", "experience_gain_factor", "surrender_limit",
                  "consumer_goods_factor", "naval_damage_factor", "special_forces_cap_flat", "command_power_gain"]:
            if k in m:
                print(f"  {k}: {m[k]}")
