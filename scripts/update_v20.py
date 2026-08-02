# -*- coding: utf-8 -*-
"""天命降临 v20：重构天命军工 MIO（贴近原版格式：mio_cat_eq 分类 + 删无效图标）"""
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

def mio(org, eq_cats, rc, trait_name):
    rc_line = f"\tresearch_categories = {{ {rc} }}\n" if rc else ""
    return f"""{org} = {{
\tallowed = {{
\t\thas_dlc = "Arms Against Tyranny"
\t}}
\tavailable = {{
\t\tFROM = {{ has_country_flag = qin_mio_unlocked }}
\t}}
\tai_will_do = {{
\t\tbase = 0
\t}}
\tequipment_type = {{
\t\t{eq_cats}
\t}}
{rc_line}\tinitial_trait = {{
\t\tname = {trait_name}
\t\tequipment_bonus = {{
\t\t\tbuild_cost_ic = -0.15
\t\t}}
\t\tproduction_bonus = {{
\t\t\tproduction_capacity_factor = 0.15
\t\t\tproduction_efficiency_cap_factor = 0.15
\t\t\tproduction_cost_factor = -0.15
\t\t\tproduction_efficiency_gain_factor = 0.15
\t\t\tproduction_resource_need_factor = -0.25
\t\t\tproduction_conversion_speed_factor = 0.5
\t\t}}
\t\torganization_modifier = {{
\t\t\tmilitary_industrial_organization_research_bonus = 0.3
\t\t\tmilitary_industrial_organization_design_team_assign_cost = -1.0
\t\t\tmilitary_industrial_organization_design_team_change_cost = -1.0
\t\t}}
\t}}
}}
"""

text = "#### 天命军工：步兵与支援 ####\n" + mio(
    "Qin_imperial_infantry", "mio_cat_eq_all_infantry_and_support_equipment", "",
    "qin_mio_infantry")
text += "\n#### 天命军工：装甲兵工厂 ####\n" + mio(
    "Qin_imperial_armor", "mio_cat_eq_all_tanks", "mio_cat_tech_all_armor_and_modules",
    "qin_mio_armor")
text += "\n#### 天命军工：炮兵工厂 ####\n" + mio(
    "Qin_imperial_artillery", "mio_cat_eq_all_artillery", "",
    "qin_mio_artillery")
text += "\n#### 天命军工：航空工业 ####\n" + mio(
    "Qin_imperial_aircraft",
    "mio_cat_eq_all_small_plane mio_cat_eq_all_medium_plane mio_cat_eq_all_large_plane mio_cat_eq_all_cv_aircraft",
    "", "qin_mio_aircraft")
text += "\n#### 天命军工：海军船坞 ####\n" + mio(
    "Qin_imperial_navy",
    "mio_cat_eq_all_destroyer mio_cat_eq_all_cruiser mio_cat_eq_all_battleship mio_cat_eq_all_carrier",
    "mio_cat_tech_all_screen_ship_and_modules", "qin_mio_navy")

# 上传（删旧+传新）
_, b = call("GET", f"/api/projects/{PID}/raw-files")
old = None
if isinstance(b, list):
    for f in b:
        if f.get("dest_path") == "common/military_industrial_organization/organizations/qin_mio.txt":
            old = f.get("id")
if old:
    call("DELETE", f"/api/projects/{PID}/raw-files/{old}")
s, b = call("POST", f"/api/projects/{PID}/raw-files", {
    "dest_path": "common/military_industrial_organization/organizations/qin_mio.txt", "content": text})
print("upload qin_mio.txt ->", s, (str(b)[:150] if s >= 300 else ""))

# loc 补充炮兵组织名
loc_en = "\n Qin_imperial_artillery: \"Qin Imperial Artillery Works\"\n qin_mio_artillery: \"Mandate of Heaven Artillery\"\n"
loc_zh = "\n Qin_imperial_artillery: \"天命军工·炮兵工厂\"\n qin_mio_artillery: \"天命炮兵\"\n"
for dest, content in [("localisation/english/qin_mio_l_english.yml", loc_en),
                      ("localisation/simp_chinese/qin_mio_l_simp_chinese.yml", loc_zh)]:
    _, b = call("GET", f"/api/projects/{PID}/raw-files")
    old = None
    if isinstance(b, list):
        for f in b:
            if f.get("dest_path") == dest:
                old = f.get("id"); cur = f.get("content") or f.get("body")
    if old and cur:
        call("DELETE", f"/api/projects/{PID}/raw-files/{old}")
        s, b = call("POST", f"/api/projects/{PID}/raw-files",
                    {"dest_path": dest, "content": cur + content})
        print(f"update loc {dest} ->", s, (str(b)[:120] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
