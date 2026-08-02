# -*- coding: utf-8 -*-
"""天命降临 v21：资源采购补煤炭"""
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

# 查资源采购分类 id
_, b = call("GET", f"/api/projects/{PID}/decisions/categories")
cat_id = None
if isinstance(b, list):
    for c in b:
        if c.get("category_id") == "qin_resource_bureau":
            cat_id = c.get("id")
print("分类 id:", cat_id)

eff = ("random_state = { limit = { is_owned_by = ROOT is_core = ROOT } "
       "add_resource = { type = coal amount = 100 } }")
s, b = call("POST", f"/api/projects/{PID}/decisions", {
    "category_id": cat_id,
    "decision_id": "qin_buy_coal",
    "name_en": "Purchase Coal", "name_zh": "采购煤炭",
    "desc_en": "Spend 20 PP: a random owned core state gains +100 Coal permanently.",
    "desc_zh": "花费 20 政治点，随机一个本国核心州永久获得 +100 煤炭。",
    "cost": 20,
    "available": "is_ai = no",
    "complete_effect": eff,
})
print("POST qin_buy_coal ->", s, (str(b)[:150] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("decision",)) if isinstance(b, dict) else "?")

# 导出安装
import zipfile, shutil, io
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN); r.add_header("User-Agent", "x")
data = urllib.request.urlopen(r, timeout=120).read()
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v21.zip", "wb") as f: f.write(data)
z = zipfile.ZipFile(io.BytesIO(data)); names = z.namelist()
mod_folder = [n.split("/")[0] for n in names if "/" in n][0]
mod_file = [n for n in names if n.endswith(".mod")][0]
MODDIR = r"C:\Users\xw130\Documents\Paradox Interactive\Hearts of Iron IV\mod"
tmp = r"C:\Users\xw130\Desktop\hoi4\_tm_install"
z.extractall(tmp)
shutil.copy(os.path.join(tmp, mod_file), MODDIR)
dst = os.path.join(MODDIR, mod_folder)
if os.path.isdir(dst): shutil.rmtree(dst)
shutil.copytree(os.path.join(tmp, mod_folder), dst)
shutil.rmtree(tmp)
print("installed", mod_folder, "| bytes:", len(data))
t = open(os.path.join(MODDIR, mod_folder, "common", "decisions", "_UNK.txt"), encoding="utf-8-sig").read()
print("含 coal:", "type = coal" in t, "| 含 qin_buy_coal:", "qin_buy_coal" in t)
