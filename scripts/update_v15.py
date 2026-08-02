# -*- coding: utf-8 -*-
"""天命降临 v15：修正 23 个无效 modifier → 游戏真实 modifier（含建造速度）"""
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

# 映射：无效 key -> 正确 key 列表（值按 split 数分配）
FIX = {
    "production_speed_factor": [],  # 删除（效率已有专门 modifier）
    "building_speed_factor": ["production_speed_buildings_factor", "production_speed_infrastructure_factor",
                              "production_speed_dockyard_factor", "production_speed_industrial_complex_factor"],
    "dockyard_speed_factor": [],  # 并入上面
    "resource_gain_factor": ["local_resources_factor"],
    "navy_attack_factor": ["naval_damage_factor", "navy_capital_ship_attack_factor",
                           "navy_screen_attack_factor", "navy_submarine_attack_factor"],
    "navy_defence_factor": ["navy_capital_ship_defence_factor", "navy_screen_defence_factor"],
    "naval_max_range_factor": ["navy_max_range_factor"],
    "air_attack_factor": [],
    "air_defence_factor": [],
    "air_bombing_factor": ["air_bombing_targetting"],
    "ace_generation_chance_factor": ["air_ace_generation_chance_factor"],
    "volunteer_factor": ["send_volunteer_size"],
    "compliance_gain_factor": ["compliance_growth"],
    "planning_speed_factor": ["planning_speed"],
    "artillery_attack_factor": ["army_artillery_attack_factor"],
    "tank_attack_factor": ["army_armor_attack_factor"],
    "infantry_attack_factor": ["army_infantry_attack_factor"],
    "intel_network_speed": ["intel_network_gain_factor"],
    "opinion_gain_mult": ["opinion_gain_monthly_factor"],
    "advisor_cost_factor": ["political_advisor_cost_factor", "army_chief_cost_factor",
                            "navy_chief_cost_factor", "air_chief_cost_factor", "high_command_cost_factor"],
    "equipment_consumption_factor": [],
    "conversion_speed": ["equipment_conversion_speed"],
    "air_accident_chance_factor": ["air_accidents_factor"],
}

_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for iid, iint in IDEA_IDS.items():
    if not iid.startswith("player_assist_"):
        continue
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    new = dict(cur)
    changed = []
    for oldk, newks in FIX.items():
        if oldk in new:
            val = new.pop(oldk)
            changed.append(oldk)
            n = max(len(newks), 1)
            for nk in newks:
                new[nk] = round(val / n, 2) if n > 1 else val
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": new})
    print(f"PUT {iid} ({len(new)} mods) 替换 {len(changed)} ->", s, (str(b2)[:120] if s >= 300 else ""))
    if changed:
        print("  替换:", changed)

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:160])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea",)) if isinstance(b, dict) else "?")
