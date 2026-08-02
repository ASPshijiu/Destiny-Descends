# -*- coding: utf-8 -*-
"""天命降临 v17：修装备设计类型错误（archetype/_0→_1）+ 军工决议重复扣 PP"""
import json, os, sys, re, urllib.request, urllib.error
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

# ---------- 1. 修天命设计局变体类型 ----------
_, b = call("GET", f"/api/projects/{PID}/decisions")
dec_ids = {d["decision_id"]: d["id"] for d in b} if isinstance(b, list) else {}
_, b = call("GET", f"/api/projects/{PID}/decisions/{dec_ids['player_assist_design']}")
eff = (b or {}).get("complete_effect") or ""
print("原 effect 长度:", len(eff))

# 变体块替换（按变体名定位块，块内替换 type 与 limit 科技）
def patch_block(eff, vname, new_type, new_tech=None):
    # 定位变体名出现的 if 块：从 name="vname" 向前找 if = {，向后到该 if 的 }
    idx = eff.find(f'name = "{vname}"')
    if idx < 0:
        print(f"  未找到 {vname}")
        return eff
    start = eff.rfind("\tif = {", 0, idx)
    end = eff.find("\n\t}", idx)
    block = eff[start:end]
    new_block = re.sub(r'type = \S+', f"type = {new_type}", block, count=1)
    if new_tech:
        new_block = re.sub(r'has_tech = \S+', f"has_tech = {new_tech}", new_block, count=1)
    return eff[:start] + new_block + eff[end:]

FIXES = [
    ("天命·自行火炮", "medium_tank_artillery_chassis_1", None),
    ("天命·坦克歼击车", "medium_tank_destroyer_chassis_1", None),
    ("天命·防空坦克", "medium_tank_aa_chassis_1", None),
    ("天命·对地攻击机", "small_plane_cas_airframe_1", "basic_small_airframe"),
    ("天命·海军轰炸机", "small_plane_naval_bomber_airframe_1", "basic_small_airframe"),
    ("天命·重型战斗机", "medium_plane_fighter_airframe_1", None),
]
for vname, ntype, ntech in FIXES:
    before = eff
    eff = patch_block(eff, vname, ntype, ntech)
    print(f"  修正 {vname}: type={ntype}" + (f" tech={ntech}" if ntech else ""))

# 确认无残留 _0 / archetype
left = re.findall(r'type = (medium_tank_(?:artillery|destroyer|aa)_chassis_0|small_plane_(?:cas|naval_bomber)_airframe_0|medium_plane_fighter_airframe\b)', eff)
print("残留错误 type:", left)
s, b = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids['player_assist_design']}", {"complete_effect": eff})
print("PUT player_assist_design ->", s, (str(b)[:150] if s >= 300 else ""))

# ---------- 2. 修军工决议重复扣 PP ----------
_, b = call("GET", f"/api/projects/{PID}/decisions/{dec_ids['player_assist_mio']}")
mio_eff = (b or {}).get("complete_effect") or ""
print("军工原 effect:", mio_eff)
mio_eff2 = mio_eff.replace("add_political_power = -300", "").strip()
s, b = call("PUT", f"/api/projects/{PID}/decisions/{dec_ids['player_assist_mio']}", {"complete_effect": mio_eff2})
print("PUT player_assist_mio ->", s, (str(b)[:150] if s >= 300 else ""), "| 新 effect:", mio_eff2)

# ---------- 3. 校验 ----------
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:180])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("decision",)) if isinstance(b, dict) else "?")
