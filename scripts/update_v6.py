# -*- coding: utf-8 -*-
"""天命降临 v6：扩展 8 个 buff 维度 + 校验导出安装"""
import api_client as A

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
    _, b = A.call("GET", f"/api/projects/{A.PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    tier = "light" if "light" in iid else ("medium" if "medium" in iid else "heavy")
    merged = dict(cur)
    merged.update(NEW[tier])
    s, b2 = A.call("PUT", f"/api/projects/{A.PID}/ideas/{iint}", {"modifier": merged})
    print(f"PUT {iid} ({len(merged)} modifiers) ->", s, (str(b2)[:150] if s >= 300 else ""))

# 校验
A.report_validation()

# 导出 + 安装
names, mod_folder = A.export_and_install(
    r"C:\Users\xw130\Desktop\hoi4\天命降临_v6.zip",
    tmpdir=r"C:\Users\xw130\Desktop\hoi4\_tm_install")
# 图标验证
for n in sorted(names):
    if "idea" in n and ("png" in n or "dds" in n):
        print("  icon file:", n)
