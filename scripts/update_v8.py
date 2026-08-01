# -*- coding: utf-8 -*-
"""天命降临 v8：拉大三档梯度（轻1:中1.5:重3），重档全面爆炸增强

注意：本脚本是「读当前值 × 倍率 → 写回」的有状态改写，**不可重跑**——
重跑会把已缩放数值再乘一遍（重档 ×3 变 ×9）。已内置幂等保护：检测到
重档政治点 ≥2.0（v8 的输出特征）即中止。
"""
import api_client as A

TARGETS = ("player_assist_light_idea", "player_assist_medium_idea", "player_assist_heavy_idea")


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

IDEA_IDS = A.get_ids("ideas", "idea_id")

# ---- 幂等保护：检测重档是否已被 v8 缩放（重档政治点 v7=1.0，v8 后=3.0）----
heavy_id = IDEA_IDS.get("player_assist_heavy_idea")
if heavy_id:
    s0, b0 = A.call("GET", f"/api/projects/{A.PID}/ideas/{heavy_id}")
    A.ensure_ok(s0, b0, "GET 重档（幂等检查）")
    heavy_pp = ((b0 or {}).get("modifier") or {}).get("political_power_factor")
    if heavy_pp is not None and heavy_pp >= 2.0:
        raise SystemExit(
            f"检测到重档 political_power_factor = {heavy_pp}（≥2.0，已是 v8 缩放后的数值）。"
            f"\nv8 为「读-乘-写」脚本，重跑会把数值再乘一遍（×3 变 ×9），已中止执行。"
            f"\n如需再次调整梯度，请手工修正平台数值或改用声明式脚本。")

summary = {}
for iid, iint in IDEA_IDS.items():
    if iid not in TARGETS:
        continue
    s0, b = A.call("GET", f"/api/projects/{A.PID}/ideas/{iint}")
    A.ensure_ok(s0, b, f"GET {iid}")
    cur = (b or {}).get("modifier") or {}
    pct_mult, flat_mult = TIER[iid]
    new = {}
    for k, v in cur.items():
        if k in FLAT_KEYS:
            new[k] = scale(v, flat_mult, True)
        else:
            new[k] = scale(v, pct_mult, False)
    s, b2 = A.call("PUT", f"/api/projects/{A.PID}/ideas/{iint}", {"modifier": new})
    A.ensure_ok(s, b2, f"PUT {iid}")
    summary[iid] = new
    print(f"PUT {iid} ->", s)

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
