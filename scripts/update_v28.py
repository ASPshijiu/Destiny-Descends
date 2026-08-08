# -*- coding: utf-8 -*-
"""天命降临 v28：按原版 modifier 极限值重设三档（轻×1 / 中×2 / 重×5）"""
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

ext = json.load(open(r"C:\Users\xw130\Desktop\hoi4\vanilla_modifier_extremes.json"))
# 手动基准（原版 json 缺失/语义特殊项）：name -> (轻, 中, 重)
MANUAL = {
    "weekly_manpower": (1000, 3000, 5000),          # 原版极限 7000
    "political_power_gain": (1, 2, 3),              # 原版极限 1.0
    "industrial_capacity_factory": (2, 5, 10),      # flat 工厂
    "special_forces_cap_flat": (3, 8, 15),          # flat 特种上限
    "army_leader_start_level": (1, 2, 5),           # 上限 5
    "naval_invasion_capacity": (1, 2, 3),           # flat 登陆容量
    "conscription": (0.05, 0.1, 0.25),              # 原版极限 0.25
}
# 负向 buff 型（原版 min 为负，按 min×倍数，钳制 -1.0）
NEG_TYPES = {"consumer_goods_factor", "training_time_factor", "justify_war_goal_time",
             "air_accidents_factor", "air_untrained_pilots_penalty_factor", "industry_air_damage_factor",
             "advisor_cost_factor", "army_fuel_consumption_factor", "out_of_supply_factor",
             "supply_consumption_factor", "attrition", "equipment_consumption_factor",
             "political_advisor_cost_factor", "army_chief_cost_factor", "navy_chief_cost_factor",
             "air_chief_cost_factor", "high_command_cost_factor", "command_abilities_cost_factor",
             "land_reinforce_rate", "civilian_factory_use"}

MULT = (1.0, 2.0, 5.0)  # 轻/中/重

def new_value(key, tier):
    if key in MANUAL:
        return MANUAL[key][tier]
    if key not in ext:
        return None
    mx, mn = ext[key][0], ext[key][1]
    mult = MULT[tier]
    if key in NEG_TYPES:
        v = round(mn * mult, 2)
        return max(v, -1.0)  # 钳制 -100%
    # 正值
    base = mx if mx > 0 else (abs(mn) if mn < 0 else 1.0)
    v = round(base * mult, 2)
    if isinstance(mx, int) or (key.endswith("_flat") or key in ("weekly_manpower",)):
        v = int(v)
    return v

_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
TIERS = {"player_assist_light_idea": 0, "player_assist_medium_idea": 1, "player_assist_heavy_idea": 2}
for iid, iint in IDEA_IDS.items():
    if iid not in TIERS:
        continue
    t = TIERS[iid]
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    new = {}
    skipped = []
    for k in cur:
        v = new_value(k, t)
        if v is None:
            skipped.append(k)
            continue
        new[k] = v
    if skipped:
        print(f"{iid} 无基准保留原值: {skipped}")
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": new})
    print(f"PUT {iid} ({len(new)} mods) ->", s, (str(b2)[:120] if s >= 300 else ""))

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
        print("\n=== 重档关键值（原版×5 基准）===")
        for k in ["research_speed_factor", "stability_factor", "war_support_factor", "political_power_factor",
                  "production_speed_buildings_factor", "industrial_capacity_factory", "army_attack_factor",
                  "recruitable_population_factor", "weekly_manpower", "experience_gain_factor", "surrender_limit",
                  "consumer_goods_factor", "naval_damage_factor", "political_power_gain", "conscription",
                  "army_org_factor", "local_resources_factor"]:
            if k in m:
                print(f"  {k}: {m[k]}")
