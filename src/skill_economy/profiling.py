"""Local task and skill profiling.

The profiler intentionally uses only task metadata and original ``SKILL.md``
files. It does not inspect verifier outputs, solutions, agent trajectories, or
rewritten skills. This mirrors the leakage-control protocol used by the paper.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable


SECTION_ALIASES = {
    "overview": "overview",
    "introduction": "overview",
    "purpose": "purpose",
    "goal": "purpose",
    "when to use": "when_to_use",
    "usage": "when_to_use",
    "workflow": "workflow",
    "process": "workflow",
    "steps": "workflow",
    "procedure": "workflow",
    "quick start": "workflow",
    "api": "api_usage",
    "api usage": "api_usage",
    "tools": "api_usage",
    "commands": "api_usage",
    "examples": "examples",
    "example": "examples",
    "code": "examples",
    "code examples": "examples",
    "validation": "validation",
    "verification": "validation",
    "testing": "validation",
    "checks": "validation",
    "constraints": "constraints",
    "rules": "constraints",
    "important": "constraints",
    "critical": "constraints",
    "pitfalls": "pitfalls",
    "common pitfalls": "pitfalls",
    "troubleshooting": "troubleshooting",
    "errors": "troubleshooting",
    "best practices": "best_practices",
    "reference": "reference",
    "schema": "reference",
    "output": "output_contract",
    "output format": "output_contract",
    "input": "input_artifacts",
    "inputs": "input_artifacts",
    "data": "input_artifacts",
    "dependencies": "dependencies",
    "prerequisites": "dependencies",
}


DOMAIN_KEYWORDS = {
    "spreadsheet_office": [
        "excel",
        "xlsx",
        "spreadsheet",
        "financial",
        "finance",
        "office",
        "pptx",
        "pdf",
        "document",
        "report",
    ],
    "code_debug_build": [
        "build",
        "migration",
        "debug",
        "java",
        "erlang",
        "scala",
        "translation",
        "dependency",
        "fuzzing",
        "cve",
        "security",
        "ctf",
    ],
    "scientific_computing": [
        "science",
        "geophysics",
        "seismology",
        "astronomy",
        "materials",
        "chemistry",
        "quantum",
        "environmental",
        "lake",
        "earthquake",
        "crystallographic",
    ],
    "data_analysis_ml": [
        "data",
        "statistics",
        "analytics",
        "ml",
        "nlp",
        "causal",
        "anomaly",
        "search",
        "classification",
    ],
    "control_optimization": [
        "control",
        "optimization",
        "scheduling",
        "planning",
        "energy",
        "dispatch",
        "power",
        "vehicle",
        "hvac",
        "pddl",
    ],
    "media_multimodal": [
        "video",
        "audio",
        "image",
        "ocr",
        "vision",
        "speech",
        "multimodal",
        "ffmpeg",
        "dubbing",
    ],
    "web_visualization": [
        "web",
        "react",
        "threejs",
        "d3",
        "visual",
        "browser",
        "frontend",
        "performance",
        "3d",
    ],
    "domain_reasoning": [
        "travel",
        "game",
        "bgp",
        "legal",
        "citation",
        "taxonomy",
        "invoice",
        "manufacturing",
    ],
}


HEAVY_DOCKER_PATTERNS = {
    "huggingface_model_download": (r"snapshot_download|load_model\(|huggingface|transformers", 4),
    "playwright_browser_install": (r"playwright install|install-deps", 4),
    "large_office_suite": (r"libreoffice|gnumeric", 3),
    "media_stack": (r"\bffmpeg\b|openai-whisper|whisper", 2),
    "node_setup": (r"nodesource|apt-get install -y nodejs|npm install", 2),
    "heavy_python_stack": (r"torch|tensorflow|jax|rdkit|geopandas|opencv|pymatgen|scipy", 2),
    "external_curl_install": (r"curl .* sh|curl -LsSf|wget http|git clone", 1),
}


def approx_tokens(text: str) -> int:
    """Cheap language-agnostic token proxy used for skill-cost accounting."""

    ascii_words = re.findall(r"[A-Za-z0-9_./#:+-]+", text)
    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    return max(1, int(len(ascii_words) * 1.25 + non_ascii * 0.8))


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = (len(ordered) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return round(ordered[lo] * (1 - frac) + ordered[hi] * frac, 4)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.S)
    if not match:
        return {}, text
    fm_text = match.group(1)
    rest = text[match.end() :]
    frontmatter: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, rest


def markdown_headings(text: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.M):
        rows.append(
            {
                "level": len(match.group(1)),
                "text": match.group(2).strip(),
                "line": text[: match.start()].count("\n") + 1,
            }
        )
    return rows


def normalize_heading(heading: str) -> str:
    clean = re.sub(r"[:\[].*$", "", heading).strip().lower()
    clean = re.sub(r"^[0-9.\-\s]+", "", clean)
    clean = re.sub(r"\s+", " ", clean)
    if clean in SECTION_ALIASES:
        return SECTION_ALIASES[clean]
    for key, alias in SECTION_ALIASES.items():
        if key in clean:
            return alias
    if re.search(r"must|never|avoid|do not|warning", clean):
        return "constraints"
    if re.search(r"verify|validate|test|check", clean):
        return "validation"
    if re.search(r"example|snippet|sample", clean):
        return "examples"
    if re.search(r"install|dependency|setup", clean):
        return "dependencies"
    return "other"


def markdown_code_blocks(text: str) -> list[tuple[str, str]]:
    return [
        (lang.strip().lower(), block.strip())
        for lang, block in re.findall(r"```([a-zA-Z0-9_-]*)\n(.*?)```", text, flags=re.S)
    ]


def _count_pattern_lines(text: str, pattern: str) -> int:
    regex = re.compile(pattern, flags=re.I)
    return sum(1 for line in text.splitlines() if regex.search(line))


def _simple_toml_metadata(task_dir: Path) -> dict[str, Any]:
    toml_path = task_dir / "task.toml"
    text = toml_path.read_text(encoding="utf-8", errors="replace") if toml_path.exists() else ""
    difficulty = re.search(r'difficulty\s*=\s*"([^"]+)"', text)
    category = re.search(r'category\s*=\s*"([^"]+)"', text)
    tags_match = re.search(r"tags\s*=\s*\[(.*?)\]", text, flags=re.S)
    tags = re.findall(r'"([^"]+)"', tags_match.group(1)) if tags_match else []
    return {
        "difficulty": difficulty.group(1) if difficulty else None,
        "category": category.group(1) if category else None,
        "tags": tags,
    }


def classify_skill(row: dict[str, Any]) -> str:
    if row["code_token_ratio"] >= 0.35 or row["code_block_count"] >= 4:
        return "code_heavy_reference"
    if row["constraint_density"] >= 8 and row["validation_density"] >= 3:
        return "guardrail_validation"
    if row["workflow_density"] >= 8:
        return "workflow_recipe"
    if row["tokens"] <= 250:
        return "compact_description"
    if row["section_count"] >= 8:
        return "sectioned_manual"
    return "mixed_guidance"


def classify_domain(task: dict[str, Any]) -> str:
    parts = [
        task.get("task_id", ""),
        task.get("category") or "",
        task.get("difficulty") or "",
        " ".join(task.get("tags") or []),
        " ".join(task.get("skill_ids") or []),
    ]
    text = " ".join(parts).lower()
    scores = {
        domain: sum(1 for keyword in keywords if keyword.lower() in text)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    best, score = max(scores.items(), key=lambda item: item[1])
    return best if score > 0 else "other"


def token_bin(total_tokens: int) -> str:
    if total_tokens < 750:
        return "short"
    if total_tokens < 2000:
        return "medium"
    if total_tokens < 5000:
        return "long"
    return "very_long"


def docker_features(task_dir: Path) -> dict[str, Any]:
    dockerfile = task_dir / "environment" / "Dockerfile"
    text = dockerfile.read_text(encoding="utf-8", errors="replace") if dockerfile.exists() else ""
    risk = 0
    reasons: list[str] = []
    for name, (pattern, weight) in HEAVY_DOCKER_PATTERNS.items():
        if re.search(pattern, text, flags=re.I):
            risk += weight
            reasons.append(name)
    run_count = len(re.findall(r"^\s*RUN\b", text, flags=re.M))
    if run_count >= 8:
        risk += 1
        reasons.append("many_docker_run_steps")
    if len(text) > 6000:
        risk += 1
        reasons.append("large_dockerfile")
    if risk <= 2:
        band = "low"
    elif risk <= 5:
        band = "medium"
    else:
        band = "high"
    return {
        "docker_risk_score": risk,
        "docker_risk_band": band,
        "docker_risk_reasons": reasons,
        "docker_run_count": run_count,
        "dockerfile_exists": dockerfile.exists(),
    }


def iter_skill_files(tasks_root: Path) -> Iterable[tuple[Path, Path]]:
    for task_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
        skills_root = task_dir / "environment" / "skills"
        if not skills_root.exists():
            continue
        for skill_path in sorted(skills_root.glob("*/SKILL.md")):
            yield task_dir, skill_path


def profile_skill(task_dir: Path, skill_path: Path, project_root: Path) -> dict[str, Any]:
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = parse_frontmatter(text)
    headings = markdown_headings(body)
    normalized_sections = [normalize_heading(h["text"]) for h in headings]
    blocks = markdown_code_blocks(body)
    code_text = "\n".join(block for _, block in blocks)
    tokens = approx_tokens(text)
    code_tokens = approx_tokens(code_text) if code_text else 0
    description = frontmatter.get("description", "")
    row = {
        "task_id": task_dir.name,
        "skill_id": skill_path.parent.name,
        "path": str(skill_path.relative_to(project_root)),
        "tokens": tokens,
        "chars": len(text),
        "line_count": len(text.splitlines()),
        "has_frontmatter": bool(frontmatter),
        "has_name": bool(frontmatter.get("name")),
        "has_description": bool(description),
        "description_tokens": approx_tokens(description) if description else 0,
        "section_count": len(headings),
        "top_level_section_count": sum(1 for h in headings if h["level"] <= 2),
        "headings": [h["text"] for h in headings],
        "normalized_sections": normalized_sections,
        "unique_sections": sorted(set(normalized_sections)),
        "code_block_count": len(blocks),
        "code_languages": sorted(set(lang or "plain" for lang, _ in blocks)),
        "code_token_ratio": round(code_tokens / max(1, tokens), 4),
        "constraint_density": round(
            _count_pattern_lines(
                body,
                r"\b(must|never|do not|don't|avoid|critical|important|required|warning|pitfall)\b",
            )
            / max(1, tokens / 1000),
            4,
        ),
        "validation_density": round(
            _count_pattern_lines(body, r"\b(validate|verify|check|test|assert|expected|confirm|ensure)\b")
            / max(1, tokens / 1000),
            4,
        ),
        "workflow_density": round(
            _count_pattern_lines(body, r"^\s*(?:\d+\.|-)\s+|workflow|step|procedure|process")
            / max(1, tokens / 1000),
            4,
        ),
        "formula_density": round(
            _count_pattern_lines(
                body,
                r"formula|equation|threshold|invariant|schema|unit|coordinate|tie-break|[A-Za-z0-9_]\s*=\s*",
            )
            / max(1, tokens / 1000),
            4,
        ),
    }
    row["archetype"] = classify_skill(row)
    return row


def _aggregate_task(task_id: str, skill_rows: list[dict[str, Any]], task_dir: Path) -> dict[str, Any]:
    metadata = _simple_toml_metadata(task_dir)
    total_tokens = sum(skill["tokens"] for skill in skill_rows)
    weighted = lambda key: sum(skill[key] * skill["tokens"] for skill in skill_rows) / max(1, total_tokens)
    archetypes = Counter(skill["archetype"] for skill in skill_rows)
    unique_sections = sorted({section for skill in skill_rows for section in skill.get("unique_sections", [])})
    row = {
        "task_id": task_id,
        **metadata,
        "skill_count": len(skill_rows),
        "skill_ids": [skill["skill_id"] for skill in skill_rows],
        "total_skill_tokens": total_tokens,
        "avg_skill_tokens": round(mean([skill["tokens"] for skill in skill_rows]), 4) if skill_rows else 0,
        "dominant_archetype": archetypes.most_common(1)[0][0] if archetypes else "none",
        "archetype_counts": dict(archetypes),
        "unique_sections": unique_sections,
        "avg_code_token_ratio": round(weighted("code_token_ratio"), 4),
        "avg_validation_density": round(weighted("validation_density"), 4),
        "avg_constraint_density": round(weighted("constraint_density"), 4),
        "avg_formula_density": round(weighted("formula_density"), 4),
        "has_validation": "validation" in unique_sections,
        "has_constraints": "constraints" in unique_sections,
        "has_examples": "examples" in unique_sections,
        "has_api_usage": "api_usage" in unique_sections,
        "has_formulas": any(skill["formula_density"] > 0 for skill in skill_rows),
    }
    row["domain_group"] = classify_domain(row)
    row["token_bin"] = token_bin(total_tokens)
    row.update(docker_features(task_dir))
    return row


def profile_tasks(tasks_root: str | Path) -> dict[str, Any]:
    tasks_root = Path(tasks_root)
    project_root = tasks_root.parent
    skills = [profile_skill(task_dir, skill_path, project_root) for task_dir, skill_path in iter_skill_files(tasks_root)]
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for skill in skills:
        by_task[skill["task_id"]].append(skill)

    tasks = [
        _aggregate_task(task_id, rows, tasks_root / task_id)
        for task_id, rows in sorted(by_task.items())
    ]
    token_values = [skill["tokens"] for skill in skills]
    section_counts = Counter(section for skill in skills for section in skill["unique_sections"])
    archetypes = Counter(skill["archetype"] for skill in skills)
    summary = {
        "tasks_scanned": len(tasks),
        "skill_files": len(skills),
        "skills_per_task_mean": round(mean([task["skill_count"] for task in tasks]), 4) if tasks else 0,
        "skills_per_task_median": median([task["skill_count"] for task in tasks]) if tasks else 0,
        "skill_tokens_median": median(token_values) if token_values else 0,
        "skill_tokens_p25": _percentile(token_values, 0.25),
        "skill_tokens_p75": _percentile(token_values, 0.75),
        "skill_tokens_p90": _percentile(token_values, 0.90),
        "archetypes": dict(archetypes),
        "common_sections": dict(section_counts.most_common()),
    }
    return {"summary": summary, "tasks": tasks, "skills": skills}


def write_profile(profile: dict[str, Any], out_dir: str | Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "skill_structure_profile.json").write_text(
        json.dumps(profile, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (out_dir / "skill_structure_profile.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = sorted({key for row in profile["tasks"] for key in row})
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in profile["tasks"]:
            writer.writerow({key: json.dumps(value) if isinstance(value, (list, dict)) else value for key, value in row.items()})
    (out_dir / "skill_structure_profile.md").write_text(render_profile_markdown(profile), encoding="utf-8")


def render_profile_markdown(profile: dict[str, Any]) -> str:
    summary = profile["summary"]
    lines = [
        "# Skill Structure Profile",
        "",
        f"- Tasks scanned: {summary['tasks_scanned']}",
        f"- SKILL.md files: {summary['skill_files']}",
        f"- Skills/task mean: {summary['skills_per_task_mean']}",
        f"- Skills/task median: {summary['skills_per_task_median']}",
        f"- Skill tokens median: {summary['skill_tokens_median']}",
        f"- Skill token p25/p75/p90: {summary['skill_tokens_p25']} / {summary['skill_tokens_p75']} / {summary['skill_tokens_p90']}",
        "",
        "## Archetypes",
        "",
        "| archetype | skill files |",
        "|---|---:|",
    ]
    for name, count in Counter(summary["archetypes"]).most_common():
        lines.append(f"| {name} | {count} |")
    lines.extend(["", "## Common Sections", "", "| section | skill files |", "|---|---:|"])
    for name, count in Counter(summary["common_sections"]).most_common(20):
        lines.append(f"| {name} | {count} |")
    lines.extend(["", "## Task Panel", "", "| task | domain | skills | skill tokens | archetype | validation | constraints | api | docker risk |", "|---|---|---:|---:|---|---|---|---|---|"])
    for task in profile["tasks"]:
        lines.append(
            "| {task_id} | {domain_group} | {skill_count} | {total_skill_tokens} | "
            "{dominant_archetype} | {has_validation} | {has_constraints} | {has_api_usage} | "
            "{docker_risk_band} |".format(**task)
        )
    lines.append("")
    return "\n".join(lines)
