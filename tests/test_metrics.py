from skill_economy.metrics import compute_relative_metrics, economic_utility


def test_relative_metrics_near_lossless_saving():
    baseline = {"partial": 0.8, "skill_tokens": 1000, "agent_tokens": 9000}
    rewrite = {"partial": 0.8, "skill_tokens": 600, "agent_tokens": 8000}

    metrics = compute_relative_metrics(rewrite, baseline)

    assert metrics["quality_retention"] == 1.0
    assert metrics["skill_token_ratio"] == 0.6
    assert metrics["agent_token_ratio"] == 8000 / 9000
    assert metrics["total_cost_ratio"] == 0.86
    assert metrics["near_lossless_dividend"] > 0
    assert economic_utility(metrics) > 1.0


def test_downstream_overrun_penalized():
    baseline = {"partial": 1.0, "skill_tokens": 1000, "agent_tokens": 9000}
    rewrite = {"partial": 1.0, "skill_tokens": 500, "agent_tokens": 12000}

    metrics = compute_relative_metrics(rewrite, baseline)

    assert metrics["execution_cost_change"] > 0
    assert metrics["execution_overrun"] > 0
    assert economic_utility(metrics) < 1.0
