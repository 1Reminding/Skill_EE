#!/usr/bin/env python3
"""Learn a compact task-conditioned rewrite selector."""

from __future__ import annotations

import argparse
from pathlib import Path

from skill_economy.policy import learn_policy_from_files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=Path("results/skill_structure_profile/skill_structure_profile.json"))
    parser.add_argument("--out", type=Path, default=Path("configs/policies/learned_policy.json"))
    parser.add_argument("--min-support", type=int, default=3)
    args = parser.parse_args()

    policy = learn_policy_from_files(
        args.observations,
        args.profile,
        args.out,
        min_support=args.min_support,
    )
    print(f"Wrote {args.out}")
    print(f"Default strategy: {policy['default_strategy']}")
    for rule in policy.get("rules", []):
        print(f"- if {rule['predicate']} -> {rule['strategy']} (gain={rule['mean_gain']})")


if __name__ == "__main__":
    main()
