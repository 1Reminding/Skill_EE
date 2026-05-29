# Artifact Scope

The cleaned repository is designed for public release with an arXiv link.

## Included

- Core source code for the paper method.
- Configuration files for rewrite strategies and the frozen selector.
- Task split lists.
- Paper-level result tables.
- Diagnostic summaries from skill-structure profiling and held-out economic analysis.
- A small set of original and policy-selected skill examples.
- Final lightweight paper figures.

## Excluded

- Raw OpenAI/provider logs.
- Harbor run directories and full trajectories.
- Large task environments, video/audio/PDF/spreadsheet inputs, Docker build caches, and generated task variants.
- Exploratory scripts and old reports unrelated to the final paper story.
- Local `.env`, API proxy files, and ad hoc notebooks/tests.

## Why

The paper's main scientific claims depend on the controlled method and aggregate measurements, not on publishing every raw execution artifact. Keeping the repository compact makes it easier for readers to inspect the algorithm, rerun the pipeline on their own task checkout, and compare against the reported aggregate tables.
