# -*- coding: utf-8 -*-
"""天命降临 v13：资源采购反过来——cost 20 买每州 +100 资源"""
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

RES = ["steel", "aluminium", "tungsten", "chromium", "oil", "rubber"]

# 1. 决议 cost 20
_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for res in RES:
    did = f"qin_buy_{res}"
    if did in dec_ids:
        s, b2 = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids[did]}", {"cost": 20})
        print(f"PUT {did} cost=20 ->", s, (str(b2)[:100] if s >= 300 else ""))

# 2. 精神 modifier 100 + removal 20
_, b = call("GET", f"/api/projects/{PID}/ideas")
idea_ids = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
MODKEY = {"steel": "country_resource_steel", "aluminium": "country_resource_aluminium",
          "tungsten": "country_resource_tungsten", "chromium": "country_resource_chromium",
          "oil": "country_resource_oil", "rubber": "country_resource_rubber"}
for res in RES:
    iid = f"qin_res_{res}"
    if iid in idea_ids:
        s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{idea_ids[iid]}",
                     {"modifier": {MODKEY[res]: 100}, "removal_cost": 20})
        print(f"PUT {iid} =100 removal=20 ->", s, (str(b2)[:100] if s >= 300 else ""))

# 3. 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:160])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea", "decision")) if isinstance(b, dict) else "?")

# 4. 导出安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v13.zip", "wb") as f:
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
