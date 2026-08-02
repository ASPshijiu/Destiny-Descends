# -*- coding: utf-8 -*-
"""应用 GitHub 最新修正（7687ef3）：负向百分比钳制 -100%、将领等级钳制 5"""
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
    r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
    try:
        x = urllib.request.urlopen(r, timeout=60)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

# 动态解析 idea id
_, b = call("GET", f"/api/projects/{PID}/ideas")
IDEA_IDS = {d["idea_id"]: d["id"] for d in b} if isinstance(b, list) else {}
print("ideas:", IDEA_IDS)

PCT_FLOOR = -1.0
CAPS = {"army_leader_start_level": 5}
fixed = {}
for iid, iint in IDEA_IDS.items():
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    new = {}
    for k, v in cur.items():
        nv = v
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if k in CAPS:
                nv = min(v, CAPS[k])
            elif v < PCT_FLOOR:
                nv = PCT_FLOOR
        if nv != v:
            fixed.setdefault(iid, []).append((k, v, nv))
        new[k] = nv
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": new})
    print(f"PUT {iid} ({len(new)} mods) ->", s, (str(b2)[:120] if s >= 300 else ""))

print("\n=== 钳制修正明细 ===")
for iid, items in fixed.items():
    for k, old, nv in items:
        print(f"  {iid}: {k} {old} -> {nv}")

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:140])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea",)) if isinstance(b, dict) else "?")

# 导出安装
import zipfile, shutil, io
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN); r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
MODDIR = r"C:\Users\xw130\Documents\Paradox Interactive\Hearts of Iron IV\mod"
z = zipfile.ZipFile(io.BytesIO(data)); names = z.namelist()
mod_folder = [n.split("/")[0] for n in names if "/" in n][0]
mod_file = [n for n in names if n.endswith(".mod")][0]
tmp = r"C:\Users\xw130\Desktop\hoi4\_tm_install"
z.extractall(tmp)
shutil.copy(os.path.join(tmp, mod_file), MODDIR)
dst = os.path.join(MODDIR, mod_folder)
if os.path.isdir(dst): shutil.rmtree(dst)
shutil.copytree(os.path.join(tmp, mod_folder), dst)
shutil.rmtree(tmp)
print("\ninstalled", mod_folder, "| bytes:", len(data))
