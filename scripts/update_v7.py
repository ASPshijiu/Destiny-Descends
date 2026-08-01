# -*- coding: utf-8 -*-
"""天命降临 v7：追加 30 项缺失高价值增益维度"""
import json, os, sys, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008
IDEA_IDS = {"player_assist_light_idea": 369870, "player_assist_medium_idea": 369871, "player_assist_heavy_idea": 369872}

def call(m, p, body=None):
    d = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(BASE + p, data=d, method=m)
    r.add_header("Content-Type", "application/json; charset=utf-8")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
    try:
        x = urllib.request.urlopen(r, timeout=60)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

# 30 项新维度（轻/中/重渐进）
NEW = {
    # 陆军
    "army_speed_factor": (0.05, 0.10, 0.20),
    "army_org_regain": (0.05, 0.10, 0.20),
    "breakthrough_factor": (0.05, 0.10, 0.20),
    "max_dig_in_factor": (0.05, 0.10, 0.20),
    "special_forces_cap_flat": (2, 4, 8),
    "army_core_defence_factor": (0.05, 0.10, 0.20),
    # 海军
    "navy_org_factor": (0.05, 0.10, 0.20),
    "naval_morale_factor": (0.05, 0.10, 0.20),
    "navy_capital_ship_attack_factor": (0.05, 0.10, 0.20),
    "shore_bombardment_bonus": (0.05, 0.10, 0.20),
    # 空军
    "air_range_factor": (0.05, 0.10, 0.20),
    "air_maximum_speed_factor": (0.05, 0.10, 0.20),
    "air_ace_bonuses_factor": (0.10, 0.20, 0.50),
    "air_untrained_pilots_penalty_factor": (-0.10, -0.20, -0.40),
    # 后勤
    "supply_node_range": (0.05, 0.10, 0.20),
    "out_of_supply_factor": (-0.05, -0.10, -0.20),
    "army_fuel_consumption_factor": (-0.05, -0.10, -0.20),
    # 经济
    "civilian_factory_use": (-0.02, -0.05, -0.10),
    "production_factory_efficiency_gain_factor": (0.05, 0.10, 0.20),
    # 人口
    "weekly_manpower": (5, 10, 20),
    # 政治/指挥
    "political_power_gain": (0.50, 1.0, 2.0),
    "max_command_power_mult": (0.10, 0.20, 0.50),
    "army_leader_start_level": (1, 2, 3),
    # 防御
    "surrender_limit": (0.05, 0.10, 0.20),
    "attrition": (-0.05, -0.10, -0.20),
    "terrain_penalty_reduction": (0.05, 0.10, 0.20),
    # 外交
    "trade_opinion_factor": (0.05, 0.10, 0.20),
    # 情报
    "intel_network_gain_factor": (0.10, 0.20, 0.50),
    "encryption_factor": (0.10, 0.20, 0.50),
    "decryption_factor": (0.10, 0.20, 0.50),
}

TIER = {"player_assist_light_idea": 0, "player_assist_medium_idea": 1, "player_assist_heavy_idea": 2}
for iid, iint in IDEA_IDS.items():
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    t = TIER[iid]
    for k, v in NEW.items():
        cur[k] = v[t]
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": cur})
    print(f"PUT {iid} ({len(cur)} modifiers) ->", s, (str(b2)[:150] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:150])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s)
if isinstance(b, dict):
    issues = [(k, it.get("level"), it.get("msg")) for k in ("idea", "focus", "event", "decision") for it in b.get(k, [])]
    print("lint issues:", len(issues))
    for k, lv, msg in issues[:30]:
        print(f"  [{k}] {lv}: {str(msg)[:140]}")
