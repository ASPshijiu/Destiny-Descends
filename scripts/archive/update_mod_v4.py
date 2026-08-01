# -*- coding: utf-8 -*-
"""v4：档位决议常驻可随时切换 + 「关闭辅助系统」决议。含校验/导出/安装"""
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

_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
print("decisions:", dec_ids)

# 1. 三个档位决议：常驻可见（visible 置空），切换逻辑（remove 其他 + add 自己）不变
for did in ("player_assist_light", "player_assist_medium", "player_assist_heavy"):
    s, b = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids[did]}", {"visible": ""})
    print(f"PUT {did} visible=常驻 ->", s, (str(b)[:150] if s >= 300 else ""))

# 2. 「重新调整辅助等级」→ 改名为「关闭辅助系统」（功能：清空当前精神）
s, b = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids['player_assist_reset']}", {
    "name_en": "Close Assistance System",
    "name_zh": "关闭辅助系统",
    "desc_en": "Remove the current assistance level and return to normal.",
    "desc_zh": "移除当前辅助档位，恢复正常状态。",
})
print("PUT reset -> 关闭辅助系统 ->", s, (str(b)[:150] if s >= 300 else ""))

# 3. 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:130])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint/tree-validation ->", s, json.dumps(b, ensure_ascii=False)[:200] if isinstance(b, (dict, list)) else b)

# 4. 导出 + 安装
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN)
r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
data = urllib.request.urlopen(r, timeout=120).read()
print("\nexport bytes:", len(data))
with open(r"C:\Users\xw130\Desktop\hoi4\游戏体验增强_v4.zip", "wb") as f:
    f.write(data)
z = zipfile.ZipFile(io.BytesIO(data))
z.extractall(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
shutil.copy(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008.mod", MODDIR)
if os.path.isdir(os.path.join(MODDIR, "mod_2008")):
    shutil.rmtree(os.path.join(MODDIR, "mod_2008"))
shutil.copytree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp\mod_2008", os.path.join(MODDIR, "mod_2008"))
shutil.rmtree(r"C:\Users\xw130\Desktop\hoi4\_install_tmp")
print("installed v4 to", MODDIR)
print("\nDONE")
