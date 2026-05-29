# Skill Structure Profile

- Tasks scanned: 88
- Tasks with skills: 88
- SKILL.md files: 231
- Skills/task mean: 2.625, median: 2.0, max: 7
- Skill tokens median: 828, p25-p75: 499.0 - 1348.5, p90: 1942.0
- Frontmatter/name/description rates: 0.9957 / 0.9957 / 0.9957

## Archetypes

| archetype | skill files |
|---|---:|
| code_heavy_reference | 173 |
| workflow_recipe | 40 |
| compact_description | 11 |
| mixed_guidance | 4 |
| sectioned_manual | 3 |

## Common Normalized Sections

| section | skill files |
|---|---:|
| other | 226 |
| workflow | 109 |
| overview | 97 |
| input_artifacts | 94 |
| when_to_use | 91 |
| examples | 87 |
| output_contract | 72 |
| validation | 71 |
| best_practices | 66 |
| constraints | 63 |
| dependencies | 62 |
| reference | 60 |
| api_usage | 49 |
| pitfalls | 29 |
| troubleshooting | 29 |
| purpose | 12 |

## Common Raw Headings

| heading | count |
|---|---:|
| overview | 92 |
| best practices | 62 |
| python | 52 |
| quick start | 32 |
| usage | 31 |
| when to use | 27 |
| common pitfalls | 25 |
| dependencies | 25 |
| extract text | 22 |
| merge pdfs | 22 |
| rotate pages | 22 |
| common issues | 22 |
| quick reference | 19 |
| installation | 18 |
| limitations | 17 |
| when to use this skill | 16 |
| workflow | 16 |
| code style guidelines | 16 |
| notes | 16 |
| requirements for outputs | 15 |

## Skill Token Outliers

| task | skill | tokens | archetype | path |
|---|---|---:|---|---|
| citation-check | citation-management | 5172 | code_heavy_reference | `tasks\citation-check\environment\skills\citation-management\SKILL.md` |
| exceltable-in-ppt | pptx | 4473 | code_heavy_reference | `tasks\exceltable-in-ppt\environment\skills\pptx\SKILL.md` |
| organize-messy-files | pptx | 4473 | code_heavy_reference | `tasks\organize-messy-files\environment\skills\pptx\SKILL.md` |
| pptx-reference-formatting | pptx | 4473 | code_heavy_reference | `tasks\pptx-reference-formatting\environment\skills\pptx\SKILL.md` |
| flink-query | senior-data-engineer | 3286 | code_heavy_reference | `tasks\flink-query\environment\skills\senior-data-engineer\SKILL.md` |
| find-topk-similiar-chemicals | rdkit | 2985 | code_heavy_reference | `tasks\find-topk-similiar-chemicals\environment\skills\rdkit\SKILL.md` |
| setup-fuzzing-py | fuzzing-python | 2923 | code_heavy_reference | `tasks\setup-fuzzing-py\environment\skills\fuzzing-python\SKILL.md` |
| crystallographic-wyckoff-position-analysis | pymatgen | 2902 | code_heavy_reference | `tasks\crystallographic-wyckoff-position-analysis\environment\skills\pymatgen\SKILL.md` |
| fix-druid-loophole-cve | senior-java | 2866 | code_heavy_reference | `tasks\fix-druid-loophole-cve\environment\skills\senior-java\SKILL.md` |
| fix-build-agentops | uv-package-manager | 2808 | code_heavy_reference | `tasks\fix-build-agentops\environment\skills\uv-package-manager\SKILL.md` |
| pedestrian-traffic-counting | gpt-multimodal | 2748 | code_heavy_reference | `tasks\pedestrian-traffic-counting\environment\skills\gpt-multimodal\SKILL.md` |
| jpg-ocr-stat | openai-vision | 2686 | code_heavy_reference | `tasks\jpg-ocr-stat\environment\skills\openai-vision\SKILL.md` |
| dapt-intrusion-detection | pcap-analysis | 2570 | code_heavy_reference | `tasks\dapt-intrusion-detection\environment\skills\pcap-analysis\SKILL.md` |
| crystallographic-wyckoff-position-analysis | sympy | 2565 | code_heavy_reference | `tasks\crystallographic-wyckoff-position-analysis\environment\skills\sympy\SKILL.md` |
| setup-fuzzing-py | discover-important-function | 2527 | workflow_recipe | `tasks\setup-fuzzing-py\environment\skills\discover-important-function\SKILL.md` |

## Task Skill Counts

| task | skills | total tokens | category |
|---|---:|---:|---|
| video-silence-remover | 7 | 2366 | media-processing |
| fix-erlang-ssh-cve | 6 | 8415 | erlang bugfix |
| python-scala-translation | 6 | 7392 | Code Translation |
| multilingual-video-dubbing | 6 | 3284 | multimodal-video-dubbing |
| travel-planning | 6 | 476 | travel-planning |
| organize-messy-files | 5 | 10512 | file-management |
| jpg-ocr-stat | 5 | 9392 | data statistics |
| spring-boot-jakarta-migration | 5 | 5971 | Legacy Systems |
| exoplanet-detection-period | 5 | 5753 | astronomy |
| hvac-control | 5 | 2892 | control-systems |
| adaptive-cruise-control | 5 | 1681 | control-systems |
| pedestrian-traffic-counting | 4 | 7773 | pedestrian traffic counting |
| fix-build-agentops | 4 | 4572 | Compilation & Build |
| earthquake-phase-association | 4 | 4536 | seismology |
| speaker-diarization-subtitles | 4 | 3813 | audio-visual |
| seismic-phase-picking | 4 | 3702 | seismology |
| trend-anomaly-causal-inference | 4 | 3470 | data-science |
| civ6-adjacency-optimizer | 4 | 3246 | games |
| energy-market-pricing | 4 | 3034 | energy |
| pg-essay-to-audiobook | 4 | 2782 | speech-synthesis |

## Initial Template Implications

- Use `name`/`description` as mandatory metadata only if frontmatter is nearly universal.
- Search over broad section families rather than only fixed labels: workflow, api_usage, constraints, validation, examples, troubleshooting, reference.
- Avoid candidates that are extremely short or extremely verbose by applying token-ratio and archetype filters before Harbor.
- Stratify Harbor tasks by category/archetype coverage, not by convenience from one task family.
