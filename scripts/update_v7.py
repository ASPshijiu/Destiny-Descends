# -*- coding: utf-8 -*-
"""天命降临 v7：追加 30 项缺失高价值增益维度"""
import api_client as A

TARGETS = ("player_assist_light_idea", "player_assist_medium_idea", "player_assist_heavy_idea")

# 30 项新维度（轻/中/重渐进）
NEW = {
    # 陆军
    "army_speed_factor": (0.05, 0.10, 0.20),
    "army_org_regain": (0.05, 0.10, 0.20),
    "breakthrough_factor": (0.05, 0.10, 0.20),
    "max_dig_in_factor": (0.05, 0.10, 0.20),
    "special_forces_cap_flat": (2, 4, 8),
    "army_core_defence_factor": (0.05, 0.10, 0.20),
    # 海军
    "navy_org_factor": (0.05, 0.10, 0.20),
    "naval_morale_factor": (0.05, 0.10, 0.20),
    "navy_capital_ship_attack_factor": (0.05, 0.10, 0.20),
    "shore_bombardment_bonus": (0.05, 0.10, 0.20),
    # 空军
    "air_range_factor": (0.05, 0.10, 0.20),
    "air_maximum_speed_factor": (0.05, 0.10, 0.20),
    "air_ace_bonuses_factor": (0.10, 0.20, 0.50),
    "air_untrained_pilots_penalty_factor": (-0.10, -0.20, -0.40),
    # 后勤
    "supply_node_range": (0.05, 0.10, 0.20),
    "out_of_supply_factor": (-0.05, -0.10, -0.20),
    "army_fuel_consumption_factor": (-0.05, -0.10, -0.20),
    # 经济
    "civilian_factory_use": (-0.02, -0.05, -0.10),
    "production_factory_efficiency_gain_factor": (0.05, 0.10, 0.20),
    # 人口
    "weekly_manpower": (5, 10, 20),
    # 政治/指挥
    "political_power_gain": (0.50, 1.0, 2.0),
    "max_command_power_mult": (0.10, 0.20, 0.50),
    "army_leader_start_level": (1, 2, 3),
    # 防御
    "surrender_limit": (0.05, 0.10, 0.20),
    "attrition": (-0.05, -0.10, -0.20),
    "terrain_penalty_reduction": (0.05, 0.10, 0.20),
    # 外交
    "trade_opinion_factor": (0.05, 0.10, 0.20),
    # 情报
    "intel_network_gain_factor": (0.10, 0.20, 0.50),
    "encryption_factor": (0.10, 0.20, 0.50),
    "decryption_factor": (0.10, 0.20, 0.50),
}

TIER = {"player_assist_light_idea": 0, "player_assist_medium_idea": 1, "player_assist_heavy_idea": 2}
IDEA_IDS = A.get_ids("ideas", "idea_id")
for iid, iint in IDEA_IDS.items():
    if iid not in TARGETS:
        continue
    s0, b = A.call("GET", f"/api/projects/{A.PID}/ideas/{iint}")
    A.ensure_ok(s0, b, f"GET {iid}")
    cur = (b or {}).get("modifier") or {}
    t = TIER[iid]
    for k, v in NEW.items():
        cur[k] = v[t]
    s, b2 = A.call("PUT", f"/api/projects/{A.PID}/ideas/{iint}", {"modifier": cur})
    A.ensure_ok(s, b2, f"PUT {iid}")
    print(f"PUT {iid} ({len(cur)} modifiers) ->", s)

# 校验
A.report_validation()
