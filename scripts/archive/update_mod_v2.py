# -*- coding: utf-8 -*-
"""v2 重建：选择菜单 + 调整入口（杜绝叠加、可切换）+ 全方位 buff。含校验/导出/安装"""
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

# ---- 1. 拿实体 id ----
_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
print("decisions:", dec_ids)
_, b = call("GET", f"/api/projects/{PID}/ideas")
idea_ids = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
print("ideas:", idea_ids)
_, b = call("GET", f"/api/projects/{PID}/decisions/categories")
cat_id = None
if isinstance(b, list) and b:
    cat_id = b[0]["id"]
    print("category id:", cat_id, b[0].get("category_id"))

L, M, H = ("player_assist_light_idea", "player_assist_medium_idea", "player_assist_heavy_idea")
NOT_ANY = (f"NOT = {{ has_idea = {L} }} NOT = {{ has_idea = {M} }} NOT = {{ has_idea = {H} }}")
HAS_ANY = (f"OR = {{ has_idea = {L} }} OR = {{ has_idea = {M} }} OR = {{ has_idea = {H} }}")

# ---- 2. 档位决议：无精神时可见；点击 = 移除其他两档 + 添加本档 ----
switch_effects = {
    "player_assist_light": f"remove_ideas = {{ {M} {H} }} add_ideas = {L}",
    "player_assist_medium": f"remove_ideas = {{ {L} {H} }} add_ideas = {M}",
    "player_assist_heavy": f"remove_ideas = {{ {L} {M} }} add_ideas = {H}",
}
for did, iid in dec_ids.items():
    s, b = call("PUT", f"/api/projects/{PID}/decisions/{iid}", {
        "visible": NOT_ANY,
        "fire_only_once": False,
        "complete_effect": switch_effects[did],
    })
    print(f"PUT decision {did} ->", s, (str(b)[:200] if s >= 300 else ""))

# ---- 3. 新增「重新调整辅助等级」决议 ----
s, b = call("POST", f"/api/projects/{PID}/decisions", {
    "category_id": cat_id,
    "decision_id": "player_assist_reset",
    "name_en": "Reconfigure Assistance Level",
    "name_zh": "重新调整辅助等级",
    "desc_en": "Clear the current assistance level so a different tier can be chosen.",
    "desc_zh": "清除当前辅助档位，以便重新选择其他等级。",
    "cost": 0,
    "allowed": "is_ai = no",
    "visible": HAS_ANY,
    "complete_effect": f"remove_ideas = {{ {L} {M} {H} }}",
})
print("POST decision player_assist_reset ->", s, (str(b)[:200] if s >= 300 else ""))

# ---- 4. 全方位 buff ----
ALL_BASE = {
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
MEDIUM = dict(ALL_BASE)
MEDIUM.update({
    "political_power_factor": 0.30, "consumer_goods_factor": -0.10,
    "research_speed_factor": 0.20, "production_speed_factor": 0.20,
    "building_speed_factor": 0.20, "dockyard_speed_factor": 0.20,
    "repair_speed_factor": 0.15, "industrial_capacity_factory": 4,
    "resource_gain_factor": 0.20,
    "army_attack_factor": 0.10, "army_defence_factor": 0.10,
    "army_org_factor": 0.15, "army_morale_factor": 0.15,
    "training_time_factor": -0.20,
    "experience_gain_army": 0.20, "experience_gain_navy": 0.20, "experience_gain_air": 0.20,
    "recruitable_population_factor": 0.10, "land_reinforce_rate": 0.10,
    "navy_attack_factor": 0.10, "navy_defence_factor": 0.10,
    "naval_speed_factor": 0.10, "naval_max_range_factor": 0.10,
    "air_attack_factor": 0.10, "air_defence_factor": 0.10,
    "air_agility_factor": 0.10, "air_bombing_factor": 0.10,
    "justify_war_goal_time": -0.20,
})
HEAVY = dict(MEDIUM)
HEAVY.update({
    "political_power_factor": 1.00, "stability_factor": 0.20, "war_support_factor": 0.20,
    "consumer_goods_factor": -0.15, "research_speed_factor": 0.50,
    "production_speed_factor": 0.40, "building_speed_factor": 0.40,
    "dockyard_speed_factor": 0.40, "repair_speed_factor": 0.30,
    "industrial_capacity_factory": 8, "resource_gain_factor": 0.40,
    "army_attack_factor": 0.20, "army_defence_factor": 0.20,
    "army_org_factor": 0.25, "army_morale_factor": 0.25,
    "training_time_factor": -0.40,
    "experience_gain_army": 0.50, "experience_gain_navy": 0.50, "experience_gain_air": 0.50,
    "recruitable_population_factor": 0.15, "conscription": 0.05, "land_reinforce_rate": 0.20,
    "navy_attack_factor": 0.20, "navy_defence_factor": 0.20,
    "naval_speed_factor": 0.15, "naval_max_range_factor": 0.15,
    "air_attack_factor": 0.20, "air_defence_factor": 0.20,
    "air_agility_factor": 0.20, "air_bombing_factor": 0.20,
    "justify_war_goal_time": -0.40,
})
for iid, mod in (("player_assist_light_idea", ALL_BASE),
                 ("player_assist_medium_idea", MEDIUM),
                 ("player_assist_heavy_idea", HEAVY)):
    s, b = call("PUT", f"/api/projects/{PID}/ideas/{idea_ids[iid]}", {"modifier": mod})
    print(f"PUT idea {iid} ->", s, (str(b)[:300] if s >= 300 else ""))

# ---- 5. 校验 ----
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:130])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint/tree-validation ->", s, json.dumps(b, ensure_ascii=False)[:200] if isinstance(b, (dict, list)) else b)

# ---- 6. 导出 + 覆盖安装 ----
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\游戏体验增强_v2.zip", "wb") as f:
    f.write(data)
z = zipfile.ZipFile(io.BytesIO(data))
z.extractall(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
shutil.copy(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008.mod", MODDIR)
if os.path.isdir(os.path.join(MODDIR, "mod_2008")):
    shutil.rmtree(os.path.join(MODDIR, "mod_2008"))
shutil.copytree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008", os.path.join(MODDIR, "mod_2008"))
shutil.rmtree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
print("installed v2 to", MODDIR)
print("\nDONE")
