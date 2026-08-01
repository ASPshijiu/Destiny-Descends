# -*- coding: utf-8 -*-
"""天命降临 v8：拉大三档梯度（轻1:中1.5:重3），重档全面爆炸增强"""
import api_client as A

IDEA_IDS = {"player_assist_light_idea": 369870, "player_assist_medium_idea": 369871, "player_assist_heavy_idea": 369872}


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
    _, b = A.call("GET", f"/api/projects/{A.PID}/ideas/{iint}")
    cur = (b or {}).get("modifier") or {}
    pct_mult, flat_mult = TIER[iid]
    new = {}
    for k, v in cur.items():
        if k in FLAT_KEYS:
            new[k] = scale(v, flat_mult, True)
        else:
            new[k] = scale(v, pct_mult, False)
    s, b2 = A.call("PUT", f"/api/projects/{A.PID}/ideas/{iint}", {"modifier": new})
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
A.report_validation()
