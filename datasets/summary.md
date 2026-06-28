# Summary — validation dataset

> **Plan:** [dataset-plan.md](./dataset-plan.md)  
> **Analysis:** [analysis-report.md](./analysis-report.md)

---

## v1 — release ✅ 2026-06-28

### Что сделано

#### Ветка 1 — извлечение (24 записи)

- Анализ 5 реальных чатов → [analysis-report.md](./analysis-report.md) (G1–G8)
- Флэттенинг: `scripts/flatten_dialogs.py`
- Извлечение Уровень 2: `scripts/build_extracted_dataset.py`
- Артефакты: `datasets/v1/extracted/` (`all.jsonl`, `b2c.jsonl`, `b2b.jsonl`)

#### Ветка 2 — синтез (36 записей)

- Анализ KB `data/b2c/` (3 продукта: agents, llm-fundamentals, rag-workshop)
- Стратификация по матрице пробелов G1–G8
- Pilot 5 записей (блок A, T6) → апрув → полный объём
- Артефакты: `datasets/v1/synthesized/` + `scripts/build_synthesized_dataset.py`

#### Release v1 (60 записей)

- Merge: `scripts/build_v1_dataset.py` → `datasets/v1/all.jsonl`
- Splits: `b2c.jsonl` (57), `b2b.jsonl` (3)
- Coverage: [v1/coverage-report.md](./v1/coverage-report.md) — все группы G1–G8 по целевым 12/12/8/4/4/4/12/4
- Validation sample 10%: [v1/validation-sample.md](./v1/validation-sample.md) — апрув 2026-06-28
- Структурная валидация: `scripts/validate_dataset.py` (9 JSONL)

---

## v2 — guardrails / G9 ✅ 2026-06-28

| Шаг | Статус |
|-----|--------|
| Копия `datasets/v1/` → `datasets/v2/` | ✅ |
| Таксономия G9 в `analysis-report.md` | ✅ |
| Схема: T7, G9, S9 в `dataset_record.py` | ✅ |
| `datasets/v2/guardrails/all.jsonl` (12) | ✅ |
| `scripts/build_v2_dataset.py` | ✅ |
| Merge 72 + coverage + validation sample | ✅ |
| **v2 release** | ✅ |

**Объём:** 72 записи (69 b2c + 3 b2b).

**Новая способность S9:** отказ / redirect на in-scope; T7 rubric, `expected_tools = []`.

---

## Ключевые решения

| Решение | Итог |
|---------|------|
| Гибрид extraction + synthesis | Реальные формулировки + закрытие T6/checkout/lead |
| Синтез только на KB-продуктах | Факты ground truth из `data/b2c/`; combo/intensive в extraction — rubric |
| consultation нет в KB | Сценарий syn-G2-03: курс + save_lead |
| B2B отдельно | `segment=b2b`, split `b2b.jsonl` |
| Формат ChatML | `datasets/schemas/dataset_record.py` |
| v2 = immutable copy v1 + delta G9 | v1 не меняется; guardrails только в v2 |
| G9 только синтез | в реальных диалогах guardrails не встречались |
| G9 ≠ G5 misfit | G5 — про курсы, но не тот продукт; G9 — вне scope агента |

---

## Покрытие способностей

| Способность | v1 | v2 (план) |
|-------------|-----|-----------|
| S1 B2B/B2C routing | T5, G8 | без изменений |
| S2 Product fit | T2, G2/G5 | без изменений |
| S3 RAG/FAQ | T1, G1 | без изменений |
| S4 Objections | T3, G3/G4 | без изменений |
| S5 Value/syllabus | T3, G4/G6 | без изменений |
| S6 Fit-check | T2, G5 | без изменений |
| S7 Checkout | T6 (8 записей) | без изменений |
| S8 save_lead | T6 + T3/T4 | без изменений |
| **S9 Guardrails** | ❌ | **T7, G9 (12 записей)** ✅ |

---

## DoD

### v1

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

### v2

| Критерий | Статус |
|----------|--------|
| Копия v1 в `datasets/v2/` | ✅ |
| G9 таксономия + план | ✅ |
| 12 guardrails записей | ✅ |
| 72 записи merge + coverage | ✅ |
| Validation sample обновлён | ✅ |
| Schema T7/G9/S9 | ✅ |
| **v2 release** | ✅ 2026-06-28 |

---

## Скрипты (make-ready)

```bash
# v1
uv run python scripts/build_v1_dataset.py
uv run python scripts/validate_dataset.py

# v2 (после апрува и генерации G9)
uv run python scripts/build_v2_dataset.py
```

---

## Roadmap (не в scope v2)

- Мультимодальность (чеки, фото)
- SGR-автогенерация синтеза
- Baseline eval сильной моделью
- Смешанные «offtopic + in-scope» multi-turn (частично: syn-G9-05)
- Расширение KB под полный каталог project-draft (combo, intensive, deep-agents)
