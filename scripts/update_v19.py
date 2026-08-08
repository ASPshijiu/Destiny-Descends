# -*- coding: utf-8 -*-
"""天命降临 v19：资源采购改随机核心州（免地图选州，不卡）"""
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

RES = {"steel": ("钢", "Steel", "steel"), "aluminium": ("铝", "Aluminium", "aluminium"),
       "tungsten": ("钨", "Tungsten", "tungsten"), "chromium": ("铬", "Chromium", "chromium"),
       "oil": ("石油", "Oil", "oil"), "rubber": ("橡胶", "Rubber", "rubber")}

_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
for res, (nz, ne, rtype) in RES.items():
    did = f"qin_buy_{res}"
    eff = (f"random_state = {{ limit = {{ is_owned_by = ROOT is_core_of = ROOT }} "
           f"add_resource = {{ type = {rtype} amount = 100 }} }}")
    body = {
        "state_target": "",
        "target_trigger": "",
        "complete_effect": eff,
        "desc_en": f"Spend 20 PP: a random owned core state gains +100 {ne} permanently.",
        "desc_zh": f"花费 20 政治点，随机一个本国核心州永久获得 +100 {nz}。",
    }
    s, b2 = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids[did]}", body)
    print(f"PUT {did} ->", s, (str(b2)[:120] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("decision",)) if isinstance(b, dict) else "?")
