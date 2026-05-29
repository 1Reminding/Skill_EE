# Reproducibility Notes

This repository is a compact reproduction package for the paper method. It is not the full raw experiment workspace.

## Required External Inputs

For end-to-end evaluation you need:

- A SkillsBench/Harbor-compatible task directory layout.
- An agent runner that records verifier scores and token usage.
- An OpenAI-compatible model endpoint if you want to regenerate rewrites.

The code assumes tasks look like:

```text
tasks/<task-id>/
  instruction.md
  task.toml
  environment/
    Dockerfile
    skills/<skill-id>/SKILL.md
  tests/
  solution/
```

## Leakage Control

The profiling and policy-selection stages should use only:

- task id, task metadata, category, tags;
- original `environment/skills/**/SKILL.md` files;
- skill structural features computed before execution.

Do not use held-out verifier scores, generated solutions, trial logs, or token usage when selecting a strategy for a held-out task. Economic outcomes are used only for calibration/policy learning.

## Suggested End-to-End Order

1. Profile original skills:

```bash
python scripts/profile_tasks.py --tasks-root tasks --out-dir results/skill_structure_profile
```

2. Generate rewrites for each strategy:

```bash
for strategy in api_code rule_formula workflow; do
  python scripts/rewrite_skills.py \
    --tasks-root tasks \
    --task-list configs/splits/heldout_20.txt \
    --strategy "$strategy" \
    --out-root work/rewrites \
    --call-openai
done
```

3. Materialize fixed-strategy and policy-selected variants. The provided script materializes policy-selected variants; fixed-strategy variants can be evaluated directly from `work/rewrites/<strategy>/` by copying only skill files into task copies.

4. Run the agent/verifier harness. Each condition must keep task instructions, environments, and verifiers fixed; only skill documents may differ.

5. Aggregate observations:

```bash
python scripts/compute_metrics.py --observations path/to/task_level_observations.csv
```

6. Optionally relearn the selector from calibration observations:

```bash
python scripts/learn_policy.py \
  --observations path/to/calibration_observations.csv \
  --profile results/skill_structure_profile/skill_structure_profile.json \
  --out configs/policies/learned_policy.json
```

## Observation Schema

`scripts/compute_metrics.py` accepts CSV or JSON rows. Useful columns are:

- `task_id`
- `agent_stack`
- `condition` or `strategy`
- `partial` or `partial_test_score`
- `reward`
- `skill_tokens` or `total_skill_tokens`
- `agent_tokens`, `api_total_tokens`, or `effective_agent_tokens`

Rows whose condition is `baseline`, `original`, or `original skills` are used as task-local denominators.

## Paper Tables

The aggregate values used for the paper-facing summary are included in:

- `results/paper_tables/main_results.csv`
- `results/paper_tables/ablation_and_transfer.csv`

These CSVs are lightweight summaries, not raw run logs.
