# -*- coding: utf-8 -*-
"""天命降临 v8：拉大三档梯度（轻1:中1.5:重3），重档全面爆炸增强"""
import json, os, sys, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008
IDEA_IDS = {"player_assist_light_idea": 369870, "player_assist_medium_idea": 369871, "player_assist_heavy_idea": 369872}

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

def scale(val, mult, is_flat):
    """按类型缩放：flat 整数用较小倍率，百分比用大倍率"""
    if is_flat:
        nv = val * mult
        return int(round(nv))
    nv = val * mult
    return round(nv, 2)

# 中档 ×1.5、重档 ×3（百分比）；flat 整数 中×1.5 重×2
TIER = {"player_assist_light_idea": (1.0, 1.0), "player_assist_medium_idea": (1.5, 1.5), "player_assist_heavy_idea": (3.0, 2.0)}
FLAT_KEYS = {"industrial_capacity_factory", "political_power_gain", "weekly_manpower",
             "special_forces_cap_flat", "army_leader_start_level", "naval_invasion_capacity"}

summary = {}
for iid, iint in IDEA_IDS.items():
    _, b = call("GET", f"/api/projects/{PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    pct_mult, flat_mult = TIER[iid]
    new = {}
    for k, v in cur.items():
        if k in FLAT_KEYS:
            new[k] = scale(v, flat_mult, True)
        else:
            new[k] = scale(v, pct_mult, False)
    s, b2 = call("PUT", f"/api/projects/{PID}/ideas/{iint}", {"modifier": new})
    summary[iid] = new
    print(f"PUT {iid} ->", s, (str(b2)[:150] if s >= 300 else ""))

# 打印重档关键数值（对比恐怖程度）
h = summary["player_assist_heavy_idea"]
print("\n=== 天命之主（重档）关键数值 ===")
for k in ["political_power_factor", "stability_factor", "war_support_factor", "research_speed_factor",
          "production_speed_factor", "building_speed_factor", "industrial_capacity_factory",
          "resource_gain_factor", "army_attack_factor", "army_org_factor", "army_morale_factor",
          "recruitable_population_factor", "weekly_manpower", "political_power_gain",
          "surrender_limit", "training_time_factor", "consumer_goods_factor", "navy_attack_factor",
          "air_attack_factor", "justify_war_goal_time", "special_forces_cap_flat", "army_leader_start_level"]:
    if k in h:
        print(f"  {k}: {h[k]}")

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:150])
s, b = call("GET", f"/api/lint/tree-validation/{PID}")
print("lint ->", s, "issues:", sum(len(b.get(k, [])) for k in ("idea","focus","event","decision")) if isinstance(b, dict) else "?")
