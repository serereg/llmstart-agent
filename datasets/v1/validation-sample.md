# Validation Sample — v1 (10%)

> 6 записей для ручной проверки: естественность, корректность эталона, KB-факты.  
> **Статус:** ✅ апрув 2026-06-28

## `ext-0014-01`

- **Branch:** extraction | **Segment:** b2c
- **Group:** G1 / format_schedule
- **Type:** T1 | **GT mode:** expert_dialog
- **Tools:** search_knowledge_base
- **User:** Добрый день. Заинтересовал комбо курс. Скажите, какой формат у курсов? Можно будет проходить в свое удобное время? Ил...
- **Expected:** Объяснить формат комбо: онлайн-потоки с возможностью проходить по записям в своём темпе; перечислить состав программы (Fullstack → Agents → Deep Agents + бонус интенсив Cursor); указать расписание liv…

### Checklist

- [ ] Формулировка user звучит естественно
- [ ] Expected_output / rubric корректны
- [ ] Факты согласованы с KB (для kb_rag / synthesis)
- [ ] expected_tools соответствуют сценарию

## `ext-0020-02`

- **Branch:** extraction | **Segment:** b2c
- **Group:** G3 / time_conflict_async_rejection
- **Type:** T3 | **GT mode:** rubric
- **Tools:** save_lead
- **User:** Привет. У меня вопрос про интенсив. По каким дням и во сколько семинары?
- **Expected:** Не настаивать на записи после явного отказа; признать барьер (рабочая пятница, нужен синхрон); предложить следующий поток в более удобное время (выходные/вечер); предложить подписаться на анонс; не да…

### Checklist

- [ ] Формулировка user звучит естественно
- [ ] Expected_output / rubric корректны
- [ ] Факты согласованы с KB (для kb_rag / synthesis)
- [ ] expected_tools соответствуют сценарию

## `ext-0127-01`

- **Branch:** extraction | **Segment:** b2b
- **Group:** G8 / coordinator_internal_delay
- **Type:** T5 | **GT mode:** rubric
- **Tools:** search_knowledge_base
- **User:** Добрый день! Отдала внутреннему заказчику, но он был в отпуске до конца прошлой неделе, поэтому пока сама не могу к в...
- **Expected:** Поблагодарить; принять организационный блокер без давления; не повторять полное КП; подтвердить готовность ответить на вопросы; определить сегмент B2B.

### Checklist

- [ ] Формулировка user звучит естественно
- [ ] Expected_output / rubric корректны
- [ ] Факты согласованы с KB (для kb_rag / synthesis)
- [ ] expected_tools соответствуют сценарию

## `syn-pilot-A2`

- **Branch:** synthesis | **Segment:** b2c
- **Group:** G7 / payment_confirmation
- **Type:** T6 | **GT mode:** tool_call
- **Tools:** confirm_payment
- **User:** Хочу купить курс Agents
- **Expected:** При наличии pending payment в сессии вызвать confirm_payment(); поблагодарить; сообщить что оплата подтверждена; предложить следующий шаг (save_lead для контакта или доступ к материалам).

### Checklist

- [ ] Формулировка user звучит естественно
- [ ] Expected_output / rubric корректны
- [ ] Факты согласованы с KB (для kb_rag / synthesis)
- [ ] expected_tools соответствуют сценарию

## `syn-G5-01`

- **Branch:** synthesis | **Segment:** b2c
- **Group:** G5 / misfit_no_python
- **Type:** T2 | **GT mode:** kb_rag
- **Tools:** list_b2c_products
- **User:** Хочу на Agents, но Python не знаю вообще. Всё равно записаться?
- **Expected:** Честный misfit: agents требует базовый Python; рекомендовать llm-fundamentals (beginner); не продавать agents любой ценой.

### Checklist

- [ ] Формулировка user звучит естественно
- [ ] Expected_output / rubric корректны
- [ ] Факты согласованы с KB (для kb_rag / synthesis)
- [ ] expected_tools соответствуют сценарию

## `syn-G8-01`

- **Branch:** synthesis | **Segment:** b2b
- **Group:** G8 / corporate_team_training
- **Type:** T5 | **GT mode:** kb_rag
- **Tools:** search_knowledge_base, save_lead
- **User:** Нужно обучить команду разработки, 15 человек. AI-агенты для внутренних процессов. Какие форматы и как заказать?
- **Expected:** Определить B2B; RAG b2b: корпоративное обучение 5–500 чел, форматы (очный, онлайн-когорта, гибрид); save_lead segment=b2b; НЕ create_payment_link B2C.

### Checklist

- [ ] Формулировка user звучит естественно
- [ ] Expected_output / rubric корректны
- [ ] Факты согласованы с KB (для kb_rag / synthesis)
- [ ] expected_tools соответствуют сценарию
