"""Economic metrics for cost-aware skill rewriting."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any


EPS = 1e-9

DEFAULT_UTILITY_WEIGHTS = {
    "save": 1.0,
    "overrun": 1.0,
    "near_lossless": 0.5,
    "near_lossless_delta": 0.05,
}


def as_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number):
        return default
    return number


def first_number(row: dict[str, Any], keys: tuple[str, ...], default: float | None = None) -> float | None:
    for key in keys:
        if key in row:
            value = as_float(row.get(key), None)
            if value is not None:
                return value
    return default


def total_cost(row: dict[str, Any]) -> float:
    skill_tokens = first_number(row, ("skill_tokens", "total_skill_tokens", "C_skill"), 0.0) or 0.0
    agent_tokens = first_number(
        row,
        ("agent_tokens", "api_total_tokens", "effective_agent_tokens", "total_agent_tokens", "C_agent"),
        0.0,
    ) or 0.0
    explicit = first_number(row, ("total_cost", "C_total"), None)
    return explicit if explicit is not None else skill_tokens + agent_tokens


def quality(row: dict[str, Any]) -> float | None:
    return first_number(row, ("partial", "partial_test_score", "q", "quality"), None)


def reward(row: dict[str, Any]) -> float | None:
    return first_number(row, ("reward", "binary_reward"), None)


def compute_relative_metrics(
    row: dict[str, Any],
    baseline: dict[str, Any],
    *,
    near_lossless_delta: float = DEFAULT_UTILITY_WEIGHTS["near_lossless_delta"],
) -> dict[str, float | None]:
    """Compute paper metrics for a rewritten-skill condition.

    The baseline should be the original-skill run for the same task and agent
    stack. Costs are token counts unless a caller substitutes monetary units.
    """

    q = quality(row)
    q0 = quality(baseline)
    skill = first_number(row, ("skill_tokens", "total_skill_tokens", "C_skill"), 0.0) or 0.0
    skill0 = first_number(baseline, ("skill_tokens", "total_skill_tokens", "C_skill"), 0.0) or 0.0
    agent = first_number(
        row,
        ("agent_tokens", "api_total_tokens", "effective_agent_tokens", "total_agent_tokens", "C_agent"),
        0.0,
    ) or 0.0
    agent0 = first_number(
        baseline,
        ("agent_tokens", "api_total_tokens", "effective_agent_tokens", "total_agent_tokens", "C_agent"),
        0.0,
    ) or 0.0
    total = total_cost(row)
    total0 = total_cost(baseline)

    qr = q / max(q0 or 0.0, EPS) if q is not None and q0 is not None else None
    r_s = skill / max(skill0, EPS)
    r_a = agent / max(agent0, EPS)
    rho = total / max(total0, EPS)
    delta = r_a - 1.0
    overrun = max(0.0, delta)
    nld = max(0.0, 1.0 - rho) if qr is not None and qr >= 1.0 - near_lossless_delta else 0.0

    return {
        "quality_retention": qr,
        "skill_token_ratio": r_s,
        "agent_token_ratio": r_a,
        "total_cost_ratio": rho,
        "execution_cost_change": delta,
        "execution_overrun": overrun,
        "near_lossless_dividend": nld,
    }


def economic_utility(
    metrics: dict[str, float | None],
    *,
    weights: dict[str, float] | None = None,
) -> float | None:
    weights = weights or DEFAULT_UTILITY_WEIGHTS
    qr = metrics.get("quality_retention")
    rho = metrics.get("total_cost_ratio")
    overrun = metrics.get("execution_overrun") or 0.0
    nld = metrics.get("near_lossless_dividend") or 0.0
    if qr is None or rho is None:
        return None
    return (
        qr
        + weights.get("save", 1.0) * (1.0 - rho)
        - weights.get("overrun", 1.0) * overrun
        + weights.get("near_lossless", 0.5) * nld
    )


def load_rows(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        for key in ("jobs", "rows", "observations"):
            if isinstance(data.get(key), list):
                return data[key]
        raise ValueError(f"Could not find row list in {path}")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize_conditions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate rows by agent stack and skill condition.

    Rows should contain ``task_id``, ``condition`` or ``strategy``, quality, skill
    tokens, and agent tokens. Baselines are rows with condition ``original`` or
    ``baseline``.
    """

    def condition(row: dict[str, Any]) -> str:
        return str(row.get("condition") or row.get("strategy") or row.get("template_id") or "")

    def stack(row: dict[str, Any]) -> str:
        return str(row.get("agent_stack") or row.get("stack") or "default")

    baselines: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        cond = condition(row).lower()
        if cond in {"original", "original skills", "baseline"}:
            baselines[(stack(row), str(row.get("task_id")))] = row

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((stack(row), condition(row)), []).append(row)

    output = []
    for (agent_stack, cond), group in sorted(grouped.items()):
        partials = [quality(row) for row in group if quality(row) is not None]
        rewards = [reward(row) for row in group if reward(row) is not None]
        relative = []
        utilities = []
        for row in group:
            baseline = baselines.get((agent_stack, str(row.get("task_id"))))
            if baseline is None:
                continue
            metrics = compute_relative_metrics(row, baseline)
            relative.append(metrics)
            utility = economic_utility(metrics)
            if utility is not None:
                utilities.append(utility)

        def avg(key: str) -> float | None:
            values = [item.get(key) for item in relative if item.get(key) is not None]
            return round(mean(values), 6) if values else None

        output.append(
            {
                "agent_stack": agent_stack,
                "condition": cond,
                "n": len(group),
                "valid_quality": len(partials),
                "partial": round(mean(partials), 6) if partials else None,
                "reward": round(mean(rewards), 6) if rewards else None,
                "quality_retention": avg("quality_retention"),
                "skill_token_ratio": avg("skill_token_ratio"),
                "agent_token_ratio": avg("agent_token_ratio"),
                "total_cost_ratio": avg("total_cost_ratio"),
                "execution_cost_change": avg("execution_cost_change"),
                "near_lossless_dividend": avg("near_lossless_dividend"),
                "economic_utility": round(mean(utilities), 6) if utilities else None,
            }
        )
    return output
