# -*- coding: utf-8 -*-
"""天命降临 v18：修 is_ai 位置（allowed→available）+ 资源采购 target_trigger"""
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

# 1. 所有决议：allowed is_ai → available
_, b = call("GET", f"/api/projects/{PID}/decisions")
decs = b if isinstance(b, list) else []
for d in decs:
    did = d.get("decision_id", "")
    if not (did.startswith("player_assist") or did.startswith("qin_buy")):
        continue
    body = {"allowed": "", "available": "is_ai = no"}
    if did.startswith("qin_buy"):
        body["target_trigger"] = ""  # 去掉无效州限制
    s, b2 = call("PUT", f"/api/projects/{PID}/decisions/{d['id']}", body)
    print(f"PUT {did} ->", s, (str(b2)[:120] if s >= 300 else ""))

# 2. 分类：allowed is_ai 处理（改 visible）
_, b = call("GET", f"/api/projects/{PID}/decisions/categories")
cats = b if isinstance(b, list) else []
for c in cats:
    cid = c.get("category_id", "")
    if cid in ("player_assistance", "qin_resource_bureau"):
        s, b2 = call("PUT", f"/api/projects/{PID}/decisions/categories/{c['id']}",
                     {"allowed": "", "visible": "is_ai = no"})
        print(f"PUT category {cid} ->", s, (str(b2)[:120] if s >= 300 else ""))

# 3. 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("decision",)) if isinstance(b, dict) else "?")
