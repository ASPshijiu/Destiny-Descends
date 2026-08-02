# -*- coding: utf-8 -*-
"""天命降临 v9：合并巧克力机制——天命军工制造商（MIO）+ 解锁决议"""
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

# ---------- 1. 天命军工制造商（4 个组织，仿巧克力机制）----------
def mio(org, etype, cats, trait_name, ic, prod_cap, prod_cost, res_need, conv, rbonus):
    return f"""{org} = {{
\ticon = GFX_idea_qin_mio
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
\t\t{etype}
\t}}
\tresearch_categories = {{ {cats} }}
\tinitial_trait = {{
\t\tname = {trait_name}
\t\tequipment_bonus = {{
\t\t\tbuild_cost_ic = {ic}
\t\t}}
\t\tproduction_bonus = {{
\t\t\tproduction_capacity_factor = {prod_cap}
\t\t\tproduction_efficiency_cap_factor = {prod_cap}
\t\t\tproduction_cost_factor = {prod_cost}
\t\t\tproduction_efficiency_gain_factor = {prod_cap}
\t\t\tproduction_resource_need_factor = {res_need}
\t\t\tproduction_conversion_speed_factor = {conv}
\t\t}}
\t\torganization_modifier = {{
\t\t\tmilitary_industrial_organization_research_bonus = {rbonus}
\t\t\tmilitary_industrial_organization_design_team_assign_cost = -1.0
\t\t\tmilitary_industrial_organization_design_team_change_cost = -1.0
\t\t}}
\t}}
}}
"""

mio_text = "#### 天命军工：步兵武器 ####\n" + mio(
    "Qin_imperial_infantry", "infantry_equipment", "infantry_weapons",
    "qin_mio_infantry", -0.15, 0.15, -0.15, -0.25, 0.5, 0.3)
mio_text += "\n#### 天命军工：支援装备 ####\n" + mio(
    "Qin_imperial_support", "support_equipment", "support",
    "qin_mio_support", -0.15, 0.15, -0.15, -0.25, 0.5, 0.3)
mio_text += "\n#### 天命军工：装甲兵工厂 ####\n" + mio(
    "Qin_imperial_armor", "tanks", "armor",
    "qin_mio_armor", -0.15, 0.15, -0.15, -0.25, 0.5, 0.3)
mio_text += "\n#### 天命军工：航空工业 ####\n" + mio(
    "Qin_imperial_aircraft", "planes", "aircraft",
    "qin_mio_aircraft", -0.15, 0.15, -0.15, -0.25, 0.5, 0.3)
mio_text += "\n#### 天命军工：海军船坞 ####\n" + mio(
    "Qin_imperial_navy", "ships", "navy",
    "qin_mio_navy", -0.15, 0.15, -0.15, -0.25, 0.5, 0.3)

s, b = call("POST", f"/api/projects/{PID}/raw-files", {
    "dest_path": "common/military_industrial_organization/organizations/qin_mio.txt",
    "content": mio_text,
})
print("upload qin_mio.txt ->", s, (str(b)[:200] if s >= 300 else ""))

# 制造商名称/特质 loc（raw-files）
loc_en = ("l_english:\n"
          " Qin_imperial_infantry: \"Qin Imperial Ordnance\"\n"
          " Qin_imperial_support: \"Qin Imperial Support Works\"\n"
          " Qin_imperial_armor: \"Qin Imperial Armor Works\"\n"
          " Qin_imperial_aircraft: \"Qin Imperial Aviation\"\n"
          " Qin_imperial_navy: \"Qin Imperial Shipyards\"\n"
          " qin_mio_infantry: \"Mandate of Heaven Arsenal\"\n"
          " qin_mio_support: \"Mandate of Heaven Support\"\n"
          " qin_mio_armor: \"Mandate of Heaven Armor\"\n"
          " qin_mio_aircraft: \"Mandate of Heaven Aviation\"\n"
          " qin_mio_navy: \"Mandate of Heaven Navy\"\n")
loc_zh = ("l_simp_chinese:\n"
          " Qin_imperial_infantry: \"天命军工·步兵军械\"\n"
          " Qin_imperial_support: \"天命军工·支援装备\"\n"
          " Qin_imperial_armor: \"天命军工·装甲兵工厂\"\n"
          " Qin_imperial_aircraft: \"天命军工·航空工业\"\n"
          " Qin_imperial_navy: \"天命军工·海军船坞\"\n"
          " qin_mio_infantry: \"天命军械\"\n"
          " qin_mio_support: \"天命支援\"\n"
          " qin_mio_armor: \"天命装甲\"\n"
          " qin_mio_aircraft: \"天命航空\"\n"
          " qin_mio_navy: \"天命船坞\"\n")
for dest, content in [("localisation/english/qin_mio_l_english.yml", loc_en),
                      ("localisation/simp_chinese/qin_mio_l_simp_chinese.yml", loc_zh)]:
    _, b = call("GET", f"/api/projects/{PID}/raw-files")
    old = None
    if isinstance(b, list):
        for f in b:
            if f.get("dest_path") == dest:
                old = f.get("id")
    if old:
        call("DELETE", f"/api/projects/{PID}/raw-files/{old}")
    s, b = call("POST", f"/api/projects/{PID}/raw-files", {"dest_path": dest, "content": content})
    print(f"upload loc {dest} ->", s, (str(b)[:150] if s >= 300 else ""))

# ---------- 2. 解锁决议「天命军工」----------
s, b = call("POST", f"/api/projects/{PID}/decisions", {
    "category_id": CAT_ID,
    "decision_id": "player_assist_mio",
    "name_en": "Unlock Destiny War Industry", "name_zh": "天命军工",
    "desc_en": "Establish the Mandate of Heaven war industry: imperial ordnance, armor, aviation and shipyards, blessed by destiny.",
    "desc_zh": "建立受天命庇佑的军工体系：天命军械、装甲、航空与船坞——生产与装备皆获神助。",
    "cost": 300,
    "allowed": "is_ai = no",
    "visible": "",
    "complete_effect": "set_country_flag = qin_mio_unlocked\nadd_political_power = -300",
    "fire_only_once": True,
})
print("POST decision player_assist_mio ->", s, (str(b)[:200] if s >= 300 else ""))

# ---------- 3. 校验 ----------
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:160])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s)
if isinstance(b, dict):
    n = sum(len(b.get(k, [])) for k in ("idea", "focus", "event", "decision"))
    print("lint issues:", n)

# ---------- 4. 导出安装 ----------
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v9.zip", "wb") as f:
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
for n in sorted(names):
    if "mio" in n or "military_industrial" in n:
        print("  mio file:", n)
