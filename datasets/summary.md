# Summary — validation dataset v1

> **Plan:** [dataset-plan.md](./dataset-plan.md)  
> **Дата закрытия:** 2026-06-28

---

## Что сделано

### Ветка 1 — извлечение (24 записи)

- Анализ 5 реальных чатов → [analysis-report.md](./analysis-report.md) (G1–G8)
- Флэттенинг: `scripts/flatten_dialogs.py`
- Извлечение Уровень 2: `scripts/build_extracted_dataset.py`
- Артефакты: `datasets/v1/extracted/` (`all.jsonl`, `b2c.jsonl`, `b2b.jsonl`)

### Ветка 2 — синтез (36 записей)

- Анализ KB `data/b2c/` (3 продукта: agents, llm-fundamentals, rag-workshop)
- Стратификация по матрице пробелов G1–G8
- Pilot 5 записей (блок A, T6) → апрув → полный объём
- Артефакты: `datasets/v1/synthesized/` + `scripts/build_synthesized_dataset.py`

### Release v1 (60 записей)

- Merge: `scripts/build_v1_dataset.py` → `datasets/v1/all.jsonl`
- Splits: `b2c.jsonl` (57), `b2b.jsonl` (3)
- Coverage: [v1/coverage-report.md](./v1/coverage-report.md) — все группы G1–G8 по целевым 12/12/8/4/4/4/12/4
- Validation sample 10%: [v1/validation-sample.md](./v1/validation-sample.md) — апрув 2026-06-28
- Структурная валидация: `scripts/validate_dataset.py` (9 JSONL)

---

## Ключевые решения

| Решение | Итог |
|---------|------|
| Гибрид extraction + synthesis | Реальные формулировки + закрытие T6/checkout/lead |
| Синтез только на KB-продуктах | Факты ground truth из `data/b2c/`; combo/intensive в extraction — rubric |
| consultation нет в KB | Сценарий syn-G2-03: курс + save_lead |
| B2B отдельно | `segment=b2b`, split `b2b.jsonl` |
| Формат ChatML | `datasets/schemas/dataset_record.py` |

---

## Покрытие способностей S1–S8

| Способность | Покрытие v1 |
|-------------|-------------|
| S1 B2B/B2C routing | T5, G8 |
| S2 Product fit | T2, G2/G5 |
| S3 RAG/FAQ | T1, G1 |
| S4 Objections | T3, G3/G4 |
| S5 Value/syllabus | T3, G4/G6 |
| S6 Fit-check | T2, G5 |
| S7 Checkout | **T6** (8 записей, синтез) |
| S8 save_lead | **T6** + T3/T4 (синтез + extraction) |

---

## DoD

| Критерий | Статус |
|----------|--------|
| Таксономия G1–G8 из анализа | ✅ |
| Извлечение из реальных диалогов | ✅ 24 |
| Синтез пробелов + баланс групп | ✅ 36 |
| Целевой объём ~60 | ✅ 60 |
| ChatML + metadata schema | ✅ |
| Coverage all groups | ✅ |
| Validation sample | ✅ |
| Прогон сильной моделью | 🔲 deferred |

---

## Скрипты (make-ready)

```bash
# из backend/
uv run python ../scripts/build_extracted_dataset.py
uv run python ../scripts/build_synthesized_dataset.py
uv run python ../scripts/build_v1_dataset.py
uv run python ../scripts/validate_dataset.py
```

---

## Не в scope v1 (roadmap)

- Guardrails / security dataset
- Мультимодальность (чеки, фото)
- SGR-автогенерация синтеза (записи курированы вручную)
- Baseline eval сильной моделью
- Расширение KB под полный каталог project-draft (combo, intensive, deep-agents)
