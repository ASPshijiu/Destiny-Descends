# -*- coding: utf-8 -*-
"""天命降临 v14：资源采购改一次性（地图选州 +100 产量，非持续）；精神描述补充建造速度"""
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
        x = urllib.request.urlopen(r, timeout=90)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

RES = {
    "steel": ("钢", "Steel", "steel"),
    "aluminium": ("铝", "Aluminium", "aluminium"),
    "tungsten": ("钨", "Tungsten", "tungsten"),
    "chromium": ("铬", "Chromium", "chromium"),
    "oil": ("石油", "Oil", "oil"),
    "rubber": ("橡胶", "Rubber", "rubber"),
}

# 1. 决议改 state_target 一次性
_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for res, (nz, ne, rtype) in RES.items():
    did = f"qin_buy_{res}"
    if did not in dec_ids:
        continue
    body = {
        "state_target": True,
        "state_target_trigger": "is_owned_by = ROOT",
        "complete_effect": f"add_resource = {{ type = {rtype} amount = 100 }}",
        "desc_en": f"Spend 20 PP: select a controlled state, it gains +100 {ne} permanently.",
        "desc_zh": f"花费 20 政治点，选择一个已控制的州，该州永久获得 +100 {nz}。",
    }
    s, b2 = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids[did]}", body)
    print(f"PUT {did} state_target ->", s, (str(b2)[:150] if s >= 300 else ""))

# 2. 删除持续资源精神
_, b = call("GET", f"/api/projects/{PID}/ideas")
idea_ids = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for res in RES:
    iid = f"qin_res_{res}"
    if iid in idea_ids:
        s, b2 = call("DELETE", f"/api/projects/{PID}/ideas/{idea_ids[iid]}")
        print(f"DELETE {iid} ->", s)

# 3. 三档精神 desc 补充（提到建造速度）
DESC = {
    "player_assist_light_idea": ("天命初醒：稳定、科研、工业、建造与三军全方位轻度增益。",
        "Destiny Awakening: light all-around bonuses in stability, research, industry, construction and the armed forces."),
    "player_assist_medium_idea": ("天命加身：稳定、科研、工业、建造与三军全方位强力增益。",
        "Destiny Embodied: powerful all-around bonuses in stability, research, industry, construction and the armed forces."),
    "player_assist_heavy_idea": ("天命之主：执掌天命，国家全维度获得无上增益（含建造速度）。",
        "Lord of Destiny: supreme all-around bonuses across every dimension, including construction speed."),
}
for iid, (dz, de) in DESC.items():
    if iid in idea_ids:
        s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{idea_ids[iid]}", {"desc_en": de, "desc_zh": dz})
        print(f"PUT {iid} desc ->", s, (str(b2)[:100] if s >= 300 else ""))

# 4. 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea", "decision")) if isinstance(b, dict) else "?")

# 5. 导出安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v14.zip", "wb") as f:
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
