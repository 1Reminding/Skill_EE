from skill_economy.policy import learn_policy, select_strategy


def test_policy_learns_feature_override():
    features = {
        "science-task": {"task_id": "science-task", "domain_group": "scientific_computing"},
        "data-task": {"task_id": "data-task", "domain_group": "data_analysis_ml"},
        "code-task": {"task_id": "code-task", "domain_group": "code_debug_build"},
    }
    rows = [
        {"task_id": "science-task", "strategy": "baseline", "partial": 1.0, "skill_tokens": 100, "agent_tokens": 100},
        {"task_id": "science-task", "strategy": "api_code", "partial": 0.8, "skill_tokens": 80, "agent_tokens": 100},
        {"task_id": "science-task", "strategy": "rule_formula", "partial": 1.0, "skill_tokens": 80, "agent_tokens": 80},
        {"task_id": "data-task", "strategy": "baseline", "partial": 1.0, "skill_tokens": 100, "agent_tokens": 100},
        {"task_id": "data-task", "strategy": "api_code", "partial": 0.8, "skill_tokens": 80, "agent_tokens": 100},
        {"task_id": "data-task", "strategy": "rule_formula", "partial": 1.0, "skill_tokens": 80, "agent_tokens": 80},
        {"task_id": "code-task", "strategy": "baseline", "partial": 1.0, "skill_tokens": 100, "agent_tokens": 100},
        {"task_id": "code-task", "strategy": "api_code", "partial": 1.0, "skill_tokens": 80, "agent_tokens": 80},
        {"task_id": "code-task", "strategy": "rule_formula", "partial": 0.6, "skill_tokens": 80, "agent_tokens": 80},
    ]

    policy = learn_policy(rows, features, min_support=1)
    selected, _ = select_strategy(features["science-task"], policy)

    assert selected in {"rule_formula", "api_code"}
    assert policy["default_strategy"] in {"api_code", "rule_formula"}
