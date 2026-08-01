# -*- coding: utf-8 -*-
"""重建 mod 到项目 2008：修复元数据（正确 UTF-8 中文）+ 重建全部内容实体"""
import json, os, sys, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = int(os.environ.get("HOI4_PROJECT_ID", "2008"))

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

# 1. 元数据：正确中文名 + 双语导出 + Gameplay 标签
s, b = call("PUT", f"/api/projects/{PID}", {
    "name": "游戏体验增强",
    "export_languages": ["en", "zh"],
    "tags": ["Gameplay"],
})
print("PUT meta ->", s)
if isinstance(b, dict):
    print("name:", b.get("name"), "| langs:", b.get("export_languages"), "| tags:", b.get("tags"))
else:
    print(b)

s, b = call("GET", f"/api/projects/{PID}")
print("GET back name:", (b or {}).get("name") if isinstance(b, dict) else b)

# 2. 决议分类
VISIBLE_ALL = ("NOT = { has_completed_decision = player_assist_light } "
               "NOT = { has_completed_decision = player_assist_medium } "
               "NOT = { has_completed_decision = player_assist_heavy }")

s, b = call("POST", f"/api/projects/{PID}/decisions/categories", {
    "category_id": "player_assistance",
    "name_en": "Player Assistance",
    "name_zh": "玩家辅助",
    "desc_en": "Enable your personal assistance system.",
    "desc_zh": "启用你的个人辅助系统。",
    "allowed": "is_ai = no",
    "priority": 1,
})
print("POST category ->", s)
if isinstance(b, dict):
    print("  cat_id:", b.get("id"), "| name_zh:", b.get("name_zh"))
    cat_id = b.get("id")
else:
    print(" ", b)
    cat_id = None

# 3. 三个决议
decisions = [
    ("player_assist_light", "启用辅助系统·轻度", "Enable Assistance · Light",
     "为玩家提供一组轻度的国家增益。",
     "Grant a light set of national bonuses to the player.",
     "player_assist_light_idea"),
    ("player_assist_medium", "启用辅助系统·中度", "Enable Assistance · Medium",
     "为玩家提供一组中度的国家增益。",
     "Grant a medium set of national bonuses to the player.",
     "player_assist_medium_idea"),
    ("player_assist_heavy", "启用辅助系统·全面", "Enable Assistance · Full",
     "为玩家提供海量的国家增益。",
     "Grant a massive set of national bonuses to the player.",
     "player_assist_heavy_idea"),
]
for did, nz, ne, dz, de, idea in decisions:
    body = {
        "category_id": cat_id,
        "decision_id": did,
        "name_en": ne, "name_zh": nz,
        "desc_en": de, "desc_zh": dz,
        "cost": 0,
        "allowed": "is_ai = no",
        "visible": VISIBLE_ALL,
        "complete_effect": f"add_ideas = {idea}",
        "fire_only_once": True,
    }
    s, b = call("POST", f"/api/projects/{PID}/decisions", body)
    print(f"POST decision {did} ->", s)
    if s >= 300:
        print("  ", json.dumps(b, ensure_ascii=False)[:400] if isinstance(b, (dict, list)) else b)

# 4. 三个民族精神
ideas = [
    ("player_assist_light_idea", "辅助系统·轻度", "Player Assistance · Light",
     "玩家轻度辅助：稳定度、战争支持度、科研与政治点数提升。",
     "A light set of player bonuses: stability, war support, research and political power.",
     {"stability_factor": 0.10, "war_support_factor": 0.10,
      "research_speed_factor": 0.10, "political_power_factor": 0.25}),
    ("player_assist_medium_idea", "辅助系统·中度", "Player Assistance · Medium",
     "玩家中度辅助：工业、科研、生产效率与政治点数提升。",
     "A medium set of player bonuses: industry, research, production and political power.",
     {"stability_factor": 0.10, "war_support_factor": 0.10,
      "research_speed_factor": 0.15, "production_speed_factor": 0.15,
      "consumer_goods_factor": -0.05, "political_power_factor": 0.50}),
    ("player_assist_heavy_idea", "辅助系统·全面", "Player Assistance · Full",
     "玩家全面辅助：工业、科研、军事、经济全方位海量增益。",
     "A massive set of player bonuses across every dimension of the nation.",
     {"stability_factor": 0.20, "war_support_factor": 0.20,
      "research_speed_factor": 0.50, "production_speed_factor": 0.30,
      "consumer_goods_factor": -0.15, "political_power_factor": 1.00,
      "army_attack_factor": 0.15, "army_defence_factor": 0.15,
      "army_org_factor": 0.20, "justify_war_goal_time": -0.30,
      "conscription": 0.05}),
]
for iid, nz, ne, dz, de, mod in ideas:
    body = {
        "idea_id": iid,
        "idea_type": "country",
        "name_en": ne, "name_zh": nz,
        "desc_en": de, "desc_zh": dz,
        "picture": "generic_build_infrastructure",
        "modifier": mod,
        "auto_attach_on_start": False,
    }
    s, b = call("POST", f"/api/projects/{PID}/ideas", body)
    print(f"POST idea {iid} ->", s)
    if s >= 300:
        print("  ", json.dumps(b, ensure_ascii=False)[:400] if isinstance(b, (dict, list)) else b)

print("\nREBUILD DONE on project", PID)
