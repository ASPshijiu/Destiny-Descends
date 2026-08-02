# -*- coding: utf-8 -*-
"""天命降临 v11：整合 5 个将领 mod——技能扩展/特质/槽位/指挥点 defines + 经验维度进精神"""
import json, os, sys, re, shutil, urllib.request, urllib.error, zipfile, io
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008
W = r"D:\Steam\steamapps\workshop\content\394360"
MODDIR = r"C:\Users\xw130\Documents\Paradox Interactive\Hearts of Iron IV\mod"

def call(m, p, body=None):
    d = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(BASE + p, data=d, method=m)
    r.add_header("Content-Type", "application/json; charset=utf-8")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
    try:
        x = urllib.request.urlopen(r, timeout=90)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

def upload_raw(dest, content):
    _, b = call("GET", f"/api/projects/{PID}/raw-files")
    old = None
    if isinstance(b, list):
        for f in b:
            if f.get("dest_path") == dest:
                old = f.get("id")
    if old:
        call("DELETE", f"/api/projects/{PID}/raw-files/{old}")
    s, b = call("POST", f"/api/projects/{PID}/raw-files", {"dest_path": dest, "content": content})
    print(f"  raw {dest} ->", s, (str(b)[:120] if s >= 300 else ""))

# ---------- 1. 将领技能扩展（6 文件合并，60/60/60/60/20/20 级）----------
skill_files = ["99_skills", "99_attack_skills", "99_defense_skills", "99_planning_skills",
               "99_logistics_skills", "99_maneuvering_skills", "99_coordination_skills"]
parts = []
for sf in skill_files:
    p = os.path.join(W, "2785310084", "common", "unit_leader", sf + ".txt")
    if os.path.exists(p):
        parts.append(open(p, encoding="utf-8-sig", errors="replace").read().strip())
skill_content = "\n\n".join(parts)
print("技能内容长度:", len(skill_content))
upload_raw("common/unit_leader/qin_leader_skills.txt", skill_content)

# ---------- 2. defines：指挥点 + 特质槽位 ----------
defines_content = (
    "# 整合自【将领等级上限】【将领特质槽位】\n"
    "NDefines.NCountry.BASE_MAX_COMMAND_POWER = 250\n"
    "NDefines.NCountry.BASE_COMMAND_POWER_GAIN = 0.5\n"
    "NDefines.NMilitary.UNIT_LEADER_TRAIT_SLOT_PER_LEVEL = { 1.0, 1.0, 1.0, 0.0, }\n")
upload_raw("common/defines/qin_leader_defines.lua", defines_content)

# ---------- 3. 将领特质（MOR_traits 内容）----------
traits = open(os.path.join(W, "1967856041", "common", "unit_leader", "MOR_traits.txt"), encoding="utf-8-sig", errors="replace").read()
print("特质内容长度:", len(traits))
upload_raw("common/unit_leader/qin_traits.txt", traits)

# ---------- 4. 特质图标（gfx + interface 注册）----------
icon_dir = os.path.join(W, "1967856041", "gfx", "interface", "teszh")
gfx_files = [f for f in os.listdir(icon_dir) if f.endswith(".png")] if os.path.isdir(icon_dir) else []
print("特质图标数:", len(gfx_files))
# interface gfx 注册文件（原 mod 里的 .gfx 定义）
iface_dir = os.path.join(W, "1967856041", "interface")
iface_files = [f for f in os.listdir(iface_dir) if f.endswith(".gfx")] if os.path.isdir(iface_dir) else []
iface_content = ""
for f in iface_files:
    iface_content += open(os.path.join(iface_dir, f), encoding="utf-8-sig", errors="replace").read() + "\n"
if iface_content:
    upload_raw("interface/qin_traits.gfx", iface_content)
    print("  interface gfx 注册已上传")

# ---------- 5. 经验维度并入三档精神 ----------
_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
EXP = {
    "player_assist_light_idea": {"experience_gain_factor": 0.5, "experience_gain_army_unit_factor": 0.5,
        "experience_gain_navy_unit_factor": 0.5, "air_training_xp_gain_factor": 0.5, "air_mission_xp_gain_factor": 0.5},
    "player_assist_medium_idea": {"experience_gain_factor": 2.0, "experience_gain_army_unit_factor": 2.0,
        "experience_gain_navy_unit_factor": 2.0, "air_training_xp_gain_factor": 2.0, "air_mission_xp_gain_factor": 2.0},
    "player_assist_heavy_idea": {"experience_gain_factor": 5.0, "experience_gain_army_unit_factor": 5.0,
        "experience_gain_navy_unit_factor": 5.0, "air_training_xp_gain_factor": 5.0, "air_mission_xp_gain_factor": 5.0},
}
for iid, iint in IDEA_IDS.items():
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    cur.update(EXP.get(iid, {}))
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": cur})
    print(f"PUT {iid} ({len(cur)} mods) ->", s, (str(b2)[:120] if s >= 300 else ""))

# ---------- 6. 校验 ----------
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:160])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea",)) if isinstance(b, dict) else "?")

# ---------- 7. 导出安装 ----------
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v11.zip", "wb") as f:
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
    if "unit_leader" in n or "qin_leader" in n or "qin_traits" in n:
        print("  ", n)
