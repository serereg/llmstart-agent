#!/usr/bin/env python3
"""Build full extracted dataset JSONL from curated records."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "datasets" / "v1" / "extracted"

# Additional records beyond sample.jsonl (approved 2026-06-28)
ADDITIONAL_RECORDS: list[dict] = [
    {
        "id": "ext-0014-03",
        "input": [
            {
                "role": "user",
                "content": "Добрый день. Заинтересовал комбо курс. Скажите, какой формат у курсов? Можно будет проходить в свое удобное время? Или есть какое-то расписание? Не могу найти его на сайте.",
            },
            {"role": "assistant", "content": "[ответ о формате комбо]"},
            {
                "role": "user",
                "content": "ИТ разработка, в основном в области ИИ. Но код сам не пишу. Ближе к CPO. В целом руку набить на инструменте хочу, чтото сам прототипировать.",
            },
            {"role": "assistant", "content": "[рекомендация комбо]"},
            {"role": "user", "content": "Спасибо сегодня ознакомлюсь и решу"},
        ],
        "expected_output": "Принять отложенное решение без давления; зафиксировать лид (save_lead); кратко напомнить следующий шаг (ссылка на комбо, вебинары); предложить задать вопросы.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0014", "message_indices": [8]},
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "deferred_decision"},
            "dataset_type": "T4",
            "abilities": ["S4", "S8"],
            "ground_truth_mode": "rubric",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [{"name": "save_lead", "args": {"interest": "ai-agents-combo"}}],
            "rubric": [
                {"id": "no_pressure", "description": "Без давления на немедленную покупку", "required": True},
                {"id": "saves_lead", "description": "Фиксирует интерес / контакт", "required": True},
                {"id": "clear_next_step", "description": "Даёт понятный следующий шаг", "required": True},
            ],
            "expert_reference": "Если появятся вопросы, задавайте, пожалуйста.",
            "notes": "В диалоге эксперт отправил вебинары — агент может предложить материалы из KB.",
        },
    },
    {
        "id": "ext-0014-04",
        "input": [
            {
                "role": "user",
                "content": "Добрый день. Заинтересовал комбо курс. Скажите, какой формат у курсов? Можно будет проходить в свое удобное время? Или есть какое-то расписание? Не могу найти его на сайте.",
            },
            {"role": "assistant", "content": "[ответ о формате комбо]"},
        ],
        "expected_output": "После информационного ответа задать квалификационный вопрос: профиль, цели, задачи — чтобы подобрать продукт.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0014", "message_indices": [3]},
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "proactive_qualification"},
            "dataset_type": "T2",
            "abilities": ["S1"],
            "ground_truth_mode": "expert_dialog",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [],
            "rubric": [
                {
                    "id": "asks_goals_or_profile",
                    "description": "Спрашивает о целях, профиле или опыте",
                    "required": True,
                }
            ],
            "expert_reference": "Подскажите, пожалуйста, а какой у вас профиль деятельности? Чем занимаетесь? Какие цели задачи?",
            "notes": "Поведение эксперта после info-ответа — эталон для агента.",
        },
    },
    {
        "id": "ext-0014-05",
        "input": [
            {
                "role": "user",
                "content": "Добрый день. Заинтересовал комбо курс. Скажите, какой формат у курсов? Можно будет проходить в свое удобное время? Или есть какое-то расписание? Не могу найти его на сайте.",
            },
            {"role": "assistant", "content": "[диалог: формат, квалификация, рекомендация]"},
            {"role": "user", "content": "Спасибо сегодня ознакомлюсь и решу"},
            {"role": "assistant", "content": "[пауза 2 дня]"},
            {
                "role": "assistant",
                "content": "Подскажите, есть ли вопросы еще? Удалось ознакомиться?",
            },
        ],
        "expected_output": "Мягкий follow-up после паузы: спросить о решении/вопросах; не давить; предложить помощь.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0014", "message_indices": [9]},
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "outbound_followup"},
            "dataset_type": "T4",
            "abilities": ["S4", "S8"],
            "ground_truth_mode": "expert_dialog",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [],
            "rubric": [
                {"id": "soft_tone", "description": "Мягкий тон без давления", "required": True},
                {"id": "asks_status", "description": "Уточняет статус решения или вопросы", "required": True},
            ],
            "expert_reference": "Подскажите, есть ли вопросы еще? Удалось ознакомиться?",
            "notes": "Outbound nurturing — контекст предыдущих сообщений в input.",
        },
    },
    {
        "id": "ext-0020-04",
        "input": [
            {"role": "user", "content": "Привет. У меня вопрос про интенсив. По каким дням и во сколько семинары?"},
            {"role": "assistant", "content": "[расписание интенсива]"},
            {"role": "assistant", "content": "Подскажите, пожалуйста, чем привлек интенсив?"},
            {
                "role": "user",
                "content": "Привет. Ну я давно хотел попробовать курсор. Я много чего делаю с ИИ, но вообще не программист. Но мне не подходит по формату затрат времени — я не смогу потратить рабочую пятницу на звонок.",
            },
        ],
        "expected_output": "Признать мотивацию (Cursor, интерес к ИИ); учесть профиль non-programmer; предложить workaround (запись, сдвиг времени, чат) до жёсткого отказа.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0020", "message_indices": [3]},
            "segment": "b2c",
            "taxonomy": {"group": "G3", "subcategory": "time_conflict_work_hours"},
            "dataset_type": "T3",
            "abilities": ["S1", "S4"],
            "ground_truth_mode": "rubric",
            "product_ids": ["vibe-coding-intensive"],
            "expected_tools": [],
            "rubric": [
                {"id": "acknowledges_motivation", "description": "Учитывает мотивацию Cursor/ИИ", "required": True},
                {"id": "offers_flexibility", "description": "Предлагает гибкость по времени или записи", "required": True},
                {"id": "addresses_non_programmer", "description": "Учитывает что не программист", "required": False},
            ],
            "expert_reference": "будет запись созвона... финальный разбор можем сдвинуть на более удобное время",
            "notes": None,
        },
    },
    {
        "id": "ext-0020-05",
        "input": [
            {"role": "user", "content": "Привет. У меня вопрос про интенсив. По каким дням и во сколько семинары?"},
            {"role": "assistant", "content": "[расписание]"},
            {"role": "assistant", "content": "Чем привлек интенсив?"},
            {
                "role": "user",
                "content": "Ну я давно хотел попробовать курсор. Я много чего делаю с ИИ, но вообще не программист. Но мне не подходит по формату затрат времени — я не смогу потратить рабочую пятницу на звонок.",
            },
        ],
        "expected_output": "Рекомендовать vibe-coding-intensive как вход для знакомства с Cursor; подчеркнуть что курс рассчитан на AI-driven работу без глубокого бэкграунда в коде (если соответствует KB).",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0020", "message_indices": [3]},
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "qualification_response_fit"},
            "dataset_type": "T2",
            "abilities": ["S2", "S6"],
            "ground_truth_mode": "rubric",
            "product_ids": ["vibe-coding-intensive"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [
                {"id": "maps_to_intensive", "description": "Связывает запрос с интенсивом Cursor", "required": True},
                {"id": "addresses_persona", "description": "Учитывает non-programmer + AI user", "required": True},
            ],
            "expert_reference": "чем привлек интенсив? → мотивация Cursor, не программист",
            "notes": None,
        },
    },
    {
        "id": "ext-0020-06",
        "input": [
            {
                "role": "user",
                "content": "[ранее: отказ от текущего потока из-за рабочей пятницы и отказа от записи]",
            },
            {
                "role": "assistant",
                "content": "У нас в субботу новый поток — улучшенная программа интенсива по AI-driven разработке в Cursor. Разрабатываем ИИ-агентов с выпускным проектом. Первый урок в выходной день. Подробности и оплата на llmstart.ru",
            },
        ],
        "expected_output": "Re-engagement с учётом прошлого барьера: акцент на субботу/выходной; кратко новая программа; CTA на llmstart.ru; не повторять отказанный формат (пятница днём).",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0020", "message_indices": [8]},
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "re_engagement_adapted_offer"},
            "dataset_type": "T4",
            "abilities": ["S4", "S7"],
            "ground_truth_mode": "rubric",
            "product_ids": ["vibe-coding-intensive"],
            "expected_tools": [{"name": "create_payment_link", "args": {"product_id": "vibe-coding-intensive"}}],
            "rubric": [
                {"id": "addresses_prior_barrier", "description": "Учитывает прошлый барьер по расписанию", "required": True},
                {"id": "weekend_slot", "description": "Акцент на выходной/удобное время", "required": True},
                {"id": "has_cta", "description": "Есть CTA (ссылка/оплата)", "required": True},
            ],
            "expert_reference": "новый поток в субботу... Первый главный онлайн-урок в выходной день. Подробности и оплата на llmstart.ru",
            "notes": None,
        },
    },
    {
        "id": "ext-0070-03",
        "input": [
            {
                "role": "user",
                "content": "Если больше внимания уделите веб-разработке (в частности фронтенду) - было бы идеально",
            },
        ],
        "expected_output": "Поблагодарить за фидбэк; подтвердить что пожелание учтено; при возможности связать с модулями fullstack/combo; не обещать несуществующий продукт.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0070", "message_indices": [5]},
            "segment": "b2c",
            "taxonomy": {"group": "G6", "subcategory": "curriculum_feedback"},
            "dataset_type": "T2",
            "abilities": ["S4", "S5"],
            "ground_truth_mode": "rubric",
            "product_ids": ["fullstack-aidd"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"query": "веб фронтенд"}}],
            "rubric": [
                {"id": "acknowledges_feedback", "description": "Благодарит и принимает фидбэк", "required": True},
                {"id": "no_false_promise", "description": "Не обещает отдельный веб-курс если его нет", "required": True},
            ],
            "expert_reference": "Понятно) попробуем учесть спасибо",
            "notes": "Агент может дать больше контекста из KB чем эксперт.",
        },
    },
    {
        "id": "ext-0070-04",
        "input": [
            {
                "role": "user",
                "content": "У фронта проблема для меня в том, что это сложная область. Периодически компоненты переиспользуются. Если генерить с 0 страницу - получается много кода. Покомпонентно как-то это сложнее",
            },
        ],
        "expected_output": "Эмпатия к pain point; связать с тем как курс/методика помогает с компонентным подходом и AI-кодингом; опционально уточняющий вопрос.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0070", "message_indices": [6]},
            "segment": "b2c",
            "taxonomy": {"group": "G6", "subcategory": "pain_point_frontend"},
            "dataset_type": "T2",
            "abilities": ["S1", "S5"],
            "ground_truth_mode": "rubric",
            "product_ids": ["agents", "fullstack-aidd"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {}}],
            "rubric": [
                {"id": "empathy", "description": "Признаёт проблему пользователя", "required": True},
                {"id": "links_to_course_value", "description": "Связывает с ценностью курса/методики", "required": False},
            ],
            "expert_reference": "Понятно) попробуем учесть спасибо",
            "notes": "Improvement: агент должен глубже ответить на боль.",
        },
    },
    {
        "id": "ext-0070-05",
        "input": [
            {
                "role": "assistant",
                "content": "Вы видели наш оффер на 2026 год? В нем включена веб-разработка",
            },
            {
                "role": "user",
                "content": "Добрый день! Спасибо за предложение. Я уже разобрался но думаю что многие заинтересуются модулем по веб-разработке.",
            },
        ],
        "expected_output": "Принять статус self-resolved без давления; поблагодарить за сигнал о спросе на веб-модуль; не настаивать на продаже.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0070", "message_indices": [9]},
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "self_resolved_lead"},
            "dataset_type": "T4",
            "abilities": ["S4"],
            "ground_truth_mode": "rubric",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [],
            "rubric": [
                {"id": "accepts_status", "description": "Принимает что пользователь уже решил задачу", "required": True},
                {"id": "no_hard_sell", "description": "Без повторного питча", "required": True},
                {"id": "thanks_for_signal", "description": "Благодарит за продуктовый сигнал", "required": False},
            ],
            "expert_reference": None,
            "notes": "В диалоге ответа эксперта нет — эталон для агента.",
        },
    },
    {
        "id": "ext-0110-03",
        "input": [
            {
                "role": "user",
                "content": "Здравствуйте. нашел ссылку на ваш курс. подскажите в каком формате проходят занятия?",
            },
        ],
        "expected_output": "Объяснить формат: запись 2025 vs онлайн 2026 в комбо; эфиры и задания.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0110", "message_indices": [0]},
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "format_only"},
            "dataset_type": "T1",
            "abilities": ["S3"],
            "ground_truth_mode": "expert_dialog",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c"}}],
            "rubric": [
                {"id": "explains_online_vs_record", "description": "Различает запись и онлайн", "required": True},
                {"id": "mentions_assignments", "description": "Упоминает задания/эфиры", "required": True},
            ],
            "expert_reference": "25 года в записи. Курсы 26 года в составе комбо предложения будут в онлайне. Эфиры и задания",
            "notes": None,
        },
    },
    {
        "id": "ext-0110-04",
        "input": [
            {
                "role": "user",
                "content": "все таки хочется посмотреть на какую то часть ваших уроков, что бы иметь представление, за что перечислять деньги, а не ждать возврата денежных средств. если все так хорошо, и вы уверены в качестве предоставляемого материала, то расшареная часть уроков, вам наоборот пойдет на пользу",
            },
        ],
        "expected_output": "Повторный запрос preview: описать программу/syllabus из KB; не отвечать только refund; предложить комбо с доступом к записи 2025 как альтернативу демо.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0110", "message_indices": [6]},
            "segment": "b2c",
            "taxonomy": {"group": "G4", "subcategory": "content_preview_repeat"},
            "dataset_type": "T3",
            "abilities": ["S5"],
            "ground_truth_mode": "rubric",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {}}],
            "rubric": [
                {"id": "addresses_preview", "description": "Отвечает на запрос материала/описания", "required": True},
                {"id": "refund_not_primary", "description": "Refund не единственный аргумент", "required": True},
            ],
            "expert_reference": "Хорошо я подумаю. Просто ссылку не дать.",
            "notes": "Improvement over expert deferral.",
        },
    },
    {
        "id": "ext-0110-05",
        "input": [
            {
                "role": "user",
                "content": "зачем вам моя цель? вам надо привлечь меня, чтобы я заплатил вам порядочную сумму",
            },
        ],
        "expected_output": "Объяснить взаимную квалификацию честно; привести пример misfit (новичок без кода → агенты); не уходить только в отзывы.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0110", "message_indices": [10]},
            "segment": "b2c",
            "taxonomy": {"group": "G5", "subcategory": "mutual_fit_honesty"},
            "dataset_type": "T2",
            "abilities": ["S6"],
            "ground_truth_mode": "expert_dialog",
            "product_ids": ["ai-agents-combo", "agents"],
            "expected_tools": [],
            "rubric": [
                {"id": "explains_fit_rationale", "description": "Объясняет зачем квалификация", "required": True},
                {"id": "misfit_example", "description": "Приводит пример несоответствия уровня", "required": True},
                {"id": "no_hard_sell", "description": "Не давит на покупку", "required": True},
            ],
            "expert_reference": "чтобы я был уверен, что наши продукты вам подходят... не умеет читать код... стартовый уровень выше",
            "notes": None,
        },
    },
    {
        "id": "ext-0110-06",
        "input": [
            {
                "role": "user",
                "content": "мне очень много лет и я в этом бизнесе очень давно. меня не привлекают картинки и отзывы. вам проще показать какой то материал, что бы я мог сделать вывод о том стоит ли мне платить или нет",
            },
        ],
        "expected_output": "Для experienced_skeptic: content-led ответ (syllabus, модули, результаты из KB); не полагаться на отзывы/TG; уточнить какой курс интересует.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0110", "message_indices": [15]},
            "segment": "b2c",
            "taxonomy": {"group": "G4", "subcategory": "social_proof_rejection"},
            "dataset_type": "T3",
            "abilities": ["S5"],
            "ground_truth_mode": "rubric",
            "product_ids": ["ai-agents-combo"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {}}],
            "rubric": [
                {"id": "no_social_proof_only", "description": "Не отвечает только отзывами", "required": True},
                {"id": "content_led", "description": "Даёт содержательное описание программы", "required": True},
                {"id": "clarifies_product", "description": "Уточняет какой курс/продукт", "required": False},
            ],
            "expert_reference": "У нас несколько курсов. Вам из какого курса материал хочется увидеть?",
            "notes": "Частично хорошо — уточнение продукта; не хватает syllabus.",
        },
    },
    {
        "id": "ext-0127-02",
        "input": [
            {"role": "assistant", "content": "[КП на корпоративное обучение команды до 20 человек]"},
            {
                "role": "user",
                "content": "Добрый день! Прошу прощения, пропустила сообщение. Спасибо, направляю команде)",
            },
        ],
        "expected_output": "Поблагодарить; подтвердить получение; кратко предложить помощь при вопросах команды; B2B сегмент; без повторного полного КП.",
        "metadata": {
            "source_branch": "extraction",
            "source": {"chat_id": "CHAT_0127", "message_indices": [3]},
            "segment": "b2b",
            "taxonomy": {"group": "G8", "subcategory": "forwarded_to_team"},
            "dataset_type": "T5",
            "abilities": ["S1", "S4"],
            "ground_truth_mode": "rubric",
            "product_ids": [],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2b"}}],
            "rubric": [
                {"id": "thanks_and_ack", "description": "Благодарит и подтверждает", "required": True},
                {"id": "no_b2c_checkout", "description": "Не предлагает B2C оплату", "required": True},
            ],
            "expert_reference": None,
            "notes": "В диалоге нет ответа эксперта на это сообщение.",
        },
    },
]


def load_sample_records() -> list[dict]:
    sample_path = OUT_DIR / "sample.jsonl"
    records: list[dict] = []
    for line in sample_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    sample = load_sample_records()
    sample_ids = {r["id"] for r in sample}
    additional = [r for r in ADDITIONAL_RECORDS if r["id"] not in sample_ids]

    all_records = sample + additional
    # Stable sort by id
    all_records.sort(key=lambda r: r["id"])

    b2c = [r for r in all_records if r["metadata"]["segment"] == "b2c"]
    b2b = [r for r in all_records if r["metadata"]["segment"] == "b2b"]

    write_jsonl(OUT_DIR / "b2c.jsonl", b2c)
    write_jsonl(OUT_DIR / "b2b.jsonl", b2b)
    write_jsonl(OUT_DIR / "all.jsonl", all_records)

    print(f"b2c: {len(b2c)} records → {OUT_DIR / 'b2c.jsonl'}")
    print(f"b2b: {len(b2b)} records → {OUT_DIR / 'b2b.jsonl'}")
    print(f"all: {len(all_records)} records → {OUT_DIR / 'all.jsonl'}")

    # Coverage summary
    from collections import Counter

    groups = Counter(r["metadata"]["taxonomy"]["group"] for r in all_records)
    types = Counter(r["metadata"]["dataset_type"] for r in all_records)
    print("taxonomy:", dict(sorted(groups.items())))
    print("types:", dict(sorted(types.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
