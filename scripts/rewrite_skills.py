#!/usr/bin/env python3
"""Generate strategy-conditioned skill rewrites.

By default this script writes prompts only. Pass ``--call-openai`` to call an
OpenAI-compatible chat completions endpoint using ``OPENAI_API_KEY`` and
``OPENAI_MODEL``.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from skill_economy.strategies import (
    audit_rewrite,
    build_rewrite_prompt,
    get_strategy,
    parse_rewrite_response,
    restore_missing_anchors,
)


def iter_task_ids(tasks_root: Path, task_list: Path | None) -> list[str]:
    if task_list:
        return [line.strip() for line in task_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    return sorted(path.name for path in tasks_root.iterdir() if path.is_dir())


def call_openai(prompt: str) -> str:
    from openai import OpenAI

    model = os.environ.get("OPENAI_MODEL") or os.environ.get("SKILLBENCH_MODEL")
    if not model:
        raise RuntimeError("Set OPENAI_MODEL or SKILLBENCH_MODEL")
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Return one valid JSON object only."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or "{}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks"))
    parser.add_argument("--task-list", type=Path, default=None)
    parser.add_argument("--strategy", required=True, help="api_code, rule_formula, workflow, or source_native_compact")
    parser.add_argument("--out-root", type=Path, default=Path("work/rewrites"))
    parser.add_argument("--call-openai", action="store_true")
    args = parser.parse_args()

    strategy = get_strategy(args.strategy)
    task_ids = iter_task_ids(args.tasks_root, args.task_list)
    manifest = []
    for task_id in task_ids:
        task_dir = args.tasks_root / task_id
        for skill_path in sorted(task_dir.glob("environment/skills/*/SKILL.md")):
            original = skill_path.read_text(encoding="utf-8", errors="replace")
            prompt = build_rewrite_prompt(original, strategy)
            rel = skill_path.relative_to(task_dir)
            out_skill = args.out_root / strategy.strategy_id / task_id / rel
            out_skill.parent.mkdir(parents=True, exist_ok=True)
            prompt_path = out_skill.with_suffix(".prompt.txt")
            prompt_path.write_text(prompt, encoding="utf-8")

            rewritten = original
            raw_path = None
            if args.call_openai:
                raw = call_openai(prompt)
                raw_path = out_skill.with_suffix(".raw.json")
                raw_path.write_text(raw, encoding="utf-8")
                parsed = parse_rewrite_response(raw)
                rewritten = parsed.get("rewritten_skill_md") or original
                rewritten = restore_missing_anchors(original, rewritten, strategy)
                out_skill.write_text(rewritten, encoding="utf-8")

            audit = audit_rewrite(original, rewritten)
            manifest.append(
                {
                    "task_id": task_id,
                    "skill": str(rel),
                    "strategy": strategy.strategy_id,
                    "prompt": str(prompt_path),
                    "output": str(out_skill) if args.call_openai else None,
                    "raw": str(raw_path) if raw_path else None,
                    "audit": audit,
                }
            )

    manifest_path = args.out_root / strategy.strategy_id / "rewrite_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
