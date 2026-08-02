# -*- coding: utf-8 -*-
"""天命降临 v10：天命设计局——一键按现有科技自动设计全部装备（含自行火炮/坦歼/防空车/战巡）"""
import json, os, sys, urllib.request, urllib.error, zipfile, shutil, io
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008
CAT_ID = 23220
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

# ---------- 变体定义：(变体名, 科技, 类型, modules dict) ----------
VARIANTS = [
    # ===== 坦克家族 =====
    ("天命·轻型坦克", "gwtank_chassis", "light_tank_chassis_0",
     {"turret_type_slot": "tank_light_one_man_tank_turret", "main_armament_slot": "tank_small_cannon",
      "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
      "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"}),
    ("天命·中型坦克", "basic_medium_tank_chassis", "medium_tank_chassis_0",
     {"turret_type_slot": "tank_medium_one_man_tank_turret", "main_armament_slot": "tank_medium_cannon",
      "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
      "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"}),
    ("天命·重型坦克", "basic_heavy_tank_chassis", "heavy_tank_chassis_0",
     {"turret_type_slot": "tank_heavy_two_man_tank_turret", "main_armament_slot": "tank_heavy_cannon",
      "suspension_type_slot": "tank_torsion_bar_suspension", "armor_type_slot": "tank_riveted_armor",
      "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"}),
    ("天命·自行火炮", "basic_medium_tank_chassis", "medium_tank_artillery_chassis_0",
     {"turret_type_slot": "tank_medium_fixed_superstructure_turret", "main_armament_slot": "tank_medium_howitzer",
      "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
      "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"}),
    ("天命·坦克歼击车", "basic_medium_tank_chassis", "medium_tank_destroyer_chassis_0",
     {"turret_type_slot": "tank_medium_fixed_superstructure_turret", "main_armament_slot": "tank_high_velocity_cannon",
      "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
      "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"}),
    ("天命·防空坦克", "basic_medium_tank_chassis", "medium_tank_aa_chassis_0",
     {"turret_type_slot": "tank_medium_fixed_superstructure_turret", "main_armament_slot": "tank_anti_air_cannon",
      "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
      "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"}),
    # ===== 飞机家族 =====
    ("天命·战斗机", "iw_small_airframe", "small_plane_airframe_0",
     {"fixed_main_weapon_slot": "light_mg_2x", "fixed_auxiliary_weapon_slot_1": "empty",
      "engine_type_slot": "engine_1_1x", "special_type_slot_1": "empty"}),
    ("天命·对地攻击机", "iw_small_airframe", "small_plane_cas_airframe_0",
     {"fixed_main_weapon_slot": "bomb_locks", "engine_type_slot": "engine_1_1x",
      "special_type_slot_1": "armor_plate_small"}),
    ("天命·海军轰炸机", "iw_small_airframe", "small_plane_naval_bomber_airframe_0",
     {"fixed_main_weapon_slot": "torpedo_mounting", "engine_type_slot": "engine_1_1x",
      "special_type_slot_1": "empty"}),
    ("天命·战术轰炸机", "early_bomber", "medium_plane_airframe_0",
     {"fixed_main_weapon_slot": "medium_bomb_bay", "engine_type_slot": "engine_2_2x",
      "special_type_slot_1": "empty"}),
    ("天命·战略轰炸机", "strategic_bomber1", "large_plane_airframe_0",
     {"fixed_main_weapon_slot": "large_bomb_bay", "engine_type_slot": "engine_4_2x",
      "special_type_slot_1": "empty"}),
    ("天命·重型战斗机", "heavy_fighter1", "medium_plane_fighter_airframe",
     {"fixed_main_weapon_slot": "heavy_mg_2x", "engine_type_slot": "engine_2_2x",
      "special_type_slot_1": "empty"}),
    # ===== 舰船家族 =====
    ("天命·驱逐舰", "early_ship_hull_light", "ship_hull_light_1",
     {"fixed_ship_battery_slot": "ship_light_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
      "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
      "fixed_ship_torpedo_slot": "ship_torpedo_1", "fixed_ship_engine_slot": "light_ship_engine_1",
      "mid_1_custom_slot": "empty", "rear_1_custom_slot": "empty"}),
    ("天命·轻型巡洋舰", "early_ship_hull_cruiser", "ship_hull_cruiser_1",
     {"fixed_ship_battery_slot": "ship_light_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
      "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
      "fixed_ship_engine_slot": "cruiser_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
      "fixed_ship_armor_slot": "ship_armor_cruiser_1"}),
    ("天命·重型巡洋舰", "early_ship_hull_cruiser", "heavy_cruiser_1",
     {"fixed_ship_battery_slot": "ship_light_medium_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
      "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
      "fixed_ship_engine_slot": "cruiser_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
      "fixed_ship_armor_slot": "ship_armor_cruiser_1"}),
    ("天命·战列舰", "early_ship_hull_heavy", "ship_hull_heavy_1",
     {"fixed_ship_battery_slot": "ship_heavy_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
      "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
      "fixed_ship_engine_slot": "heavy_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
      "fixed_ship_armor_slot": "ship_armor_bb_1"}),
    ("天命·战列巡洋舰", "early_ship_hull_heavy", "ship_hull_heavy_1",
     {"fixed_ship_battery_slot": "ship_heavy_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
      "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
      "fixed_ship_engine_slot": "heavy_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
      "fixed_ship_armor_slot": "ship_armor_bc_1"}),
    ("天命·航空母舰", "basic_ship_hull_carrier", "ship_hull_carrier_1",
     {"fixed_ship_deck_slot_1": "ship_deck_space", "fixed_ship_deck_slot_2": "ship_deck_space",
      "fixed_ship_anti_air_slot": "ship_anti_air_1", "fixed_ship_radar_slot": "empty",
      "fixed_ship_engine_slot": "carrier_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
      "fixed_ship_armor_slot": "ship_armor_carrier_deck"}),
    ("天命·潜艇", "early_ship_hull_submarine", "ship_hull_submarine_1",
     {"fixed_ship_torpedo_slot": "ship_torpedo_sub_1", "fixed_ship_engine_slot": "sub_ship_engine_1",
      "rear_1_custom_slot": "empty"}),
]

# 生成 effect：每个变体 if 科技链
def fmt_variant(name, tech, etype, mods):
    lines = [f"\tif = {{", f"\t\tlimit = {{ has_tech = {tech} }}",
             f"\t\tcreate_equipment_variant = {{", f"\t\t\tname = \"{name}\"",
             f"\t\t\ttype = {etype}", "\t\t\tmodules = {"]
    for slot, mod in mods.items():
        lines.append(f"\t\t\t\t{slot} = {mod}")
    lines += ["\t\t\t}", "\t\t}", "\t}"]
    return "\n".join(lines)

effect = "\n".join(fmt_variant(n, t, e, m) for n, t, e, m in VARIANTS)
print("effect lines:", len(effect.splitlines()), "| variants:", len(VARIANTS))

# 决议「天命设计局」
s, b = call("POST", f"/api/projects/{PID}/decisions", {
    "category_id": CAT_ID,
    "decision_id": "player_assist_design",
    "name_en": "Destiny Design Bureau", "name_zh": "天命设计局",
    "desc_en": "Auto-design the full arsenal from your researched technologies: tanks, SPGs, tank destroyers, AA tanks, aircraft and warships — all per vanilla stats.",
    "desc_zh": "根据已研发科技一键自动设计全套装备：坦克、自行火炮、坦克歼击车、防空坦克、各型飞机与舰船——数值均按原版标准。",
    "cost": 200,
    "allowed": "is_ai = no",
    "visible": "",
    "complete_effect": effect,
    "fire_only_once": True,
})
print("POST decision player_assist_design ->", s, (str(b)[:200] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:160])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s)
if isinstance(b, dict):
    issues = [(k, it.get("level"), it.get("msg")) for k in ("decision", "idea", "focus", "event") for it in b.get(k, [])]
    print("lint issues:", len(issues))
    for k, lv, msg in issues[:20]:
        print(f"  [{k}] {lv}: {str(msg)[:140]}")

# 导出安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v10.zip", "wb") as f:
    f.write(data)
z = zipfile.ZipFile(io.BytesIO(data))
names = z.namelist()
mod_folder = [n.split("/")[0] for n in names if "/" in n][0]
mod_file = [n for n in names if n.endswith(".mod")][0]
tmp = r"C:\Users\xw130\Desktop\hoi4\_tm_install"
z.extractall(tmp)
shutil.copy(os.path.join(tmp, mod_file), MODDIR)
dst = os.path.join(MODDIR, mod_folder)
if os.path.isdir(dst):
    shutil.rmtree(dst)
shutil.copytree(os.path.join(tmp, mod_folder), dst)
shutil.rmtree(tmp)
print("installed", mod_folder)
