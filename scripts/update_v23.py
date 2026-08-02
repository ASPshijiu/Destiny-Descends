# -*- coding: utf-8 -*-
"""天命降临 v23：天命设计局——可重复点 + 按科技自动生成最高代设计"""
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

# 每类型：变体名基、档位列表 [(科技, chassis type, 序号罗马/数字)]
ROMAN = ["I", "II", "III", "IV", "V"]
# 基础模块组合（沿用 v10 的，按类型）
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

# 类型定义：(名称, 模块组, [(科技, chassis type), ...]) 高→低
TYPES = [
    ("天命·轻型坦克", "tank_l", [("advanced_light_tank_chassis", "light_tank_chassis_3"),
                                   ("improved_light_tank_chassis", "light_tank_chassis_2"),
                                   ("basic_light_tank_chassis", "light_tank_chassis_1"),
                                   ("gwtank_chassis", "light_tank_chassis_0")]),
    ("天命·中型坦克", "tank_m", [("advanced_medium_tank_chassis", "medium_tank_chassis_2"),
                                   ("improved_medium_tank_chassis", "medium_tank_chassis_1"),
                                   ("basic_medium_tank_chassis", "medium_tank_chassis_0")]),
    ("天命·重型坦克", "tank_h", [("advanced_heavy_tank_chassis", "heavy_tank_chassis_2"),
                                   ("improved_heavy_tank_chassis", "heavy_tank_chassis_1"),
                                   ("basic_heavy_tank_chassis", "heavy_tank_chassis_0")]),
    ("天命·自行火炮", "tank_fixed", [("advanced_medium_tank_chassis", "medium_tank_artillery_chassis_2"),
                                       ("improved_medium_tank_chassis", "medium_tank_artillery_chassis_1"),
                                       ("basic_medium_tank_chassis", "medium_tank_artillery_chassis_1")]),
    ("天命·坦克歼击车", "tank_fixed", [("advanced_medium_tank_chassis", "medium_tank_destroyer_chassis_2"),
                                         ("improved_medium_tank_chassis", "medium_tank_destroyer_chassis_1"),
                                         ("basic_medium_tank_chassis", "medium_tank_destroyer_chassis_1")]),
    ("天命·防空坦克", "tank_fixed", [("advanced_medium_tank_chassis", "medium_tank_aa_chassis_2"),
                                       ("improved_medium_tank_chassis", "medium_tank_aa_chassis_1"),
                                       ("basic_medium_tank_chassis", "medium_tank_aa_chassis_1")]),
    ("天命·战斗机", "plane_f", [("advanced_small_airframe", "small_plane_airframe_3"),
                                  ("improved_small_airframe", "small_plane_airframe_2"),
                                  ("basic_small_airframe", "small_plane_airframe_1"),
                                  ("iw_small_airframe", "small_plane_airframe_0")]),
    ("天命·对地攻击机", "plane_cas", [("basic_small_airframe", "small_plane_cas_airframe_1"),
                                        ("iw_small_airframe", "small_plane_cas_airframe_1")]),
    ("天命·海军轰炸机", "plane_nav", [("basic_small_airframe", "small_plane_naval_bomber_airframe_1"),
                                         ("iw_small_airframe", "small_plane_naval_bomber_airframe_1")]),
    ("天命·战术轰炸机", "plane_med", [("advanced_medium_airframe", "medium_plane_airframe_2"),
                                        ("improved_medium_airframe", "medium_plane_airframe_1"),
                                        ("basic_medium_airframe", "medium_plane_airframe_0"),
                                        ("early_bomber", "medium_plane_airframe_0")]),
    ("天命·战略轰炸机", "plane_large", [("advanced_large_airframe", "large_plane_airframe_2"),
                                           ("improved_large_airframe", "large_plane_airframe_1"),
                                           ("basic_large_airframe", "large_plane_airframe_0"),
                                           ("strategic_bomber1", "large_plane_airframe_0")]),
    ("天命·重型战斗机", "plane_hf", [("heavy_fighter1", "medium_plane_fighter_airframe_1")]),
    ("天命·驱逐舰", "ship_dd", [("advanced_ship_hull_light", "ship_hull_light_4"),
                                   ("improved_ship_hull_light", "ship_hull_light_3"),
                                   ("basic_ship_hull_light", "ship_hull_light_2"),
                                   ("early_ship_hull_light", "ship_hull_light_1")]),
    ("天命·轻型巡洋舰", "ship_cl", [("advanced_ship_hull_cruiser", "ship_hull_cruiser_4"),
                                       ("improved_ship_hull_cruiser", "ship_hull_cruiser_3"),
                                       ("basic_ship_hull_cruiser", "ship_hull_cruiser_2"),
                                       ("early_ship_hull_cruiser", "ship_hull_cruiser_1")]),
    ("天命·重型巡洋舰", "ship_ca", [("advanced_ship_hull_cruiser", "heavy_cruiser_4"),
                                       ("improved_ship_hull_cruiser", "heavy_cruiser_3"),
                                       ("basic_ship_hull_cruiser", "heavy_cruiser_2"),
                                       ("early_ship_hull_cruiser", "heavy_cruiser_1")]),
    ("天命·战列舰", "ship_bb", [("advanced_ship_hull_heavy", "ship_hull_heavy_4"),
                                   ("improved_ship_hull_heavy", "ship_hull_heavy_3"),
                                   ("basic_ship_hull_heavy", "ship_hull_heavy_2"),
                                   ("early_ship_hull_heavy", "ship_hull_heavy_1")]),
    ("天命·航空母舰", "ship_cv", [("advanced_ship_hull_carrier", "ship_hull_carrier_4"),
                                     ("improved_ship_hull_carrier", "ship_hull_carrier_3"),
                                     ("basic_ship_hull_carrier", "ship_hull_carrier_2")]),
    ("天命·潜艇", "ship_ss", [("advanced_ship_hull_submarine", "ship_hull_submarine_4"),
                                 ("improved_ship_hull_submarine", "ship_hull_submarine_3"),
                                 ("basic_ship_hull_submarine", "ship_hull_submarine_2"),
                                 ("early_ship_hull_submarine", "ship_hull_submarine_1")]),
]

def fmt_variant(name, etype, mods):
    lines = ["create_equipment_variant = {", f' name = "{name}"', f" type = {etype}", " modules = {"]
    for slot, mod in mods.items():
        lines.append(f"  {slot} = {mod}")
    lines += [" }", "}"]
    return "\n".join(lines)

def build_nested(vname, modkey, tiers):
    """嵌套 if（最高代优先）：生成 else-if 链"""
    mods = BASE_MODS[modkey]
    # 生成从低到高的嵌套（最内层 = 最低代）
    def gen(i):
        tech, etype = tiers[i]
        name = f"{vname}·{ROMAN[len(tiers)-1-i]}"  # 最高代=最后一个序号
        if i == len(tiers) - 1:
            return (f"\tif = {{\n\t\tlimit = {{ has_tech = {tech} }}\n"
                    + fmt_variant(name, etype, mods) + "\n\t}")
        inner = gen(i + 1)
        return (f"\tif = {{\n\t\tlimit = {{ has_tech = {tech} }}\n"
                + fmt_variant(name, etype, mods)
                + f"\n\t\telse = {{\n{inner}\n\t\t}}\n\t}}")
    return gen(0)

blocks = [build_nested(v, mk, t) for v, mk, t in TYPES]
effect = "\n".join(blocks)
print("effect 长度:", len(effect), "| 类型数:", len(TYPES))

# PUT 决议：fire_only_once 去掉 + 新 effect
_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
s, b = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids['player_assist_design']}", {
    "fire_only_once": False,
    "complete_effect": effect,
})
print("PUT player_assist_design ->", s, (str(b)[:150] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("decision",)) if isinstance(b, dict) else "?")
