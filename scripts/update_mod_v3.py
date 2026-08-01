# -*- coding: utf-8 -*-
"""v3 优化：基于创意工坊同类 mod 调研，扩展 12 个新 buff 维度。含校验/导出/安装"""
import json, os, sys, urllib.request, urllib.error, zipfile, shutil, io
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008
MODDIR = r"C:\Users\xw130\Documents\Paradox Interactive\Hearts of Iron IV\mod"

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

# ---- 基础 30 项（v2 已确认合法）----
BASE_MOD = {
    "political_power_factor": 0.15, "stability_factor": 0.10, "war_support_factor": 0.10,
    "consumer_goods_factor": -0.05, "research_speed_factor": 0.10,
    "production_speed_factor": 0.10, "building_speed_factor": 0.10,
    "dockyard_speed_factor": 0.10, "repair_speed_factor": 0.10,
    "industrial_capacity_factory": 2, "resource_gain_factor": 0.10,
    "army_attack_factor": 0.05, "army_defence_factor": 0.05,
    "army_org_factor": 0.10, "army_morale_factor": 0.10,
    "training_time_factor": -0.10,
    "experience_gain_army": 0.10, "experience_gain_navy": 0.10, "experience_gain_air": 0.10,
    "recruitable_population_factor": 0.05,
    "navy_attack_factor": 0.05, "navy_defence_factor": 0.05,
    "naval_speed_factor": 0.05, "naval_max_range_factor": 0.05,
    "air_attack_factor": 0.05, "air_defence_factor": 0.05,
    "air_agility_factor": 0.05, "air_bombing_factor": 0.05,
    "justify_war_goal_time": -0.10,
}
# ---- 调研新增 12 维度（参考 +Easybuff / Precise Buffs / TFR cheat decision）----
LIGHT_EXTRA = {
    "ace_generation_chance_factor": 0.10, "supply_consumption_factor": -0.05,
    "fuel_gain_factor": 0.05, "volunteer_factor": 0.05, "compliance_gain_factor": 0.05,
    "command_power_gain_mult": 0.10, "planning_speed_factor": 0.10,
    "max_planning_factor": 0.05, "industry_air_damage_factor": -0.10,
    "equipment_capture_factor": 0.05, "production_factory_max_efficiency_factor": 0.05,
    "artillery_attack_factor": 0.05,
}
MEDIUM_EXTRA = {
    "ace_generation_chance_factor": 0.20, "supply_consumption_factor": -0.10,
    "fuel_gain_factor": 0.10, "volunteer_factor": 0.10, "compliance_gain_factor": 0.10,
    "command_power_gain_mult": 0.20, "planning_speed_factor": 0.15,
    "max_planning_factor": 0.10, "industry_air_damage_factor": -0.20,
    "equipment_capture_factor": 0.10, "production_factory_max_efficiency_factor": 0.10,
    "artillery_attack_factor": 0.10, "tank_attack_factor": 0.10,
}
HEAVY_EXTRA = {
    "ace_generation_chance_factor": 0.50, "supply_consumption_factor": -0.20,
    "fuel_gain_factor": 0.25, "volunteer_factor": 0.25, "compliance_gain_factor": 0.25,
    "command_power_gain_mult": 0.50, "planning_speed_factor": 0.30,
    "max_planning_factor": 0.20, "industry_air_damage_factor": -0.40,
    "equipment_capture_factor": 0.25, "production_factory_max_efficiency_factor": 0.20,
    "artillery_attack_factor": 0.20, "tank_attack_factor": 0.20,
    "infantry_attack_factor": 0.15,
}

_, b = call("GET", f"/api/projects/{PID}/ideas")
idea_ids = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
print("ideas:", idea_ids)

MEDIUM = dict(BASE_MOD); MEDIUM.update(MEDIUM_EXTRA)
MEDIUM.update({"political_power_factor": 0.30, "consumer_goods_factor": -0.10,
    "research_speed_factor": 0.20, "production_speed_factor": 0.20,
    "building_speed_factor": 0.20, "dockyard_speed_factor": 0.20,
    "repair_speed_factor": 0.15, "industrial_capacity_factory": 4,
    "resource_gain_factor": 0.20, "army_attack_factor": 0.10,
    "army_defence_factor": 0.10, "army_org_factor": 0.15, "army_morale_factor": 0.15,
    "training_time_factor": -0.20, "experience_gain_army": 0.20,
    "experience_gain_navy": 0.20, "experience_gain_air": 0.20,
    "recruitable_population_factor": 0.10, "land_reinforce_rate": 0.10,
    "navy_attack_factor": 0.10, "navy_defence_factor": 0.10,
    "naval_speed_factor": 0.10, "naval_max_range_factor": 0.10,
    "air_attack_factor": 0.10, "air_defence_factor": 0.10,
    "air_agility_factor": 0.10, "air_bombing_factor": 0.10,
    "justify_war_goal_time": -0.20})
HEAVY = dict(MEDIUM); HEAVY.update(HEAVY_EXTRA)
HEAVY.update({"political_power_factor": 1.00, "stability_factor": 0.20, "war_support_factor": 0.20,
    "consumer_goods_factor": -0.15, "research_speed_factor": 0.50,
    "production_speed_factor": 0.40, "building_speed_factor": 0.40,
    "dockyard_speed_factor": 0.40, "repair_speed_factor": 0.30,
    "industrial_capacity_factory": 8, "resource_gain_factor": 0.40,
    "army_attack_factor": 0.20, "army_defence_factor": 0.20,
    "army_org_factor": 0.25, "army_morale_factor": 0.25,
    "training_time_factor": -0.40, "experience_gain_army": 0.50,
    "experience_gain_navy": 0.50, "experience_gain_air": 0.50,
    "recruitable_population_factor": 0.15, "conscription": 0.05, "land_reinforce_rate": 0.20,
    "navy_attack_factor": 0.20, "navy_defence_factor": 0.20,
    "naval_speed_factor": 0.15, "naval_max_range_factor": 0.15,
    "air_attack_factor": 0.20, "air_defence_factor": 0.20,
    "air_agility_factor": 0.20, "air_bombing_factor": 0.20,
    "justify_war_goal_time": -0.40})

mods = {
    "player_assist_light_idea": dict(BASE_MOD, **LIGHT_EXTRA),
    "player_assist_medium_idea": MEDIUM,
    "player_assist_heavy_idea": HEAVY,
}
for iid, mod in mods.items():
    s, b = call("PUT", f"/api/projects/{PID}/ideas/{idea_ids[iid]}", {"modifier": mod})
    print(f"PUT idea {iid} ({len(mod)} modifiers) ->", s, (str(b)[:300] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:130])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint/tree-validation ->", s, json.dumps(b, ensure_ascii=False)[:300] if isinstance(b, (dict, list)) else b)

# 导出 + 安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\游戏体验增强_v3.zip", "wb") as f:
    f.write(data)
z = zipfile.ZipFile(io.BytesIO(data))
z.extractall(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
shutil.copy(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008.mod", MODDIR)
if os.path.isdir(os.path.join(MODDIR, "mod_2008")):
    shutil.rmtree(os.path.join(MODDIR, "mod_2008"))
shutil.copytree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008", os.path.join(MODDIR, "mod_2008"))
shutil.rmtree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
print("installed v3 to", MODDIR)
print("\nDONE")
