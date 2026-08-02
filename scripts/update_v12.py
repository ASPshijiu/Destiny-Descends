# -*- coding: utf-8 -*-
"""天命降临 v12：资源采购——5 种资源决议（花 PP 获得持续资源精神，可移除）"""
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

# 1. 分类「资源采购」
s, b = call("POST", f"/api/projects/{PID}/decisions/categories", {
    "category_id": "qin_resource_bureau",
    "name_en": "Resource Procurement", "name_zh": "资源采购",
    "desc_en": "Purchase strategic resources with political power, blessed by destiny.",
    "desc_zh": "以政治点采购战略资源，天命庇佑，货通天下。",
    "allowed": "is_ai = no",
    "priority": 4,
})
print("category ->", s, (str(b)[:150] if s >= 300 else ""))
cat_id = b.get("id") if isinstance(b, dict) else None

# 2. 资源决议 + 精神（5 种资源）
RES = [
    ("steel", "钢", "Steel", "钢材", "Qin Steel", "country_resource_steel", 20),
    ("aluminium", "铝", "Aluminium", "铝土", "Qin Aluminium", "country_resource_aluminium", 20),
    ("tungsten", "钨", "Tungsten", "钨矿", "Qin Tungsten", "country_resource_tungsten", 20),
    ("chromium", "铬", "Chromium", "铬矿", "Qin Chromium", "country_resource_chromium", 20),
    ("oil", "石油", "Oil", "石油", "Qin Oil", "country_resource_oil", 20),
    ("rubber", "橡胶", "Rubber", "橡胶", "Qin Rubber", "country_resource_rubber", 20),
]
for (res, nz, ne, resname, iname, modkey, val) in RES:
    idea_id = f"qin_res_{res}"
    dec_id = f"qin_buy_{res}"
    # 精神
    s, b = call("POST", f"/api/projects/{PID}/ideas", {
        "idea_id": idea_id, "idea_type": "country",
        "name_zh": f"天命{resname}供应", "name_en": f"{iname} Supply",
        "desc_zh": f"天命采购的{resname}源源不断送达，每个控制州每月 +{val}。",
        "desc_en": f"Procured by destiny: +{val} {ne} per controlled state each month.",
        "picture": "generic_build_infrastructure",
        "modifier": {modkey: val},
        "auto_attach_on_start": False,
        "removal_cost": 100,
    })
    print(f"idea {idea_id} ->", s, (str(b)[:120] if s >= 300 else ""))
    # 决议
    s, b = call("POST", f"/api/projects/{PID}/decisions", {
        "category_id": cat_id,
        "decision_id": dec_id,
        "name_en": f"Purchase {ne}", "name_zh": f"采购{resname}",
        "desc_en": f"Spend 100 political power to gain +{val} {ne} per state each month.",
        "desc_zh": f"花费 100 政治点，每个控制州每月获得 +{val} {resname}。",
        "cost": 100,
        "allowed": "is_ai = no",
        "visible": f"NOT = {{ has_idea = {idea_id} }}",
        "complete_effect": f"add_ideas = {idea_id}",
    })
    print(f"decision {dec_id} ->", s, (str(b)[:120] if s >= 300 else ""))

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
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v12.zip", "wb") as f:
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
