# -*- coding: utf-8 -*-
"""天命降临 v25：删除天命军工 + 天命设计局"""
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

# 1. 删除决议：天命军工 + 天命设计局
_, b = call("GET", f"/api/projects/{PID}/decisions")
if isinstance(b, list):
    for d in b:
        did = d.get("decision_id", "")
        if did in ("player_assist_mio", "player_assist_design"):
            s = call("DELETE", f"/api/projects/{PID}/decisions/{d['id']}")[0]
            print(f"DELETE decision {did} ->", s)

# 2. 删除 raw 文件：qin_mio + on_actions 设计 + 相关 loc
_, b = call("GET", f"/api/projects/{PID}/raw-files")
if isinstance(b, list):
    for f in b:
        dp = f.get("dest_path", "")
        if any(k in dp for k in ["qin_mio", "qin_designs"]):
            s = call("DELETE", f"/api/projects/{PID}/raw-files/{f['id']}")[0]
            print(f"DELETE raw {dp} ->", s)

# 3. 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
