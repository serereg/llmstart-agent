#!/usr/bin/env python3
"""Build full synthesized dataset JSONL from pilot + curated records."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "datasets" / "v1" / "synthesized"
PILOT_PATH = OUT_DIR / "pilot.jsonl"

SYNTH = {
    "source_branch": "synthesis",
    "source": None,
}

ADDITIONAL_RECORDS: list[dict] = [
    # --- G1 (+7) ---
    {
        "id": "syn-G1-01",
        "input": [{"role": "user", "content": "Расскажите про LLM Fundamentals — как проходит обучение? Это live или записи?"}],
        "expected_output": "Факты из KB: 4 недели; онлайн; видеолекции + квизы; уровень начальный; аудитория — разработчики без ML-опыта, PM, студенты.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "format_llm_fundamentals"},
            "dataset_type": "T1",
            "abilities": ["S3"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["llm-fundamentals"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c", "query": "llm-fundamentals формат"}}],
            "rubric": [
                {"id": "states_duration", "description": "4 недели", "required": True},
                {"id": "mentions_video_quizzes", "description": "Видеолекции + квизы", "required": True},
            ],
            "notes": "Persona: baseline.",
        },
    },
    {
        "id": "syn-G1-02",
        "input": [{"role": "user", "content": "RAG Workshop — это только записи или будут live-coding сессии? Сколько по времени?"}],
        "expected_output": "Из KB: 2 недели; live-coding сессии + проект; уровень intermediate; результат — свой RAG-пайплайн.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "format_rag_workshop"},
            "dataset_type": "T1",
            "abilities": ["S3"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["rag-workshop"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c", "query": "rag-workshop формат live-coding"}}],
            "rubric": [
                {"id": "live_coding", "description": "Упоминает live-coding", "required": True},
                {"id": "two_weeks", "description": "2 недели", "required": True},
            ],
        },
    },
    {
        "id": "syn-G1-03",
        "input": [{"role": "user", "content": "Курс Agents — сколько длится и какой формат занятий? Нужен ли опыт в ML?"}],
        "expected_output": "8 недель; онлайн с практическими ДЗ; intermediate; нужен базовый Python (не ML); ReAct, tools, RAG, observability, деплой.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "format_agents"},
            "dataset_type": "T1",
            "abilities": ["S3"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c", "query": "agents формат длительность"}}],
            "rubric": [
                {"id": "eight_weeks", "description": "8 недель", "required": True},
                {"id": "python_requirement", "description": "Базовый Python, не ML", "required": True},
            ],
        },
    },
    {
        "id": "syn-G1-04",
        "input": [{"role": "user", "content": "Записался на RAG Workshop — live-coding в какое время по МСК? Я сейчас в Лондоне."}],
        "expected_output": "Указать что точное расписание live-сессий уточняется; перевести типичное время в GMT/BST; предложить уточнить email/TG; не выдумывать конкретные даты.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "timezone_live_session"},
            "dataset_type": "T1",
            "abilities": ["S3"],
            "ground_truth_mode": "rubric",
            "product_ids": ["rag-workshop"],
            "expected_tools": [],
            "rubric": [
                {"id": "timezone_conversion", "description": "Учитывает часовой пояс пользователя", "required": True},
                {"id": "no_fabricated_schedule", "description": "Не выдумывает даты если их нет в KB", "required": True},
            ],
            "notes": "Improvement over ext-0020-03: конвертация timezone.",
        },
    },
    {
        "id": "syn-G1-05",
        "input": [{"role": "user", "content": "LLM Fundamentals можно проходить в своём темпе или строго по расписанию группы?"}],
        "expected_output": "Из KB: онлайн, видеолекции + квизы — подразумевает асинхронный темп; честно если нет жёсткого расписания live в KB.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "async_vs_sync"},
            "dataset_type": "T1",
            "abilities": ["S3"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["llm-fundamentals"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c", "query": "llm-fundamentals формат темп"}}],
            "rubric": [{"id": "flexible_pace", "description": "Подтверждает гибкий/видео формат", "required": True}],
        },
    },
    {
        "id": "syn-G1-06",
        "input": [{"role": "user", "content": "Когда следующий набор на курс Agents? Хочу успеть до конца года."}],
        "expected_output": "Честно: конкретных дат набора в KB может не быть; предложить save_lead для уведомления; кратко напомнить формат 8 недель.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "next_cohort"},
            "dataset_type": "T1",
            "abilities": ["S3", "S8"],
            "ground_truth_mode": "rubric",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "save_lead", "args": {}}],
            "rubric": [
                {"id": "no_false_dates", "description": "Не выдумывает дату набора", "required": True},
                {"id": "offers_notification", "description": "Предлагает уведомление/лид", "required": True},
            ],
        },
    },
    {
        "id": "syn-G1-07",
        "input": [{"role": "user", "content": "Я не программист вообще. Смогу пройти Agents или это не для меня по формату/уровню?"}],
        "expected_output": "Из KB: agents требует базовый Python, intermediate — для non-coder это барьер; честно предупредить; альтернатива llm-fundamentals (beginner).",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G1", "subcategory": "level_requirement"},
            "dataset_type": "T1",
            "abilities": ["S3", "S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents", "llm-fundamentals"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c"}}],
            "rubric": [
                {"id": "states_python_req", "description": "Упоминает требование базового Python", "required": True},
                {"id": "suggests_alternative", "description": "Предлагает llm-fundamentals для новичков", "required": True},
            ],
            "notes": "Persona: non-programmer.",
        },
    },
    # --- G2 (+6, pilot has A7+A9) ---
    {
        "id": "syn-G2-01",
        "input": [{"role": "user", "content": "Я продакт-менеджер, хочу понимать LLM для фич в продукте. Какой курс посоветуете?"}],
        "expected_output": "Рекомендовать llm-fundamentals: beginner, 4 недели, для PM и dev без ML; кратко agents если захочет углубиться в разработку агентов позже.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "pm_fit_llm_fundamentals"},
            "dataset_type": "T2",
            "abilities": ["S1", "S2", "S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["llm-fundamentals"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [
                {"id": "recommends_llm_fundamentals", "description": "Рекомендует llm-fundamentals для PM", "required": True},
                {"id": "addresses_persona", "description": "Учитывает PM без ML", "required": True},
            ],
            "notes": "Persona: product manager.",
        },
    },
    {
        "id": "syn-G2-02",
        "input": [{"role": "user", "content": "Python-разработчик, 3 года опыта. Хочу production AI-агентов — что из вашего каталога подойдёт?"}],
        "expected_output": "Рекомендовать agents: 8 недель, ReAct, tools, RAG, observability, FastAPI деплой; подтвердить fit по уровню intermediate + Python.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "dev_fit_agents"},
            "dataset_type": "T2",
            "abilities": ["S2", "S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [{"id": "recommends_agents", "description": "Рекомендует agents", "required": True}],
            "notes": "Persona: Python dev 3y.",
        },
    },
    {
        "id": "syn-G2-03",
        "input": [{"role": "user", "content": "Можно записаться на консультацию с экспертом перед покупкой курса?"}],
        "expected_output": "Честно: отдельного продукта consultation в B2C-каталоге KB нет; предложить agents или llm-fundamentals по цели; save_lead для связи с менеджером; list_b2c_products.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "consultation_request"},
            "dataset_type": "T2",
            "abilities": ["S2", "S8"],
            "ground_truth_mode": "rubric",
            "product_ids": ["agents", "llm-fundamentals"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}, {"name": "save_lead", "args": {}}],
            "rubric": [
                {"id": "no_fake_consultation_product", "description": "Не выдумывает consultation в каталоге", "required": True},
                {"id": "offers_alternative_path", "description": "Предлагает курс или контакт", "required": True},
            ],
        },
    },
    {
        "id": "syn-G2-04",
        "input": [{"role": "user", "content": "Сколько стоит RAG Workshop? Можно оплатить частями?"}],
        "expected_output": "От 19 900 ₽ из KB; рассрочку не обещать если нет в rag-workshop.md (честно); 2 недели live-coding; при интересе create_payment_link.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "direct_price_rag_workshop"},
            "dataset_type": "T1",
            "abilities": ["S2", "S3"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["rag-workshop"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c", "query": "rag-workshop стоимость"}}],
            "rubric": [
                {"id": "states_price", "description": "19 900 ₽", "required": True},
                {"id": "no_invented_installment", "description": "Не выдумывает рассрочку", "required": True},
            ],
            "notes": "Блок A8.",
        },
    },
    {
        "id": "syn-G2-05",
        "input": [{"role": "user", "content": "Я новичок в AI. LLM Fundamentals или сразу Agents — с чего начать?"}],
        "expected_output": "Сравнить: llm-fundamentals beginner 4 нед vs agents intermediate 8 нед + Python; для новичка → llm-fundamentals; agents после базы.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "beginner_path_comparison"},
            "dataset_type": "T2",
            "abilities": ["S2", "S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["llm-fundamentals", "agents"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [
                {"id": "recommends_fundamentals_first", "description": "Рекомендует llm-fundamentals новичку", "required": True},
                {"id": "accurate_levels", "description": "beginner vs intermediate", "required": True},
            ],
            "notes": "Блок A10.",
        },
    },
    {
        "id": "syn-G2-06",
        "input": [{"role": "user", "content": "Мне нужен только embeddings и vector search для MVP — есть отдельный короткий курс?"}],
        "expected_output": "Маппинг на rag-workshop: 2 недели, chunking, embeddings, vector stores, evaluation; не обещать отдельный micro-курс вне каталога.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G2", "subcategory": "narrow_rag_mapping"},
            "dataset_type": "T2",
            "abilities": ["S2", "S3"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["rag-workshop"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [{"id": "maps_to_rag_workshop", "description": "Предлагает rag-workshop", "required": True}],
        },
    },
    # --- G3 (+5) ---
    {
        "id": "syn-G3-01",
        "input": [{"role": "user", "content": "Agents интересен, но 8 недель — слишком долго при текущей загрузке. Может позже."}],
        "expected_output": "Признать барьер; без давления; save_lead с interest=agents; предложить уведомление о наборе или llm-fundamentals 4 нед как lighter option.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G3", "subcategory": "duration_objection"},
            "dataset_type": "T3",
            "abilities": ["S4", "S8"],
            "ground_truth_mode": "rubric",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "save_lead", "args": {"product": "agents", "segment": "b2c"}}],
            "rubric": [
                {"id": "no_pressure", "description": "Без давления", "required": True},
                {"id": "saves_or_defers", "description": "save_lead или defer", "required": True},
            ],
        },
    },
    {
        "id": "syn-G3-02",
        "input": [{"role": "user", "content": "14 900 за LLM Fundamentals — дорого для вводного курса. Есть смысл платить?"}],
        "expected_output": "Эмпатия; описать ценность из KB (трансформеры, промпты, OpenAI API, 4 нед); без выдуманных скидок; fit-check — спросить цель.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G3", "subcategory": "price_objection"},
            "dataset_type": "T3",
            "abilities": ["S4", "S5"],
            "ground_truth_mode": "rubric",
            "product_ids": ["llm-fundamentals"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c"}}],
            "rubric": [
                {"id": "value_from_kb", "description": "Аргументы из программы, не только цена", "required": True},
                {"id": "no_fake_discount", "description": "Без выдуманных скидок", "required": True},
            ],
        },
    },
    {
        "id": "syn-G3-03",
        "input": [{"role": "user", "content": "RAG Workshop хочу, но эти две недели заняты — перенесу на следующий месяц."}],
        "expected_output": "Принять отложенный старт; save_lead; кратко подтвердить формат; без CTA на немедленную оплату.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G3", "subcategory": "busy_deferred_start"},
            "dataset_type": "T3",
            "abilities": ["S4", "S8"],
            "ground_truth_mode": "rubric",
            "product_ids": ["rag-workshop"],
            "expected_tools": [{"name": "save_lead", "args": {}}],
            "rubric": [{"id": "accepts_defer", "description": "Принимает перенос", "required": True}],
        },
    },
    {
        "id": "syn-G3-04",
        "input": [{"role": "user", "content": "LLM Fundamentals — только видео? Мне важен live, иначе не дойду до конца."}],
        "expected_output": "Честно из KB: видеолекции + квизы, без live в описании; не обещать live; альтернатива rag-workshop (live-coding) если нужен sync.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G3", "subcategory": "sync_preference"},
            "dataset_type": "T3",
            "abilities": ["S4", "S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["llm-fundamentals", "rag-workshop"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c"}}],
            "rubric": [
                {"id": "honest_about_video", "description": "Честно про видеоформат", "required": True},
                {"id": "suggests_live_alternative", "description": "Предлагает rag-workshop если нужен live", "required": False},
            ],
        },
    },
    {
        "id": "syn-G3-05",
        "input": [{"role": "user", "content": "У других школ 2–3 созвона в неделю вечером. У вас Agents — как устроено? Боюсь что формат не подойдёт."}],
        "expected_output": "Описать реальный формат agents из KB (онлайн, ДЗ, 8 нед); не выдумывать частоту созвонов; эмпатия; save_lead или уточнить барьер.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G3", "subcategory": "format_comparison_bootcamps"},
            "dataset_type": "T3",
            "abilities": ["S3", "S4"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c"}}],
            "rubric": [{"id": "factual_format", "description": "Формат из KB без выдумок", "required": True}],
        },
    },
    # --- G4 (+1) ---
    {
        "id": "syn-G4-01",
        "input": [{"role": "user", "content": "Покажите программу курса Agents — что именно буду делать на практике? Без отзывов, нужен syllabus."}],
        "expected_output": "Content-led ответ из KB: ReAct, tool calling, RAG, Langfuse traces, деплой FastAPI; без video demo; refund не как единственный аргумент.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G4", "subcategory": "syllabus_preview"},
            "dataset_type": "T3",
            "abilities": ["S5"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c", "query": "agents программа syllabus"}}],
            "rubric": [
                {"id": "content_led", "description": "Описание модулей/навыков из KB", "required": True},
                {"id": "no_social_proof_only", "description": "Не только отзывы", "required": True},
            ],
        },
    },
    # --- G5 (+3) ---
    {
        "id": "syn-G5-01",
        "input": [{"role": "user", "content": "Хочу на Agents, но Python не знаю вообще. Всё равно записаться?"}],
        "expected_output": "Честный misfit: agents требует базовый Python; рекомендовать llm-fundamentals (beginner); не продавать agents любой ценой.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G5", "subcategory": "misfit_no_python"},
            "dataset_type": "T2",
            "abilities": ["S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents", "llm-fundamentals"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [
                {"id": "honest_misfit", "description": "Не рекомендует agents без Python", "required": True},
                {"id": "alternative_fundamentals", "description": "Альтернатива llm-fundamentals", "required": True},
            ],
            "notes": "Блок B1.",
        },
    },
    {
        "id": "syn-G5-02",
        "input": [{"role": "user", "content": "Мне нужны только промпты для ChatGPT, код не интересен. Agents подойдёт?"}],
        "expected_output": "Misfit для agents (код, ReAct, деплой); redirect llm-fundamentals (промпт-инжиниринг, API); честный fit-check.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G5", "subcategory": "prompts_only_misfit"},
            "dataset_type": "T2",
            "abilities": ["S6"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["llm-fundamentals", "agents"],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [{"id": "redirect_fundamentals", "description": "llm-fundamentals для промптов", "required": True}],
            "notes": "Блок B2.",
        },
    },
    {
        "id": "syn-G5-03",
        "input": [{"role": "user", "content": "29 900 за Agents — не уверен что потяну по уровню. Может зря потрачу."}],
        "expected_output": "Взаимная квалификация; описать уровень intermediate + Python; предложить llm-fundamentals если базы нет; без hard sell; save_lead опционально.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G5", "subcategory": "price_and_level_doubt"},
            "dataset_type": "T2",
            "abilities": ["S4", "S6"],
            "ground_truth_mode": "rubric",
            "product_ids": ["agents", "llm-fundamentals"],
            "expected_tools": [],
            "rubric": [
                {"id": "mutual_qualification", "description": "Объясняет fit-check", "required": True},
                {"id": "no_hard_sell", "description": "Без давления", "required": True},
            ],
            "notes": "Блок B3.",
        },
    },
    # --- G6 (+2) ---
    {
        "id": "syn-G6-01",
        "input": [{"role": "user", "content": "На Agents было бы здорово больше часов про RAG и evaluation — учтёте в программе?"}],
        "expected_output": "Поблагодарить за фидбэк; не обещать изменений; кратко что RAG уже в программе agents; rag-workshop как доп. углубление.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G6", "subcategory": "curriculum_feedback_rag"},
            "dataset_type": "T2",
            "abilities": ["S4", "S5"],
            "ground_truth_mode": "rubric",
            "product_ids": ["agents", "rag-workshop"],
            "expected_tools": [],
            "rubric": [{"id": "acknowledges_feedback", "description": "Принимает фидбэк", "required": True}],
            "notes": "Блок B4.",
        },
    },
    {
        "id": "syn-G6-02",
        "input": [{"role": "user", "content": "Планируете курс Deep Agents? Или agents уже покрывает продвинутую тему?"}],
        "expected_output": "Честно: deep-agents нет в B2C KB; agents — production-grade агенты (LangChain, ReAct, RAG, observability); не выдумывать roadmap deep-agents.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G6", "subcategory": "roadmap_deep_agents"},
            "dataset_type": "T2",
            "abilities": ["S3", "S5"],
            "ground_truth_mode": "kb_rag",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "search_knowledge_base", "args": {"audience": "b2c"}}],
            "rubric": [{"id": "no_hallucinated_product", "description": "Не выдумывает deep-agents в каталоге", "required": True}],
            "notes": "Блок B5.",
        },
    },
    # --- G7 (+5, pilot has A1-A3) ---
    {
        "id": "syn-G7-01",
        "input": [{"role": "user", "content": "Решил брать LLM Fundamentals. Пришлите ссылку на оплату, пожалуйста."}],
        "expected_output": "create_payment_link(product_id=llm-fundamentals); цена 14 900 ₽; кратко формат 4 недели.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "checkout_llm_fundamentals"},
            "dataset_type": "T6",
            "abilities": ["S7"],
            "ground_truth_mode": "tool_call",
            "product_ids": ["llm-fundamentals"],
            "expected_tools": [{"name": "create_payment_link", "args": {"product_id": "llm-fundamentals"}}],
            "rubric": [{"id": "correct_product", "description": "llm-fundamentals", "required": True}],
            "notes": "Блок A4.",
        },
    },
    {
        "id": "syn-G7-02",
        "input": [
            {"role": "user", "content": "Что входит в RAG Workshop?"},
            {"role": "assistant", "content": "[описание: 2 недели, chunking, embeddings, vector stores, 19 900 ₽]"},
            {"role": "user", "content": "Подходит, беру. Как оплатить?"},
        ],
        "expected_output": "Multi-turn: подтвердить выбор rag-workshop; create_payment_link(rag-workshop).",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "multi_turn_info_to_checkout"},
            "dataset_type": "T6",
            "abilities": ["S2", "S7"],
            "ground_truth_mode": "tool_call",
            "product_ids": ["rag-workshop"],
            "expected_tools": [{"name": "create_payment_link", "args": {"product_id": "rag-workshop"}}],
            "notes": "Блок A5.",
        },
    },
    {
        "id": "syn-G7-03",
        "input": [
            {"role": "user", "content": "Agents интересен, но куплю через месяц"},
            {"role": "assistant", "content": "[save_lead, без давления]"},
            {"role": "user", "content": "Вернулся — готов оплатить agents сейчас"},
        ],
        "expected_output": "Re-engagement; create_payment_link(agents); не повторять старые возражения.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "defer_return_checkout"},
            "dataset_type": "T6",
            "abilities": ["S7", "S8"],
            "ground_truth_mode": "tool_call",
            "product_ids": ["agents"],
            "expected_tools": [{"name": "create_payment_link", "args": {"product_id": "agents"}}],
            "notes": "Блок A6.",
        },
    },
    {
        "id": "syn-G7-04",
        "input": [
            {"role": "user", "content": "Сколько стоит agents?"},
            {"role": "assistant", "content": "[29 900 ₽, рассрочка, 8 недель]"},
            {"role": "user", "content": "Ок, беру"},
            {"role": "assistant", "content": "[create_payment_link agents]"},
            {"role": "user", "content": "Оплатил"},
            {"role": "assistant", "content": "[confirm_payment]"},
            {"role": "user", "content": "Мария, maria@example.com — для доступа"},
        ],
        "expected_output": "Happy path: save_lead(name=Мария, contact=maria@example.com, product=agents, segment=b2c) после оплаты.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "full_funnel_paid_lead"},
            "dataset_type": "T6",
            "abilities": ["S7", "S8"],
            "ground_truth_mode": "tool_call",
            "product_ids": ["agents"],
            "expected_tools": [
                {
                    "name": "save_lead",
                    "args": {
                        "name": "Мария",
                        "contact": "maria@example.com",
                        "product": "agents",
                        "segment": "b2c",
                    },
                }
            ],
            "rubric": [{"id": "saves_after_payment", "description": "save_lead после оплаты", "required": True}],
            "notes": "Блок A11. Контакт — плейсхолдер.",
        },
    },
    {
        "id": "syn-G7-05",
        "input": [{"role": "user", "content": "Пока не готов покупать. Напишите когда откроете набор на agents — email notify@example.com, зовут Иван."}],
        "expected_output": "save_lead без create_payment_link; без давления; подтвердить что уведомят о наборе.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G7", "subcategory": "notify_only_lead"},
            "dataset_type": "T6",
            "abilities": ["S8"],
            "ground_truth_mode": "tool_call",
            "product_ids": ["agents"],
            "expected_tools": [
                {
                    "name": "save_lead",
                    "args": {
                        "name": "Иван",
                        "contact": "notify@example.com",
                        "product": "agents",
                        "segment": "b2c",
                    },
                }
            ],
            "rubric": [{"id": "no_checkout_push", "description": "Без навязанной оплаты", "required": True}],
            "notes": "Блок A12.",
        },
    },
    # --- G8 (+2) B2B ---
    {
        "id": "syn-G8-01",
        "input": [{"role": "user", "content": "Нужно обучить команду разработки, 15 человек. AI-агенты для внутренних процессов. Какие форматы и как заказать?"}],
        "expected_output": "Определить B2B; RAG b2b: корпоративное обучение 5–500 чел, форматы (очный, онлайн-когорта, гибрид); save_lead segment=b2b; НЕ create_payment_link B2C.",
        "metadata": {
            **SYNTH,
            "segment": "b2b",
            "taxonomy": {"group": "G8", "subcategory": "corporate_team_training"},
            "dataset_type": "T5",
            "abilities": ["S1", "S8"],
            "ground_truth_mode": "kb_rag",
            "product_ids": [],
            "expected_tools": [
                {"name": "search_knowledge_base", "args": {"audience": "b2b"}},
                {"name": "save_lead", "args": {"segment": "b2b"}},
            ],
            "rubric": [
                {"id": "segment_b2b", "description": "B2B routing", "required": True},
                {"id": "no_b2c_checkout", "description": "Без B2C оплаты", "required": True},
            ],
            "notes": "Блок D1. KB: corporate-training.md.",
        },
    },
    {
        "id": "syn-G8-02",
        "input": [{"role": "user", "content": "Интересуют ваши курсы по AI. Это для себя лично или можно для нашей компании на 50 человек?"}],
        "expected_output": "Disambiguation: уточнить B2B vs B2C; если компания 50 чел → b2b enterprise; если лично → list_b2c_products; не смешивать checkout.",
        "metadata": {
            **SYNTH,
            "segment": "b2c",
            "taxonomy": {"group": "G8", "subcategory": "b2b_b2c_disambiguation"},
            "dataset_type": "T5",
            "abilities": ["S1"],
            "ground_truth_mode": "rubric",
            "product_ids": [],
            "expected_tools": [{"name": "list_b2c_products", "args": {}}],
            "rubric": [
                {"id": "asks_clarification", "description": "Уточняет лично vs компания", "required": True},
                {"id": "routes_correctly", "description": "B2B путь для 50 чел", "required": True},
            ],
            "notes": "Блок D2. Ambiguous segment — user asks both; agent clarifies.",
        },
    },
]


def load_pilot_records() -> list[dict]:
    records: list[dict] = []
    for line in PILOT_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def validate_records(records: list[dict]) -> list[str]:
    sys.path.insert(0, str(ROOT / "datasets" / "schemas"))
    from dataset_record import DatasetRecord  # noqa: PLC0415

    errors: list[str] = []
    for record in records:
        try:
            DatasetRecord.model_validate(record)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{record.get('id', '?')}: {exc}")
    return errors


def main() -> int:
    pilot = load_pilot_records()
    pilot_ids = {r["id"] for r in pilot}
    additional = [r for r in ADDITIONAL_RECORDS if r["id"] not in pilot_ids]

    all_records = pilot + additional
    all_records.sort(key=lambda r: r["id"])

    errors = validate_records(all_records)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    b2c = [r for r in all_records if r["metadata"]["segment"] == "b2c"]
    b2b = [r for r in all_records if r["metadata"]["segment"] == "b2b"]

    write_jsonl(OUT_DIR / "b2c.jsonl", b2c)
    write_jsonl(OUT_DIR / "b2b.jsonl", b2b)
    write_jsonl(OUT_DIR / "all.jsonl", all_records)

    groups = Counter(r["metadata"]["taxonomy"]["group"] for r in all_records)
    types = Counter(r["metadata"]["dataset_type"] for r in all_records)

    print(f"pilot: {len(pilot)} records")
    print(f"additional: {len(additional)} records")
    print(f"b2c: {len(b2c)} → {OUT_DIR / 'b2c.jsonl'}")
    print(f"b2b: {len(b2b)} → {OUT_DIR / 'b2b.jsonl'}")
    print(f"all: {len(all_records)} → {OUT_DIR / 'all.jsonl'}")
    print("taxonomy:", dict(sorted(groups.items())))
    print("types:", dict(sorted(types.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
