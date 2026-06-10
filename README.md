# What Should a Skill Remember?

Core code and public artifacts for **[What Should a Skill Remember? Quality-Cost Trade-offs in Cost-Aware Skill Rewriting for Language Model Agents](https://arxiv.org/abs/2606.09421)**.

The project studies skill rewriting as cost-aware operational knowledge preservation. Instead of compressing every `SKILL.md` uniformly, it profiles task-skill structure, rewrites skills with strategy-specific preservation objectives, evaluates quality and cost under fixed task conditions, and learns a lightweight task-conditioned selector.

## What Is Included

This is the cleaned public repository prepared from the larger experiment workspace.

- Core algorithms for skill profiling, rewrite prompting/auditing, economic metrics, policy learning, and variant materialization.
- Strategy and policy configs used by the paper-facing pipeline.
- Task split files for calibration and held-out evaluation.
- Paper-level aggregate result tables and diagnostic summaries.
- Small original-vs-policy-selected skill rewrite examples.
- Final paper figures as lightweight PNG assets.

The original workspace also contained large task environments, raw provider logs, Harbor run directories, temporary notebooks/scripts, proxy tooling, and exploratory reports. Those are intentionally not copied here.

## Repository Layout

```text
src/skill_economy/
  profiling.py       # task/skill structural features from original SKILL.md files
  strategies.py      # rewrite strategy definitions, prompts, audits, anchor repair
  metrics.py         # QR, cost ratios, execution overrun, NLD, utility
  policy.py          # low-capacity task-conditioned strategy selector
  materialize.py     # controlled task copies with only skill files rewritten

scripts/
  profile_tasks.py
  rewrite_skills.py
  compute_metrics.py
  learn_policy.py
  materialize_policy_variants.py

configs/
  rewrite_strategies.json
  policies/frozen_selector.json
  splits/*.txt

results/
  paper_tables/*.csv
  diagnostics/*.md

examples/skill_rewrites/
  original and policy-selected SKILL.md excerpts for representative tasks
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

The tests cover the central economic metrics and the decision-list policy logic.

## Reproduction Workflow

Full agent execution requires a SkillsBench/Harbor-compatible task checkout. Place or symlink task directories under `tasks/`:

```bash
python scripts/profile_tasks.py --tasks-root tasks --out-dir results/skill_structure_profile
```

Generate rewrite prompts without calling a model:

```bash
python scripts/rewrite_skills.py \
  --tasks-root tasks \
  --task-list configs/splits/heldout_20.txt \
  --strategy api_code \
  --out-root work/rewrites
```

To generate rewritten skills with an OpenAI-compatible endpoint:

```bash
export OPENAI_API_KEY=...
export OPENAI_MODEL=...
python scripts/rewrite_skills.py --tasks-root tasks --task-list configs/splits/heldout_20.txt --strategy api_code --call-openai
```

Materialize policy-selected task variants after rewrites exist:

```bash
python scripts/materialize_policy_variants.py \
  --tasks-root tasks \
  --rewrites-root work/rewrites \
  --profile results/skill_structure_profile/skill_structure_profile.json \
  --policy configs/policies/frozen_selector.json \
  --task-list configs/splits/heldout_20.txt \
  --out-root work/task_variants/policy_selected
```

Agent execution and verifier runs are performed by Harbor or an equivalent SkillsBench runner. After collecting task-level observations, aggregate quality-cost metrics with:

```bash
python scripts/compute_metrics.py --observations path/to/observations.csv
```

## Main Result Artifacts

The paper-facing aggregate tables are in `results/paper_tables/`:

- `main_results.csv`: held-out and frozen cross-model quality-cost results.
- `ablation_and_transfer.csv`: objective ablations and policy transfer rows.

The headline held-out result is that policy-selected rewriting preserves verifier quality while reducing total cost (`rho = 0.93`) and downstream agent-token cost (`ra = 0.94`) on the 20-task balanced panel.

## Rewrite Strategies

The final policy arms are:

- `api_code`: preserve executable API, library, command, and object-construction anchors.
- `rule_formula`: preserve equations, schemas, units, thresholds, invariants, and domain conventions.
- `workflow`: preserve ordered procedures, validation checks, constraints, pitfalls, and recovery cues.

`source_native_compact` is retained as a diagnostic strategy but is not a final policy arm.

## Notes

- The full raw logs are excluded because they are large and contain provider-specific run metadata.
- The scripts only rewrite `environment/skills/**/SKILL.md`; task instructions, environments, solutions, and verifiers are left fixed for controlled evaluation.
- The selector uses only task metadata and original skill profiles before execution. It does not inspect held-out verifier outcomes or agent traces.

## Citation

Please cite the accompanying arXiv paper once available. A BibTeX entry will be added after the public identifier is assigned.
