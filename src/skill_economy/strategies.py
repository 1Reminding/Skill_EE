"""Rewrite strategy definitions and lightweight audits."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .profiling import approx_tokens, markdown_code_blocks


@dataclass(frozen=True)
class RewriteStrategy:
    """A preservation objective for rewriting ``SKILL.md`` files."""

    strategy_id: str
    title: str
    sections: tuple[str, ...]
    preservation_policy: str
    target_ratio: float
    max_anchor_blocks: int = 1
    max_anchor_chars: int = 2400


STRATEGIES: dict[str, RewriteStrategy] = {
    "source_native_compact": RewriteStrategy(
        strategy_id="source_native_compact",
        title="Source-native compacting",
        sections=(
            "YAML metadata",
            "Original section outline, merged only when redundant",
            "Operational details",
            "Validation and risks",
        ),
        preservation_policy=(
            "Preserve the source author's organization, local terminology, and "
            "operational details while removing redundant prose."
        ),
        target_ratio=0.72,
        max_anchor_blocks=1,
        max_anchor_chars=1800,
    ),
    "api_code": RewriteStrategy(
        strategy_id="api_code",
        title="API/code anchoring",
        sections=(
            "YAML metadata",
            "Capability and use cases",
            "Required artifacts",
            "API/tool patterns",
            "Implementation anchors",
            "Workflow",
            "Validation checks",
            "Pitfalls",
        ),
        preservation_policy=(
            "Preserve imports, API calls, object construction patterns, commands, "
            "minimal executable snippets, and non-obvious implementation details."
        ),
        target_ratio=0.82,
        max_anchor_blocks=2,
        max_anchor_chars=4200,
    ),
    "rule_formula": RewriteStrategy(
        strategy_id="rule_formula",
        title="Rule/formula anchoring",
        sections=(
            "YAML metadata",
            "When to use",
            "Exact definitions and invariants",
            "Decision rules or formulas",
            "Minimal implementation anchors",
            "Workflow",
            "Validation checks",
            "Failure modes",
        ),
        preservation_policy=(
            "Preserve coordinate conventions, formulas, thresholds, ranking rules, "
            "tie-breaks, schemas, units, constants, and compact examples that define correctness."
        ),
        target_ratio=0.78,
        max_anchor_blocks=2,
        max_anchor_chars=3600,
    ),
    "workflow": RewriteStrategy(
        strategy_id="workflow",
        title="Workflow guarding",
        sections=(
            "YAML metadata",
            "When to use",
            "Inputs and outputs",
            "Core workflow",
            "Tools and APIs",
            "Validation checks",
            "Pitfalls and constraints",
            "Compact examples",
        ),
        preservation_policy=(
            "Make ordered procedures, validation checks, constraints, failure modes, "
            "and recovery cues explicit and easy to follow."
        ),
        target_ratio=0.62,
        max_anchor_blocks=1,
        max_anchor_chars=2200,
    ),
}


STRATEGY_ALIASES = {
    "api_anchor_balanced": "api_code",
    "rule_formula_anchor": "rule_formula",
    "workflow_guarded": "workflow",
}


def normalize_strategy_id(strategy_id: str) -> str:
    return STRATEGY_ALIASES.get(strategy_id, strategy_id)


def get_strategy(strategy_id: str) -> RewriteStrategy:
    normalized = normalize_strategy_id(strategy_id)
    if normalized not in STRATEGIES:
        raise KeyError(f"Unknown rewrite strategy: {strategy_id}")
    return STRATEGIES[normalized]


def build_rewrite_prompt(original_skill: str, strategy: RewriteStrategy) -> str:
    """Build the conservative JSON-producing rewrite prompt."""

    section_list = "\n".join(f"- {section}" for section in strategy.sections)
    return f"""Rewrite the original SKILL.md using the specified strategy family.

Inputs:
- Strategy id: {strategy.strategy_id}
- Target sections:
{section_list}
- Preservation policy: {strategy.preservation_policy}
- Soft target compression ratio: {strategy.target_ratio}

Return one JSON object with these fields:
- rewritten_skill_md: the rewritten SKILL.md markdown.
- preserved_information: short list of anchors preserved.
- compressed_information: short list of prose or examples compressed.
- risk_flags: short list of possible missing anchors or ambiguity.

Rules:
- Preserve YAML metadata when present.
- Do not solve the task and do not invent facts.
- Preserve exact file types, API names, commands, class/function names, constants,
  formulas, validation thresholds, schemas, units, and do-not rules.
- Keep minimal executable code/API patterns when APIs are non-obvious.
- Keep coordinate systems, formulas, schemas, invariants, and validation checks for
  scientific or rule-governed skills.
- Use concise Markdown suitable for SKILL.md.

Original SKILL.md:
```markdown
{original_skill}
```
"""


def parse_rewrite_response(raw_text: str) -> dict[str, Any]:
    """Parse a model response that should contain a JSON object."""

    cleaned = raw_text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, flags=re.S)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def code_like_terms(text: str) -> set[str]:
    terms = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b", text))
    terms.update(re.findall(r"\b[A-Z][A-Za-z0-9_]{2,}\b", text))
    terms.update(re.findall(r"`([^`\n]{3,80})`", text))
    return {term.strip() for term in terms if len(term.strip()) >= 3}


def audit_rewrite(original_skill: str, rewritten_skill: str) -> dict[str, Any]:
    original_tokens = approx_tokens(original_skill)
    rewritten_tokens = approx_tokens(rewritten_skill)
    original_terms = code_like_terms(original_skill)
    rewritten_terms = code_like_terms(rewritten_skill)
    missing_terms = sorted(original_terms - rewritten_terms)
    original_blocks = markdown_code_blocks(original_skill)
    rewritten_blocks = markdown_code_blocks(rewritten_skill)
    return {
        "original_tokens": original_tokens,
        "rewritten_tokens": rewritten_tokens,
        "token_ratio": round(rewritten_tokens / max(1, original_tokens), 4),
        "original_code_blocks": len(original_blocks),
        "rewritten_code_blocks": len(rewritten_blocks),
        "code_term_coverage": round(1.0 - (len(missing_terms) / max(1, len(original_terms))), 4),
        "missing_code_terms": missing_terms[:30],
    }


def _anchor_score(block: str, original_skill: str) -> int:
    score = 0
    if re.search(r"\b(import|from|class|def|function|const|let|var|new |curl|python|pytest|npm)\b", block):
        score += 5
    if re.search(r"\b(must|critical|required|never|do not|assert|validate|verify|threshold)\b", block, re.I):
        score += 3
    if any(term in original_skill for term in code_like_terms(block)):
        score += 1
    return score


def select_anchor_blocks(original_skill: str, strategy: RewriteStrategy) -> list[str]:
    blocks = [block for _, block in markdown_code_blocks(original_skill)]
    scored = sorted((( _anchor_score(block, original_skill), block) for block in blocks), reverse=True)
    anchors: list[str] = []
    budget = strategy.max_anchor_chars
    for score, block in scored:
        if score <= 0 or len(anchors) >= strategy.max_anchor_blocks:
            continue
        snippet = block.strip()
        if len(snippet) > budget:
            snippet = snippet[:budget].rstrip()
        if snippet:
            anchors.append(snippet)
            budget -= len(snippet)
        if budget <= 0:
            break
    return anchors


def restore_missing_anchors(original_skill: str, rewritten_skill: str, strategy: RewriteStrategy) -> str:
    """Append compact source-derived anchors when code/API coverage is low."""

    audit = audit_rewrite(original_skill, rewritten_skill)
    needs_anchor = (
        audit["original_code_blocks"] > audit["rewritten_code_blocks"]
        or audit["code_term_coverage"] < 0.75
    )
    if not needs_anchor:
        return rewritten_skill
    anchors = select_anchor_blocks(original_skill, strategy)
    if not anchors:
        return rewritten_skill
    block_text = "\n\n".join(f"```text\n{anchor}\n```" for anchor in anchors)
    return rewritten_skill.rstrip() + "\n\n## Implementation Anchors\n\n" + block_text + "\n"


def write_strategy_config(path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: asdict(strategy) for key, strategy in STRATEGIES.items()}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
