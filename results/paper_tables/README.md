# Paper Tables

These CSV files contain compact aggregate values reported in the paper.

- `main_results.csv`: Table 3 style quality-cost results for the held-out panel and frozen-policy cross-model transfer.
- `ablation_and_transfer.csv`: Table 4 style ablations and transfer rows.

Column abbreviations:

- `QR`: quality retention relative to original skills.
- `rs`: direct skill-token cost ratio.
- `ra`: downstream agent-token cost ratio.
- `rho`: total cost ratio.
- `EO`: execution-overrun penalty.
- `delta`: downstream execution-cost change, `ra - 1`.
- `NLD`: near-lossless dividend.
