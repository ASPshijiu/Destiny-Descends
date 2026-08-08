# -*- coding: utf-8 -*-
"""v29：按修正项语义重新平衡轻度、中度和重度增益。"""

import api_client as A


TIER_INDEX = {
    "player_assist_light_idea": 0,
    "player_assist_medium_idea": 1,
    "player_assist_heavy_idea": 2,
}

# 普通百分比型增益：+10% / +25% / +50%。
DEFAULT_VALUES = (0.10, 0.25, 0.50)

# 这些修正项的正数表示惩罚或花费，因此增益必须使用负数。
NEGATIVE_KEYS = {
    "air_accidents_factor",
    "air_chief_cost_factor",
    "air_untrained_pilots_penalty_factor",
    "army_chief_cost_factor",
    "army_fuel_consumption_factor",
    "attrition",
    "command_abilities_cost_factor",
    "high_command_cost_factor",
    "industry_air_damage_factor",
    "navy_chief_cost_factor",
    "out_of_supply_factor",
    "political_advisor_cost_factor",
    "supply_consumption_factor",
}
NEGATIVE_VALUES = (-0.10, -0.25, -0.50)

# 固定值、风险较高或需要单独控制强度的修正项。
CUSTOM_VALUES = {
    "army_leader_start_level": (1, 2, 3),
    "army_morale_factor": (0.05, 0.15, 0.30),
    "army_org_factor": (0.05, 0.15, 0.30),
    "army_speed_factor": (0.05, 0.10, 0.20),
    "command_power_gain": (0.25, 0.50, 1.00),
    "conscription": (0.02, 0.05, 0.10),
    "consumer_goods_factor": (-0.05, -0.10, -0.20),
    "experience_gain_air": (0.10, 0.25, 0.50),
    "experience_gain_army": (0.10, 0.25, 0.50),
    "experience_gain_navy": (0.10, 0.25, 0.50),
    "fuel_gain_factor": (0.15, 0.35, 0.75),
    "industrial_capacity_factory": (0.15, 0.35, 0.75),
    "justify_war_goal_time": (-0.15, -0.35, -0.60),
    "land_reinforce_rate": (0.02, 0.05, 0.10),
    "local_resources_factor": (0.15, 0.35, 0.75),
    "max_command_power": (50, 100, 250),
    "max_planning_factor": (0.05, 0.15, 0.30),
    "naval_morale_factor": (0.05, 0.15, 0.30),
    "naval_speed_factor": (0.05, 0.10, 0.20),
    "navy_org_factor": (0.05, 0.15, 0.30),
    "political_power_factor": (0.25, 0.50, 1.00),
    "political_power_gain": (0.25, 0.50, 1.00),
    "production_factory_efficiency_gain_factor": (0.15, 0.35, 0.75),
    "production_factory_max_efficiency_factor": (0.10, 0.25, 0.50),
    "production_speed_buildings_factor": (0.15, 0.35, 0.75),
    "production_speed_dockyard_factor": (0.15, 0.35, 0.75),
    "production_speed_industrial_complex_factor": (0.15, 0.35, 0.75),
    "production_speed_infrastructure_factor": (0.15, 0.35, 0.75),
    "recruitable_population_factor": (0.10, 0.25, 0.50),
    "repair_speed_factor": (0.15, 0.35, 0.75),
    "research_speed_factor": (0.10, 0.25, 0.50),
    "send_volunteer_size": (1, 3, 5),
    "special_forces_cap_flat": (2, 5, 10),
    "stability_factor": (0.10, 0.20, 0.35),
    "supply_node_range": (0.10, 0.20, 0.35),
    "surrender_limit": (0.10, 0.20, 0.35),
    "terrain_penalty_reduction": (0.05, 0.10, 0.20),
    "training_time_factor": (-0.15, -0.30, -0.50),
    "war_support_factor": (0.10, 0.20, 0.35),
    "weekly_manpower": (100, 500, 2000),
}

# 正数会额外占用民用工厂，不属于增益；三个档位都删除。
REMOVE_KEYS = {"civilian_factory_use"}


def values_for(key):
    if key in CUSTOM_VALUES:
        return CUSTOM_VALUES[key]
    if key in NEGATIVE_KEYS:
        return NEGATIVE_VALUES
    return DEFAULT_VALUES


def rebalance(modifier, tier_index):
    return {
        key: values_for(key)[tier_index]
        for key in modifier
        if key not in REMOVE_KEYS
    }


def main():
    ids = A.get_ids("ideas", "idea_id")
    missing = set(TIER_INDEX) - set(ids)
    if missing:
        raise RuntimeError(f"缺少目标 idea：{sorted(missing)}")

    originals = {}
    expected = {}
    updated = []

    for idea_id in TIER_INDEX:
        status, idea = A.call("GET", f"/api/projects/{A.PID}/ideas/{ids[idea_id]}")
        A.ensure_ok(status, idea, f"读取 {idea_id}")
        originals[idea_id] = dict(idea.get("modifier") or {})

    # 三档使用同一组修正项，只让强度不同；同时保留平台原有的稳定输出顺序。
    all_modifier_keys = dict.fromkeys(
        key
        for modifier in originals.values()
        for key in modifier
        if key not in REMOVE_KEYS
    )
    for idea_id, tier_index in TIER_INDEX.items():
        expected[idea_id] = rebalance(all_modifier_keys, tier_index)

    try:
        for idea_id in TIER_INDEX:
            status, result = A.call(
                "PUT",
                f"/api/projects/{A.PID}/ideas/{ids[idea_id]}",
                {"modifier": expected[idea_id]},
            )
            A.ensure_ok(status, result, f"更新 {idea_id}")
            updated.append(idea_id)

        for idea_id in TIER_INDEX:
            status, idea = A.call("GET", f"/api/projects/{A.PID}/ideas/{ids[idea_id]}")
            A.ensure_ok(status, idea, f"复核 {idea_id}")
            actual = idea.get("modifier") or {}
            if actual != expected[idea_id]:
                raise RuntimeError(f"{idea_id} 回读结果与预期不一致")
    except Exception:
        for idea_id in reversed(updated):
            status, result = A.call(
                "PUT",
                f"/api/projects/{A.PID}/ideas/{ids[idea_id]}",
                {"modifier": originals[idea_id]},
            )
            A.ensure_ok(status, result, f"回滚 {idea_id}")
        raise

    A.report_validation()
    for idea_id in TIER_INDEX:
        modifier = expected[idea_id]
        print(
            idea_id,
            f"修正项={len(modifier)}",
            f"科研={modifier.get('research_speed_factor')}",
            f"工厂产出={modifier.get('industrial_capacity_factory')}",
            f"周人力={modifier.get('weekly_manpower')}",
        )


if __name__ == "__main__":
    main()
