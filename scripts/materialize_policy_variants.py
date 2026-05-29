#!/usr/bin/env python3
"""Create controlled task variants using a frozen rewrite policy."""

from __future__ import annotations

import argparse
from pathlib import Path

from skill_economy.materialize import materialize_policy_variants


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    parser.add_argument("--rewrites-root", type=Path, default=Path("work/rewrites"))
    parser.add_argument("--profile", type=Path, default=Path("results/skill_structure_profile/skill_structure_profile.json"))
    parser.add_argument("--policy", type=Path, default=Path("configs/policies/frozen_selector.json"))
    parser.add_argument("--out-root", type=Path, default=Path("work/task_variants/policy_selected"))
    parser.add_argument("--task-list", type=Path, default=None)
    args = parser.parse_args()

    task_ids = None
    if args.task_list:
        task_ids = [line.strip() for line in args.task_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = materialize_policy_variants(
        tasks_root=args.tasks_root,
        rewrites_root=args.rewrites_root,
        profile_path=args.profile,
        policy_path=args.policy,
        out_root=args.out_root,
        task_ids=task_ids,
    )
    print(f"Wrote {args.out_root / 'policy_variant_manifest.json'}")
    print(f"Tasks: {len(manifest['tasks'])}")


if __name__ == "__main__":
    main()
