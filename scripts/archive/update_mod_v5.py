# -*- coding: utf-8 -*-
"""v5：全套天命系命名（mod/分类/决议/精神，中英双语）。含校验/导出/安装"""
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

# 1. 项目名
s, b = call("PUT", f"/api/projects/{PID}", {"name": "天命降临"})
print("PUT project name ->", s, (str(b)[:120] if s >= 300 else ""))

# 2. 分类
_, b = call("GET", f"/api/projects/{PID}/decisions/categories")
cat_id = b[0]["id"] if isinstance(b, list) and b else None
s, b = call("PUT", f"/api/projects/{PID}/decisions/categories/{cat_id}", {
    "name_en": "Hall of Destiny", "name_zh": "天命帷幄",
    "desc_en": "Hold the mandate of heaven and bless the nation.",
    "desc_zh": "执掌天命，恩泽万民，护佑社稷。",
})
print("PUT category ->", s, (str(b)[:120] if s >= 300 else ""))

# 3. 决议
_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
NAMES = {
    "player_assist_light": ("天命初醒", "Destiny Awakening",
        "天命初醒，国运渐起——为玩家提供全方位的轻度祝福。",
        "Destiny awakens — grant the player a light set of all-around blessings."),
    "player_assist_medium": ("天命加身", "Destiny Embodied",
        "天命加身，国势日隆——为玩家提供全方位的强力祝福。",
        "Destiny embodied — grant the player a powerful set of all-around blessings."),
    "player_assist_heavy": ("天命之主", "Lord of Destiny",
        "天命之主，君临天下——为玩家提供无上的全面祝福。",
        "Lord of Destiny — grant the player supreme all-around blessings."),
    "player_assist_reset": ("收回天命", "Withdraw Destiny",
        "收回天命祝福，让国家回归凡尘。",
        "Withdraw the destiny blessing and return to normal."),
}
for did, (nz, ne, dz, de) in NAMES.items():
    s, b = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids[did]}", {
        "name_en": ne, "name_zh": nz, "desc_en": de, "desc_zh": dz,
    })
    print(f"PUT decision {did} ->", s, (str(b)[:120] if s >= 300 else ""))

# 4. 民族精神
_, b = call("GET", f"/api/projects/{PID}/ideas")
idea_ids = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
IDEAS = {
    "player_assist_light_idea": ("天命初醒", "Destiny Awakening",
        "天命初醒：稳定、科研、工业与三军全方位轻度增益。",
        "Destiny Awakening: light all-around bonuses in stability, research, industry and the armed forces."),
    "player_assist_medium_idea": ("天命加身", "Destiny Embodied",
        "天命加身：稳定、科研、工业与三军全方位强力增益。",
        "Destiny Embodied: powerful all-around bonuses in stability, research, industry and the armed forces."),
    "player_assist_heavy_idea": ("天命之主", "Lord of Destiny",
        "天命之主：执掌天命，国家全维度获得无上增益。",
        "Lord of Destiny: supreme all-around bonuses across every dimension of the nation."),
}
for iid, (nz, ne, dz, de) in IDEAS.items():
    s, b = call("PUT", f"/api/projects/{PID}/ideas/{idea_ids[iid]}", {
        "name_en": ne, "name_zh": nz, "desc_en": de, "desc_zh": dz,
    })
    print(f"PUT idea {iid} ->", s, (str(b)[:120] if s >= 300 else ""))

# 5. 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:130])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint/tree-validation ->", s, json.dumps(b, ensure_ascii=False)[:200] if isinstance(b, (dict, list)) else b)

# 6. 导出 + 安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v5.zip", "wb") as f:
    f.write(data)
z = zipfile.ZipFile(io.BytesIO(data))
z.extractall(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
shutil.copy(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008.mod", MODDIR)
if os.path.isdir(os.path.join(MODDIR, "mod_2008")):
    shutil.rmtree(os.path.join(MODDIR, "mod_2008"))
shutil.copytree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008", os.path.join(MODDIR, "mod_2008"))
shutil.rmtree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
print("installed v5 to", MODDIR)
print("\nDONE")
