#!/usr/bin/env python3
"""Profile original SkillsBench task skills."""

from __future__ import annotations

import argparse
from pathlib import Path

from skill_economy.profiling import profile_tasks, write_profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/skill_structure_profile"))
    args = parser.parse_args()

    profile = profile_tasks(args.tasks_root)
    write_profile(profile, args.out_dir)
    print(f"Wrote profile to {args.out_dir}")


if __name__ == "__main__":
    main()
