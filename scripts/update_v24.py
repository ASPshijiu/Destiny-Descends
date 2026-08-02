# -*- coding: utf-8 -*-
"""天命降临 v24：on_startup 预设基础代设计（玩家开局即有，科技门控自动）"""
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

# 基础代设计（开局预设）：类型名 + 基础 chassis + 基础模块
BASE_MODS = {
    "tank_l": {"turret_type_slot": "tank_light_one_man_tank_turret", "main_armament_slot": "tank_small_cannon",
               "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
               "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"},
    "tank_m": {"turret_type_slot": "tank_medium_one_man_tank_turret", "main_armament_slot": "tank_medium_cannon",
               "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
               "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"},
    "tank_h": {"turret_type_slot": "tank_heavy_two_man_tank_turret", "main_armament_slot": "tank_heavy_cannon",
               "suspension_type_slot": "tank_torsion_bar_suspension", "armor_type_slot": "tank_riveted_armor",
               "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"},
    "tank_fixed": {"turret_type_slot": "tank_medium_fixed_superstructure_turret",
                   "suspension_type_slot": "tank_bogie_suspension", "armor_type_slot": "tank_riveted_armor",
                   "engine_type_slot": "tank_gasoline_engine", "special_type_slot_1": "tank_radio_1"},
    "plane_f": {"fixed_main_weapon_slot": "light_mg_2x", "fixed_auxiliary_weapon_slot_1": "empty",
                "engine_type_slot": "engine_1_1x", "special_type_slot_1": "empty"},
    "plane_cas": {"fixed_main_weapon_slot": "bomb_locks", "engine_type_slot": "engine_1_1x",
                  "special_type_slot_1": "armor_plate_small"},
    "plane_nav": {"fixed_main_weapon_slot": "torpedo_mounting", "engine_type_slot": "engine_1_1x",
                  "special_type_slot_1": "empty"},
    "plane_med": {"fixed_main_weapon_slot": "medium_bomb_bay", "engine_type_slot": "engine_2_2x",
                  "special_type_slot_1": "empty"},
    "plane_large": {"fixed_main_weapon_slot": "large_bomb_bay", "engine_type_slot": "engine_4_2x",
                    "special_type_slot_1": "empty"},
    "plane_hf": {"fixed_main_weapon_slot": "heavy_mg_2x", "engine_type_slot": "engine_2_2x",
                 "special_type_slot_1": "empty"},
    "ship_dd": {"fixed_ship_battery_slot": "ship_light_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
                "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
                "fixed_ship_torpedo_slot": "ship_torpedo_1", "fixed_ship_engine_slot": "light_ship_engine_1",
                "mid_1_custom_slot": "empty", "rear_1_custom_slot": "empty"},
    "ship_cl": {"fixed_ship_battery_slot": "ship_light_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
                "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
                "fixed_ship_engine_slot": "cruiser_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
                "fixed_ship_armor_slot": "ship_armor_cruiser_1"},
    "ship_ca": {"fixed_ship_battery_slot": "ship_light_medium_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
                "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
                "fixed_ship_engine_slot": "cruiser_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
                "fixed_ship_armor_slot": "ship_armor_cruiser_1"},
    "ship_bb": {"fixed_ship_battery_slot": "ship_heavy_battery_1", "fixed_ship_anti_air_slot": "ship_anti_air_1",
                "fixed_ship_fire_control_system_slot": "ship_fire_control_system_0", "fixed_ship_radar_slot": "empty",
                "fixed_ship_engine_slot": "heavy_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
                "fixed_ship_armor_slot": "ship_armor_bb_1"},
    "ship_cv": {"fixed_ship_deck_slot_1": "ship_deck_space", "fixed_ship_deck_slot_2": "ship_deck_space",
                "fixed_ship_anti_air_slot": "ship_anti_air_1", "fixed_ship_radar_slot": "empty",
                "fixed_ship_engine_slot": "carrier_ship_engine_1", "fixed_ship_secondaries_slot": "ship_secondaries_1",
                "fixed_ship_armor_slot": "ship_armor_carrier_deck"},
    "ship_ss": {"fixed_ship_torpedo_slot": "ship_torpedo_sub_1", "fixed_ship_engine_slot": "sub_ship_engine_1",
                "rear_1_custom_slot": "empty"},
}

# 基础代设计清单：(名称, 模块组, chassis type)
BASIC = [
    ("天命·轻型坦克", "tank_l", "light_tank_chassis_0"),
    ("天命·中型坦克", "tank_m", "medium_tank_chassis_0"),
    ("天命·重型坦克", "tank_h", "heavy_tank_chassis_0"),
    ("天命·自行火炮", "tank_fixed", "medium_tank_artillery_chassis_1"),
    ("天命·坦克歼击车", "tank_fixed", "medium_tank_destroyer_chassis_1"),
    ("天命·防空坦克", "tank_fixed", "medium_tank_aa_chassis_1"),
    ("天命·战斗机", "plane_f", "small_plane_airframe_0"),
    ("天命·对地攻击机", "plane_cas", "small_plane_cas_airframe_1"),
    ("天命·海军轰炸机", "plane_nav", "small_plane_naval_bomber_airframe_1"),
    ("天命·战术轰炸机", "plane_med", "medium_plane_airframe_0"),
    ("天命·战略轰炸机", "plane_large", "large_plane_airframe_0"),
    ("天命·重型战斗机", "plane_hf", "medium_plane_fighter_airframe_1"),
    ("天命·驱逐舰", "ship_dd", "ship_hull_light_1"),
    ("天命·轻型巡洋舰", "ship_cl", "ship_hull_cruiser_1"),
    ("天命·重型巡洋舰", "ship_ca", "heavy_cruiser_1"),
    ("天命·战列舰", "ship_bb", "ship_hull_heavy_1"),
    ("天命·航空母舰", "ship_cv", "ship_hull_carrier_1"),
    ("天命·潜艇", "ship_ss", "ship_hull_submarine_1"),
]

def fmt_variant(name, etype, mods):
    lines = ["create_equipment_variant = {", f' name = "{name}"', f" type = {etype}", " modules = {"]
    for slot, mod in mods.items():
        lines.append(f"  {slot} = {mod}")
    lines += [" }", "}"]
    return "\n".join(lines)

creates = "\n".join(fmt_variant(n, t, BASE_MODS[mk]) for n, mk, t in BASIC)
on_actions = f"""on_actions = {{
\ton_startup = {{
\t\teffect = {{
\t\t\tif = {{
\t\t\t\tlimit = {{ is_ai = no }}
{creates}
\t\t\t}}
\t\t}}
\t}}
}}
"""
print("on_actions 长度:", len(on_actions))

# 上传 raw（删旧+传新）
dest = "common/on_actions/qin_designs.txt"
_, b = call("GET", f"/api/projects/{PID}/raw-files")
old = None
if isinstance(b, list):
    for f in b:
        if f.get("dest_path") == dest:
            old = f.get("id")
if old:
    call("DELETE", f"/api/projects/{PID}/raw-files/{old}")
s, b = call("POST", f"/api/projects/{PID}/raw-files", {"dest_path": dest, "content": on_actions})
print("upload on_actions ->", s, (str(b)[:150] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
