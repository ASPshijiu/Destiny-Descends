# -*- coding: utf-8 -*-
"""天命降临 v6：扩展 8 个 buff 维度 + 校验导出安装"""
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

# 8 个新维度（轻/中/重渐进）
NEW = {
    "light": {"intel_network_speed": 0.10, "opinion_gain_mult": 0.10,
              "advisor_cost_factor": -0.10, "army_core_attack_factor": 0.05,
              "army_non_core_attack_factor": 0.05, "equipment_consumption_factor": -0.05,
              "conversion_speed": 0.05, "air_accident_chance_factor": -0.10},
    "medium": {"intel_network_speed": 0.20, "opinion_gain_mult": 0.20,
               "advisor_cost_factor": -0.20, "army_core_attack_factor": 0.10,
               "army_non_core_attack_factor": 0.10, "equipment_consumption_factor": -0.10,
               "conversion_speed": 0.10, "air_accident_chance_factor": -0.20},
    "heavy": {"intel_network_speed": 0.50, "opinion_gain_mult": 0.50,
              "advisor_cost_factor": -0.40, "army_core_attack_factor": 0.20,
              "army_non_core_attack_factor": 0.20, "equipment_consumption_factor": -0.20,
              "conversion_speed": 0.20, "air_accident_chance_factor": -0.40},
}
IDEA_IDS = {"player_assist_light_idea": 369870, "player_assist_medium_idea": 369871, "player_assist_heavy_idea": 369872}

# 获取当前 modifier 并追加
for iid, iint in IDEA_IDS.items():
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    tier = "light" if "light" in iid else ("medium" if "medium" in iid else "heavy")
    merged = dict(cur)
    merged.update(NEW[tier])
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": merged})
    print(f"PUT {iid} ({len(merged)} modifiers) ->", s, (str(b2)[:150] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:140])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s)
if isinstance(b, dict):
    n = sum(len(b.get(k, [])) for k in ("focus", "event", "idea", "decision", "character"))
    print("lint issues:", n)
    for k in ("idea", "focus"):
        for it in b.get(k, []):
            print(f"  [{k}] {it.get('level')}: {str(it.get('msg'))[:120]}")

# 导出 + 安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\天命降临_v6.zip", "wb") as f:
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
# 图标验证
for n in sorted(names):
    if "idea" in n and ("png" in n or "dds" in n):
        print("  icon file:", n)
