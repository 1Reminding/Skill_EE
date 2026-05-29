"""Low-capacity task-conditioned rewrite policy."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from .metrics import compute_relative_metrics, economic_utility, load_rows
from .strategies import normalize_strategy_id


@dataclass(frozen=True)
class Predicate:
    name: str
    description: str
    fn: Callable[[dict[str, Any]], bool]


@dataclass(frozen=True)
class PolicyRule:
    predicate: str
    description: str
    strategy: str
    support: int
    mean_gain: float


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def predicate_bank(task_features: dict[str, dict[str, Any]]) -> list[Predicate]:
    domains = sorted({str(f.get("domain_group")) for f in task_features.values() if f.get("domain_group")})
    archetypes = sorted(
        {str(f.get("dominant_archetype")) for f in task_features.values() if f.get("dominant_archetype")}
    )
    predicates: list[Predicate] = []
    for domain in domains:
        predicates.append(
            Predicate(
                f"domain_group == {domain}",
                f"domain_group is {domain}",
                lambda f, domain=domain: f.get("domain_group") == domain,
            )
        )
    for archetype in archetypes:
        predicates.append(
            Predicate(
                f"dominant_archetype == {archetype}",
                f"dominant_archetype is {archetype}",
                lambda f, archetype=archetype: f.get("dominant_archetype") == archetype,
            )
        )
    for key in (
        "has_validation",
        "has_constraints",
        "has_examples",
        "has_api_usage",
        "has_formulas",
    ):
        predicates.append(Predicate(key, f"{key} is true", lambda f, key=key: bool(f.get(key))))
    for threshold in (750, 1200, 2000, 4000):
        predicates.append(
            Predicate(
                f"total_skill_tokens >= {threshold}",
                f"skill tokens >= {threshold}",
                lambda f, threshold=threshold: _as_float(f.get("total_skill_tokens")) >= threshold,
            )
        )
    for threshold in (0.2, 0.35, 0.5):
        predicates.append(
            Predicate(
                f"avg_code_token_ratio >= {threshold}",
                f"average code-token ratio >= {threshold}",
                lambda f, threshold=threshold: _as_float(f.get("avg_code_token_ratio")) >= threshold,
            )
        )
    for threshold in (1.0, 2.0, 4.0):
        predicates.append(
            Predicate(
                f"avg_validation_density >= {threshold}",
                f"average validation density >= {threshold}",
                lambda f, threshold=threshold: _as_float(f.get("avg_validation_density")) >= threshold,
            )
        )
    for threshold in (1.0, 2.0, 4.0):
        predicates.append(
            Predicate(
                f"avg_formula_density >= {threshold}",
                f"average formula/rule density >= {threshold}",
                lambda f, threshold=threshold: _as_float(f.get("avg_formula_density")) >= threshold,
            )
        )
    return predicates


def _row_strategy(row: dict[str, Any]) -> str:
    raw = str(row.get("strategy") or row.get("condition") or row.get("template_id") or "")
    if raw.lower() in {"baseline", "original", "original skills"}:
        return "baseline"
    return normalize_strategy_id(raw)


def _task_id(row: dict[str, Any]) -> str:
    return str(row.get("task_id") or row.get("task") or "")


def _utility_table(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    by_task_strategy: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        task_id = _task_id(row)
        strategy = _row_strategy(row)
        if task_id:
            by_task_strategy[(task_id, strategy)] = row
    table: dict[str, dict[str, float]] = {}
    for (task_id, strategy), row in by_task_strategy.items():
        if strategy == "baseline":
            continue
        baseline = by_task_strategy.get((task_id, "baseline"))
        if baseline is None:
            continue
        metrics = compute_relative_metrics(row, baseline)
        utility = economic_utility(metrics)
        if utility is not None:
            table.setdefault(task_id, {})[strategy] = utility
    return table


def _current_strategy(task_id: str, features: dict[str, Any], default: str, rules: list[PolicyRule]) -> str:
    for rule in rules:
        if _matches_rule_name(rule.predicate, features):
            return rule.strategy
    return default


def _matches_rule_name(rule_name: str, features: dict[str, Any]) -> bool:
    if " == " in rule_name:
        key, value = rule_name.split(" == ", 1)
        return str(features.get(key.strip())) == value.strip()
    if " >= " in rule_name:
        key, value = rule_name.split(" >= ", 1)
        return _as_float(features.get(key.strip())) >= _as_float(value)
    return bool(features.get(rule_name))


def learn_policy(
    rows: list[dict[str, Any]],
    task_features: dict[str, dict[str, Any]],
    *,
    candidate_strategies: tuple[str, ...] = ("api_code", "rule_formula", "workflow"),
    min_support: int = 3,
    min_gain: float = 0.0,
) -> dict[str, Any]:
    """Learn a small greedy decision list from observed economic utility."""

    candidate_strategies = tuple(normalize_strategy_id(strategy) for strategy in candidate_strategies)
    utilities = _utility_table(rows)
    strategy_means: dict[str, float] = {}
    for strategy in candidate_strategies:
        values = [by_strategy[strategy] for by_strategy in utilities.values() if strategy in by_strategy]
        if values:
            strategy_means[strategy] = mean(values)
    if not strategy_means:
        raise ValueError("No usable task-strategy utilities found")
    default = max(strategy_means.items(), key=lambda item: item[1])[0]
    rules: list[PolicyRule] = []
    predicates = predicate_bank(task_features)

    while True:
        best: PolicyRule | None = None
        for predicate in predicates:
            matching_tasks = [
                task_id
                for task_id, features in task_features.items()
                if predicate.fn(features) and task_id in utilities
            ]
            if len(matching_tasks) < min_support:
                continue
            for strategy in candidate_strategies:
                gains = []
                for task_id in matching_tasks:
                    if strategy not in utilities[task_id]:
                        continue
                    current = _current_strategy(task_id, task_features[task_id], default, rules)
                    if current not in utilities[task_id]:
                        continue
                    gains.append(utilities[task_id][strategy] - utilities[task_id][current])
                if len(gains) < min_support:
                    continue
                gain = mean(gains)
                if gain <= min_gain:
                    continue
                candidate = PolicyRule(
                    predicate=predicate.name,
                    description=predicate.description,
                    strategy=strategy,
                    support=len(gains),
                    mean_gain=round(gain, 6),
                )
                if best is None or candidate.mean_gain > best.mean_gain:
                    best = candidate
        if best is None:
            break
        if any(rule.predicate == best.predicate and rule.strategy == best.strategy for rule in rules):
            break
        rules.append(best)
        if len(rules) >= 6:
            break

    return {
        "policy_id": "learned_decision_list",
        "default_strategy": default,
        "candidate_strategies": list(candidate_strategies),
        "rules": [asdict(rule) for rule in rules],
        "diagnostics": {
            "strategy_mean_utility": {key: round(value, 6) for key, value in strategy_means.items()},
            "tasks_with_utility": len(utilities),
            "min_support": min_support,
            "min_gain": min_gain,
        },
    }


def select_strategy(features: dict[str, Any], policy: dict[str, Any]) -> tuple[str, str]:
    for rule in policy.get("rules", []):
        if _matches_rule_name(rule["predicate"], features):
            return rule["strategy"], rule.get("predicate", "rule")
    return policy["default_strategy"], "default"


def load_task_features(profile_path: str | Path) -> dict[str, dict[str, Any]]:
    profile = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    return {task["task_id"]: task for task in profile.get("tasks", [])}


def learn_policy_from_files(
    observations_path: str | Path,
    profile_path: str | Path,
    out_path: str | Path,
    *,
    min_support: int = 3,
) -> dict[str, Any]:
    rows = load_rows(observations_path)
    features = load_task_features(profile_path)
    policy = learn_policy(rows, features, min_support=min_support)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")
    return policy
