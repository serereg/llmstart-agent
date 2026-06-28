# Validation dataset v2

> **Release:** ✅ 2026-06-28 — 72 записи (60 v1 + 12 G9 guardrails).

## Структура

```
v2/
├── extracted/          # копия v1 (24)
├── synthesized/        # копия v1 (36)
├── guardrails/         # all.jsonl (12, T7 / G9)
├── all.jsonl           # merge 72
├── b2c.jsonl (69) / b2b.jsonl (3)
├── coverage-report.md
└── validation-sample.md
```

## Сборка

```bash
cd backend && uv run python ../scripts/build_v2_dataset.py
cd backend && uv run python ../scripts/validate_dataset.py
```

## G9 subcategories

| Subcategory | Count |
|-------------|-------|
| offtopic_general | 3 |
| competitor_comparison | 2 |
| prompt_injection | 2 |
| toxic_abusive | 2 |
| professional_advice | 1 |
| service_outside_catalog | 2 |

План: [dataset-plan.md §11](../dataset-plan.md#11-v2--guardrails--g9--release-2026-06-28).
