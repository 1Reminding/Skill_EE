# Clean Main Economic Evidence

This report aggregates the completed clean-main evaluation. Economic metrics are not only post-hoc diagnostics: the learned policy was trained with a utility that includes quality retention, total cost ratio, quality-cost frontier, near-lossless dividend, and downstream inflation penalty.

## Utility Used For Policy Learning

- `partial`: 1.0
- `reward`: 0.15
- `retention`: 0.2
- `cost`: 0.3
- `frontier`: 0.2
- `near_lossless`: 0.2
- `inflation`: 0.15
- `win_bonus`: 0.05
- `near_lossless_eps`: 0.02

## Template-Level Results

| condition | jobs | valid | valid rate | partial | reward | total cost | cost ratio | retention | frontier | bang/token | near-lossless dividend | downstream inflation | econ utility |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `api_anchor_balanced` | 20 | 17 | 0.85 | 0.7921 | 0.4706 | 42252.1176 | 0.9745 | 0.8539 | -0.1956 | 0.9044 | -0.2121 | 0.4273 | 0.9037 |
| `baseline` | 20 | 18 | 0.9 | 0.8147 | 0.6111 | 42375.0 | None | None | None | None | None | None | 1.1063 |
| `policy_selected` | 20 | 19 | 0.95 | 0.8188 | 0.5658 | 37185.5789 | 0.9561 | 0.9038 | 0.0202 | 2.3175 | 0.1624 | 0.2415 | 1.0967 |
| `rule_formula_anchor` | 20 | 19 | 0.95 | 0.5546 | 0.3848 | 36964.5263 | 1.0501 | 0.6792 | -0.2279 | 0.9329 | 0.0745 | 0.2176 | 0.6966 |
| `workflow_guarded` | 20 | 19 | 0.95 | 0.7307 | 0.45 | 44690.3158 | 1.1037 | 0.9352 | -0.1559 | 0.8751 | -0.123 | 0.4837 | 0.9027 |

## Policy Pairwise Deltas

Positive deltas mean `policy_selected` is better than the comparison condition. Cost deltas are token counts, so lower is better and negative means cheaper.

| comparison | pairs | W/T/L partial | partial delta | reward delta | cost token delta | econ utility delta | frontier delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| policy vs `api_anchor_balanced` | 17 | 5/8/4 | 0.0447 | 0.1029 | -5866.1765 | 0.2388 | 0.2586 |
| policy vs `baseline` | 18 | 6/8/4 | -0.0009 | -0.0139 | -5205.9444 | -0.0096 | None |
| policy vs `rule_formula_anchor` | 18 | 7/8/3 | 0.2234 | 0.1493 | -1230.5 | 0.3807 | 0.2365 |
| policy vs `workflow_guarded` | 18 | 4/11/3 | 0.0375 | 0.0667 | -8189.0 | 0.1566 | 0.1316 |

## Interpretation For The Paper

- `quality_cost_frontier = quality_retention - total_cost_ratio` is the cleanest headline metric: it rewards preserving quality while reducing total cost.
- `near_lossless_dividend` is the practical cost-saving metric: token savings count only when quality is near-lossless.
- `downstream_inflation` is a failure-mode metric: a rewrite can shorten skills but cause more API reasoning, which should be penalized.
- The policy result is evidence that these metrics are actionable because they were used as selection signals and improved the fixed-template frontier.
