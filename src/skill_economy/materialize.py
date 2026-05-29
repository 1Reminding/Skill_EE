"""Materialize controlled task variants with rewritten skills."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .policy import select_strategy
from .strategies import normalize_strategy_id


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def copy_task_variant(src_task_dir: Path, dst_task_dir: Path) -> None:
    if dst_task_dir.exists():
        shutil.rmtree(dst_task_dir)
    shutil.copytree(src_task_dir, dst_task_dir)


def replace_skill_files(dst_task_dir: Path, rewrite_task_dir: Path) -> list[str]:
    replaced: list[str] = []
    for rewrite_skill in rewrite_task_dir.glob("environment/skills/*/SKILL.md"):
        rel = rewrite_skill.relative_to(rewrite_task_dir)
        target = dst_task_dir / rel
        if not target.exists():
            continue
        target.write_text(rewrite_skill.read_text(encoding="utf-8"), encoding="utf-8")
        replaced.append(str(rel))
    return replaced


def materialize_policy_variants(
    *,
    tasks_root: str | Path,
    rewrites_root: str | Path,
    profile_path: str | Path,
    policy_path: str | Path,
    out_root: str | Path,
    task_ids: list[str] | None = None,
) -> dict[str, Any]:
    tasks_root = Path(tasks_root)
    rewrites_root = Path(rewrites_root)
    out_root = Path(out_root)
    profile = read_json(profile_path)
    policy = read_json(policy_path)
    features_by_task = {task["task_id"]: task for task in profile.get("tasks", [])}
    selected_task_ids = task_ids or sorted(features_by_task)
    out_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for task_id in selected_task_ids:
        features = features_by_task[task_id]
        strategy, reason = select_strategy(features, policy)
        strategy = normalize_strategy_id(strategy)
        src_task = tasks_root / task_id
        dst_task = out_root / task_id
        rewrite_task = rewrites_root / strategy / task_id
        copy_task_variant(src_task, dst_task)
        replaced = replace_skill_files(dst_task, rewrite_task)
        rows.append(
            {
                "task_id": task_id,
                "strategy": strategy,
                "reason": reason,
                "rewritten_skill_files": replaced,
                "rewrites_found": rewrite_task.exists(),
            }
        )

    manifest = {
        "tasks_root": str(tasks_root),
        "rewrites_root": str(rewrites_root),
        "profile_path": str(profile_path),
        "policy_path": str(policy_path),
        "out_root": str(out_root),
        "tasks": rows,
    }
    (out_root / "policy_variant_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
