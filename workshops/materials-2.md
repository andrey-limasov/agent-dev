# Материалы к циклу 2: Инструменты агентов (Tool Use)

> ⏰ **До воркшопа 2 у вас один день.** Поэтому список разделён на три части. **Обязательное** — около часа, без него на воркшопе будет трудно. Остальное — по желанию до воркшопа или после, до практики 2.

---

## 🔴 Обязательно до воркшопа (≈ 60 минут)

Делайте по порядку. Если время кончается — пункт 1 важнее всех остальных вместе взятых.

### 1. Спецификация двух инструментов — ваш входной билет (30 мин)

Это пункт 5 домашнего задания практики 1. Если уже сделали — перечитайте и переходите к пункту 2.

В `docs/tools-spec-cycle2.md` вашего репозитория по форме воркшопа 1 (имя, назначение для LLM, параметры с допустимыми значениями, формат возврата, краевые случаи) опишите:

- **поиск по кодовой базе** — что принимает и что возвращает, чтобы результат поместился в контекст модели;
- **чтение файла** — как ограничить его так, чтобы агент не мог прочитать `.env` или что-либо за пределами репозитория.

И допишите в конце один абзац: **какой инструмент в вашем проекте опаснее всего давать агенту и почему** (пункт 6 домашки).

Закоммитьте и пришлите ссылку на файл в чат курса до начала пары. На воркшопе другая команда будет атаковать именно эту спецификацию — чем конкретнее вы опишете ограничения, тем меньше атак пройдёт.

### 2. Anthropic: Writing effective tools for AI agents (15 мин)

[Writing effective tools for AI agents — using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic Engineering, сентябрь 2025, англ.)

Читайте **только раздел «Principles for writing effective tools»** — остальное про автоматические оценки, это позже. Четыре подраздела, на каждый — один вопрос к себе:

- *Choosing the right tools for agents* — почему лучше несколько узких инструментов, чем один универсальный?
- *Returning meaningful context* — что из ответа вашего инструмента модели на самом деле нужно?
- *Optimizing tool responses for token efficiency* — что ваш поиск вернёт, если совпадений 5 000?
- *Prompt-engineering your tool descriptions* — объяснит ли ваше описание новому человеку в команде, когда вызывать инструмент?

Если английский даётся тяжело — прогоните раздел через переводчик, статья того стоит.

### 3. OWASP: Excessive Agency (10 мин)

[LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) (OWASP Top 10 for LLM Applications, англ.)

Прочитайте **Description** и **Prevention and Mitigation Strategies**. Главное — три причины уязвимости: избыточная *функциональность*, избыточные *права*, избыточная *автономность*. Проверьте свою спецификацию: какая из трёх про вас?

### 4. Function calling за 3 минуты (5 мин)

[Function Calling with LLMs](https://www.promptingguide.ai/applications/function_calling) (Prompting Guide, англ.) — если читали по домашке практики 1, пропустите.

Держите в голове один вопрос: **модель сама выполняет функцию или только просит её выполнить?** С этого начнётся воркшоп.

---

## 🟡 По желанию до воркшопа (если осталось время)

- [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) — Simon Willison, 6 минут, англ. Почему агент, у которого одновременно есть доступ к приватным данным, чтение недоверенного текста и канал наружу, почти гарантированно сольёт данные. Будет на этапе 5 воркшопа.
- Посмотрите на свой `docs/lint-report.json` (пункт 4 домашки практики 1; если не сделали — `ruff check --output-format=json > docs/lint-report.json`, 5 минут). Какие поля есть у одного замечания? Что из этого нужно агенту, а что — шум?

---

## 🟢 После воркшопа, до практики 2 (СРС)

Это понадобится, когда вы будете писать код трёх инструментов.

**Python**

- [`pathlib`: `Path.resolve()` и `Path.is_relative_to()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve) — нормализация пути и проверка «внутри ли корня». 10 минут.
- [`subprocess.run`](https://docs.python.org/3/library/subprocess.html#subprocess.run) — параметры `capture_output`, `text`, `timeout`, `check`, и почему **не** `shell=True` ([раздел Security Considerations](https://docs.python.org/3/library/subprocess.html#security-considerations)). 15 минут.

**Ruff**

- [The Ruff Linter](https://docs.astral.sh/ruff/linter/) — разделы *Fixes* и *Exit codes*: что означают коды 0, 1 и 2. 10 минут.

**CrewAI**

- [Create Custom Tools](https://docs.crewai.com/en/learn/create-custom-tools) — повторение: декоратор `@tool` и класс `BaseTool`. Для инструментов с несколькими параметрами и значениями по умолчанию посмотрите вариант с `BaseTool` и `args_schema`. 10 минут.

**Для любопытных (не обязательно)**

- Весь текст статьи Anthropic из пункта 2 — про то, как оценивать инструменты автоматически. Пригодится в цикле 6.
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) целиком — особенно *LLM01 Prompt Injection*. Вернёмся к нему в цикле 7.
