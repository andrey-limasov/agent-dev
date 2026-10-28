# Практика 4. Первая Crew: Исследователь и Кодер, цикл «генерация → линтер → исправление»

**Длительность:** 180 минут (2 пары)
**Формат:** самостоятельная командная работа по этому руководству. Pair Programming со сменой ролей Driver / Navigator, в блоке 2 — две пары параллельно, тесты до кода, в конце — peer review с соседней командой и ADR.
**Роль преподавателя:** организационная. Он следит за временем, объявляет стоп-точки, фиксирует прогресс команд и назначает пары для peer review. Всё содержание занятия — в этом файле и по ссылкам из него.

> Руководство рассчитано на то, что вы дойдёте до конца сами. Если шаг не получается — сначала читайте блок «Если не получилось» у этого шага, потом таблицу Troubleshooting в конце файла, потом документацию по ссылке.

**Проверено на:** Windows 11, Git Bash и PowerShell 5.1; каркасы [`templates/crewai_example.py`](../templates/crewai_example.py), [`templates/generated_files.py`](../templates/generated_files.py), [`templates/generated-conftest.py`](../templates/generated-conftest.py) и обязательные тесты — Python 3.13 (синтаксис — и 3.11), `crewai==1.15.22`, `pytest==9.1.1`, `ruff==0.17.0`; запуск теста из `generated/` — `fastapi 0.162.0`, `psycopg 3.3.6`, `starlette 1.8.0` на бэкенде недели 8 «Конфигурирования» (`settings.py` на `pydantic-settings`, `.python-version` 3.14), на варианте с python-dotenv (ветка `develop`), на варианте `pydantic-settings` с `extra="forbid"` и полями для ключей `.env` бэкенда и на учебном `templates/sample-backend/` — октябрь 2026. Шаги с моделью (1.4, 3.2–3.4) прошли двумя прогонами занятия целиком — на бэкенде «Конфигурирования» и на «Заметках», шаг 3.2 с итоговым каркасом — ещё тремя запусками на каждом; `qwen3:4b-instruct` на сервере с GPU: 7 вызовов LLM за запуск на «Конфигурировании» (0,8–1,2 минуты), 10–11 на «Заметках» (1,0–1,6 минуты). Время на CPU в этом файле — оценка по этому числу вызовов (1–2 минуты на вызов), не замер. macOS и Linux не проверялись.

---

## Что вы сделаете сегодня

**Проблема.** Разработчик пишет в чат: «Нужен тест: `GET /version` отвечает 200, в ответе версия и команда». Агент практики 3 нашёл бы обработчик и ответил словами, но тест он не напишет: за `max_iter=5` один агент не успевает найти эндпоинт, написать файл, проверить его линтером и исправить. На воркшопе 4 вы разделили эту работу между агентами и записали архитектуру в `docs/crew-design.md`. Сегодня она становится кодом: Исследователь находит факты в бэкенде, Кодер по ним пишет pytest-тест в каталог `generated/` помощника и сам проверяет его линтером.

В конце занятия в репозитории помощника `<проект>-assistant` будет:

1. Ветка `feature/crew` от `main`, в который влит PR практики 3, с `docs/crew-design.md` и Pull Request в `main` с комментариями соседней команды.
2. `ai/tools/generated_files.py` — Tool `write_generated`: первый инструмент курса, который пишет на диск, только в `generated/test_<имя>.py`, с той же проверкой пути, что у инструментов практики 2. `run_linter` проверяет `generated/` вторым корнем.
3. `tests/test_generated_tools.py` — обязательные тесты курса к записи и второму корню. В истории PR коммит с тестами идёт **раньше** кода.
4. `pytest.ini` (`testpaths = tests`), `requirements-generated.txt` и `generated/conftest.py`: человек запускает сгенерированный тест командой `python -m pytest generated -q` из окружения помощника, бэкенд не меняется.
5. `ai/run_crew.py` — Crew из двух агентов по вашей архитектуре; трасса `ai/traces/run-p4-01.log` и тест `generated/test_<кратко>.py`, который написал Кодер.
6. В описании PR — таблица «дошли ли поля итога Исследователя до Кодера» и вывод запуска сгенерированного теста.
7. `docs/adr/004-orchestration-pattern.md` — ADR 004 «Принято» с замером: сколько вызовов LLM и минут занял запуск.

**Помощник по-прежнему только читает бэкенд.** Пишет он только в `generated/` своего репозитория. Код бэкенда и сгенерированный тест помощник не запускает: тест запускает человек.

---

## Таймлайн

| Время | Блок | Что должно быть готово к концу блока |
|---|---|---|
| 00:00–00:05 | Блок 0. Какой агент сломается первым | Преподаватель зачитал 2–3 ответа со стикеров воркшопа 4 |
| 00:05–00:30 | Блок 1. Ветка, бэкенд, индекс, модель | Роли названы; в `feature/crew` код практик 1–3 и `docs/crew-design.md`; бэкенд обновлён, его состояние записано; индекс построен; загрузка модели запущена во втором окне (проверка — на сведении) |
| 00:30–01:10 | Блок 2. Две пары одновременно | Пара 1: тесты, коммит `test:`, Tool записи и второй корень `run_linter`, тесты зелёные. Пара 2: `pytest.ini`, зависимости бэкенда, `generated/conftest.py`, образец-тест проходит |
| 01:10–01:20 | Сведение кода двух пар | Всё в `feature/crew`; полный набор тестов зелёный на машине, где запускается Crew |
| 01:20–02:15 | Блок 3. Crew | `ai/run_crew.py`, трасса `run-p4-01.log`, тест в `generated/`, таблица передачи контекста, вывод запуска теста |
| 02:15–02:55 | Блок 4. PR, peer review, ADR | PR открыт, review в обе стороны, ADR 004 «Принято» |
| 02:55–03:00 | Итог | Ответ по чек-листу самопроверки |

Перерыв — во время запуска Crew в шаге 3.2 (около 01:40): машина считает, команда отдыхает. Одна машина или одна пара — перерыв после шага 2.5 (маршрут в начале блока 2).

Тесты этого занятия не импортируют CrewAI и не обращаются к Ollama: обязательные тесты к записи — около 5 секунд, весь набор помощника — 20–60 секунд. Медленные места: построение индекса (около 2,5 минуты на бэкенде «Конфигурирования», 1 мин 40 с на «Заметках»), импорт CrewAI (до двух минут) и запуск Crew. Запуск Crew из двух агентов — 7–12 вызовов LLM, на CPU по 1–2 минуты: **10–25 минут**; первый вызов после загрузки модели — до 10 минут, поэтому модель загружается заранее, в шаге 1.4. На одной машине — одна долгая команда за раз.

---

## Подготовка ДО занятия

Около 50 минут дома, из них 30 — чтение. Пункт 1 делает один участник на команду, пункт 2 — хотя бы один, пункт 3 — каждый.

### 1. Хвосты прошлых занятий (один участник)

- PR практики 3 (`feature/rag-search` → `main` помощника) влит (домашнее задание воркшопа 4, п. 1). Не влит — на паре вы вольёте его первым делом (шаг 1.2).
- `docs/crew-design.md` — в ветке `feature/crew` (домашнее задание воркшопа 4, п. 2) или хотя бы в рабочей папке у одного участника; черновик `docs/adr/004-orchestration-pattern.md` со статусом «Предложено» — там же (п. 3).
- Обновите клон курса: `git -C <клон курса> pull` (скачивали архив — скачайте заново). В `templates/` появились каркасы `crewai_example.py`, `generated_files.py` и `generated-conftest.py`.

**Как понять, что получилось.** `ls <клон курса>/templates/generated_files.py` (PowerShell: `Test-Path <клон курса>\templates\generated_files.py`) находит файл. `git log --oneline -3 origin/feature/crew` показывает коммит `docs: add Crew design` — или ветки ещё нет (команда печатает `fatal: ambiguous argument 'origin/feature/crew'`, это не сбой), но файл архитектуры лежит у вас в `docs/`.

**Если не получилось.** `pull` не проходит — архив репозитория курса (Code → Download ZIP на [странице репозитория](https://github.com/andrey-limasov/agent-dev)). Архитектуры нет ни у кого (пропустили воркшоп 4) — на паре в шаге 1.2 вы возьмёте каркас из [`materials-4.md`](materials-4.md) и заполните четыре раздела за 10 минут; дома прочитайте в этом файле справку «Паттерны в CrewAI» (10 минут).

### 2. Модели в Ollama (хотя бы один участник, 5 мин)

Crew запускается на одной машине команды — той, где есть Ollama, модель для агентов и модель эмбеддингов из практики 3. Обе модели у вас уже должны быть:

```bash
ollama ls
```

PowerShell — та же команда.

**Как понять, что получилось.** В списке есть `qwen3:4b-instruct` (без `:latest`: у модели свой тег) (или `qwen2.5:7b`, если в архитектуре она) и `embeddinggemma:latest` (или `qwen3-embedding:0.6b` по ADR 003 помощника).

**Если не получилось.** Модели нет — `ollama pull qwen3:4b-instruct` (2,5 ГБ) и `ollama pull embeddinggemma` (622 МБ) дома: по сети аудитории это долго. `qwen2.5-coder` не подходит: он не поддерживает Tools (`does not support tools`). Ollama нет ни у кого — поставьте её одному участнику по [«Подготовке» практики 1, путь А](practice-1.md#3-путь-а-локальная-модель-10-мин--загрузка-25-гб), п. 1; без модели эмбеддингов не работает `search_docs` у Исследователя.

### 3. Зависимости бэкенда в окружении помощника (каждый, 3 мин)

Сгенерированный тест импортирует приложение бэкенда, поэтому в окружении помощника нужны пакеты, которые импортирует бэкенд. Скачайте их дома; на паре в шаге 2.4 они закрепятся в файле. В корне помощника, с активированным окружением:

```bash
pip install fastapi "psycopg[binary]"
pip check
```

На учебном бэкенде «Заметки» `psycopg` не нужен: `pip install fastapi`. Окружение `uv venv` без `--seed` — `uv pip install …` и `uv pip check`. Версии не закрепляйте: это зависимости бэкенда, а не помощника, и в `requirements.txt` помощника они не попадают.

**Как понять, что получилось.** `pip check` печатает `No broken requirements found.` (`uv pip check` — `All installed packages are compatible`); `python -c "import fastapi; print(fastapi.__version__)"` печатает номер версии.

**Если не получилось.** `pip check` сообщает о несовместимости `starlette` — запишите строку целиком и покажите её в шаге 2.4: в проверочном прогоне `fastapi 0.162.0` встал со `starlette 1.8.0`, которая уже стоит в окружении помощника вместе с CrewAI, без конфликтов.

### 4. Прочитать (≈ 30 мин)

| Что читать | К какому шагу | Время |
|---|---|---|
| Свой `docs/crew-design.md`, разделы 1, 5, 6, 8 — то, что сегодня становится кодом | 1.3, 3.1 | 5 мин |
| Шаги блока 2 этого файла: 2.1–2.3, если вы в паре 1, 2.4–2.6 — в паре 2 (пары можно договорить в чате команды заранее; не договорились — прочитайте 2.1 и 2.4): пояснения к тестам и правкам, чтобы на паре только выполнять | 2.1–2.6 | 5 мин |
| [`templates/crewai_example.py`](../templates/crewai_example.py) и [`templates/generated_files.py`](../templates/generated_files.py) — docstring модуля и константы промптов | 2.2, 3.1 | 5 мин |
| [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/) — разделы *Using TestClient* и *Separating tests*: так выглядит тест, который напишет Кодер | 2.5, 3.4 | 5 мин |
| [pytest: Invoking pytest versus python -m pytest](https://docs.pytest.org/en/stable/explanation/pythonpath.html) — почему в курсе `python -m pytest`, а не `pytest` | 2.5 | 3 мин |
| [pytest: conftest.py — local per-directory plugins](https://docs.pytest.org/en/stable/how-to/writing_plugins.html#conftest-py-local-per-directory-plugins) — что такое `conftest.py` каталога | 2.5 | 3 мин |
| [CrewAI: Crews](https://docs.crewai.com/en/concepts/crews) — раздел *Crew Usage Metrics*: откуда каркас берёт число вызовов LLM для ADR 004 | 3.2 | 4 мин |

СРС к циклу 4 (задачи и `context`, guardrail, `max_iter` и `max_execution_time`) — раздел «После воркшопа, до практики 4» в [`materials-4.md`](materials-4.md), если ещё не прочитан.

---

## Блок 0. Какой агент сломается первым (00:00–00:05)

Преподаватель зачитывает 2–3 самых частых ответа со стикеров воркшопа 4 «Какой агент нашей Crew сломается первым и почему?». Driver в это время открывает терминал в корне помощника и активирует окружение. В шаге 3.3 вы проверите по трассе, сломался ли тот агент, которого вы назвали.

> **Стоп-точка (00:05)** — преподаватель: зачитайте 2–3 самых частых ответа со стикеров воркшопа 4 и объявите начало блока 1.

---

## Блок 1. Ветка, бэкенд, индекс, модель (00:05–00:30)

### Шаг 1.1: Роли и две пары (2 мин)

**Driver** — клавиатура, проговаривает вслух, что делает. **Navigator** — держит открытыми `docs/crew-design.md` и этот файл, сверяет код с архитектурой.

В блоке 2 команда работает **двумя парами** параллельно, каждая на своей машине:

- **Пара 1** — Tool записи `write_generated` и второй корень `run_linter` (шаги 2.1–2.3). Ей не нужны ни Ollama, ни бэкенд.
- **Пара 2** — запуск теста из `generated/` pytest'ом (шаги 2.4–2.6). Ей нужен клон бэкенда рядом с помощником.

Команда из трёх человек: третий участник ведёт пару 2 один, Navigator у него — по очереди кто-то из пары 1, когда та ждёт тесты. Одна машина или одна пара — маршрут в начале блока 2. В блоке 3 Crew запускается на **машине Crew** — той, где есть Ollama и обе модели (подготовка, п. 2). Роли меняются на стоп-точках 00:50 и 01:20. Запишите, кто в каком блоке в какой роли: это пойдёт в описание PR.

**Как понять, что получилось.** Каждый называет свою роль и пару; названа машина Crew.

### Шаг 1.2: PR практики 3 — в `main`, ветка `feature/crew` (10 мин)

**Зачем это нужно.** Исследователю нужен `search_docs` из `ai/tools/rag_pipeline.py` практики 3, Кодеру — `run_linter` практики 2. Если PR практики 3 не влит, ветка от `main` этих файлов не получит.

**Что сделать**

1. Если PR практики 3 ещё не влит — влейте его в `main` в веб-интерфейсе хостинга (кнопка Merge на странице PR). Если `main` защищена — одобряет любой участник команды, который не автор PR.
2. Тот, у кого файл архитектуры (в ветке или в рабочей папке), в корне помощника:

```bash
git switch main
git pull
git ls-files ai/tools/rag_pipeline.py
git fetch
git branch -a --list "*crew*"
```

3. Дальше — по выводу последней команды:
   - **Ветка есть** (строка `remotes/origin/feature/crew` или `feature/crew`) — переключитесь на неё **без** `-c` и подтяните в неё свежий `main`:

     ```bash
     git switch feature/crew
     git pull
     git merge --no-edit main
     ```

   - **Ветки нет** (вывод пустой) — создайте её от `main`:

     ```bash
     git switch -c feature/crew
     ```

4. Если `git ls-files docs/crew-design.md docs/adr/004-orchestration-pattern.md` печатает не обе строки, а файлы лежат у вас в рабочей папке, закоммитьте их. Выполняйте пару `git add` + `git commit` только для того файла, которого нет в выводе `git ls-files`; ответ `nothing to commit, working tree clean` значит, что файл уже в ветке, — это не ошибка. ADR 004 нет совсем — сначала создайте его по [каркасу ADR 004](materials-4.md#каркас-adr-004) со статусом «Предложено» и заполните только «Контекст»: остальное — в шаге 4.3.

```bash
git add docs/crew-design.md
git commit -m "docs: add Crew design"
git add docs/adr/004-orchestration-pattern.md
git commit -m "docs: add ADR 004 draft on orchestration pattern"
```

5. Проверьте и опубликуйте:

```bash
git ls-files ai/tools/rag_pipeline.py docs/crew-design.md
git push -u origin feature/crew
```

6. Остальные участники — после этого `push`: `git fetch`, `git switch feature/crew`, `git pull`. `.env` и `.chroma/` при смене ветки не пропадают: они не отслеживаются git.

**Как понять, что получилось.** Первый `git ls-files` печатает `ai/tools/rag_pipeline.py` (код практики 3 в `main`). `git merge` печатает `Already up to date.`, `Fast-forward` или `Merge made by the 'ort' strategy.` Последний `git ls-files` печатает обе строки: `ai/tools/rag_pipeline.py` и `docs/crew-design.md`.

**Если не получилось**

- Первый `git ls-files` ничего не напечатал — PR практики 3 не влит. Влейте его (пункт 1) и повторите с `git switch main`. **Влить сейчас нельзя** (нет второго одобряющего, нет прав): создайте или возьмите ветку по пункту 3, затем подтяните ветку практики 3 напрямую — `git merge --no-edit origin/feature/rag-search` — и продолжайте с пункта 4. В первой строке описания PR практики 4 напишите, что в нём и код практики 3.
- `git switch feature/crew` ответил `error: The following untracked working tree files would be overwritten by checkout: docs/crew-design.md` — в ветке уже есть закоммиченная архитектура, а у вас своя копия. Отложите её: `mv docs/crew-design.md ../crew-design-mine.md` (PowerShell: `Move-Item docs/crew-design.md ../crew-design-mine.md`), повторите `git switch` и перенесите свои правки вручную.
- `git add` ответил `fatal: pathspec 'docs/adr/004-orchestration-pattern.md' did not match any files` — ADR 004 нет у вас на диске: создайте его по каркасу (пункт 4) или возьмите у участника, у которого он есть.
- `git add` ответил `fatal: pathspec 'docs/crew-design.md' did not match any files` — файл у другого участника. Он выполняет пункты 2–5 у себя; вы — пункт 6.
- **Архитектуры нет ни у кого** (воркшоп 4 пропущен). Скопируйте [каркас `docs/crew-design.md`](materials-4.md#каркас-docscrew-designmd) в `docs/crew-design.md`. Navigator заполняет разделы 1, 2, 5 и 6 за 10 минут, пока Driver делает шаги 1.3–1.4: раздел 1 — по шагу 1.3, раздел 2 — Исследователь и Кодер (образцы — константы `RESEARCHER_*` и `CODER_*` в каркасе `crewai_example.py`), раздел 5 — поля итога Исследователя, раздел 6 — «Кодер через Tool `write_generated`, одно исправление при `max_iter=5`». Закоммитьте по пункту 4; остальные разделы — дома в тот же PR.
- `CONFLICT` при `git merge` — откройте файл, оставьте строки обеих версий, удалите маркеры `<<<<<<<`, `=======`, `>>>>>>>`, затем `git add <файл>` и `git commit --no-edit`.

### Шаг 1.3: Бэкенд — обновить и определить его состояние (6 мин)

**Зачем это нужно.** На неделе 8 «Конфигурирования» в бэкенде появляется `settings.py`: приложение проверяет настройки при импорте и без `DATABASE_URL` не импортируется. Пришёл ли этот код в ваш клон, зависит от того, прошла ли уже практика 4 «Конфигурирования» и на какой ветке клон. От этого зависит, какое поведение выбрать для теста: тест будут запускать без базы данных.

**Что сделать.** На машине пары 2 и на машине Crew, из корня помощника (одинаково в Git Bash и PowerShell; `<проект>` — каталог из `AI_REPO_ROOT` в `.env`):

```bash
git -C ../<проект> pull
git -C ../<проект> branch --show-current
git -C ../<проект> log --oneline -1
git -C ../<проект> ls-files settings.py app/settings.py
git -C ../<проект> grep -n -E "pydantic_settings|load_dotenv|environs|os\.environ" -- "*.py"
```

Учебный бэкенд «Заметки» — не git-репозиторий: все пять команд выше не нужны (они ответят `fatal: not a git repository`), его код не менялся с практики 3. Проверка — `ls ../sample-backend` (PowerShell: `Get-ChildItem ..\sample-backend`): `main.py`, `README.md`, `CONTRIBUTING.md`, `docs`.

Ожидаемо на бэкенде недели 8 (на своём — свои ветка, хеш и строки):

```
main
b6f6ce8 Merge pull request #14 from ivan-petrov/feature/configuration
settings.py
settings.py:9:from pydantic_settings import BaseSettings, SettingsConfigDict
```

Найдите свою строку и сверьте с разделом 1 `docs/crew-design.md`:

| Что напечатали `ls-files` и `grep` | Состояние | Какое поведение брать для теста |
|---|---|---|
| `settings.py` (или `app/settings.py`) и `pydantic_settings` | Неделя 8, путь по умолчанию | Без базы: `GET /version` → 200 и поля ответа; `GET /health` → 503 и `{"status": "unhealthy", "database": "unavailable"}`, если так написано в коде обработчика. Не брать `/health` → 200 и запросы, которые пишут в базу |
| `settings.py` и `load_dotenv` / `environs` / `os.environ` | Неделя 8, вариант ADR 003 бэкенда с python-dotenv или environs | То же |
| `settings.py` нет, в `grep` — `main.py: … os.environ.get("DATABASE_URL")` | Код недели 6–7: практика 4 «Конфигурирования» ещё не влита в эту ветку | `GET /version` или другое поведение без базы. Не опирайтесь на ответ `/health` «`DATABASE_URL is not set`»: на неделе 8 этой ветки в коде не будет. При GitFlow `settings.py` лежит в `develop`: если в клоне нет вашей незаконченной работы по «Конфигурированию» — `git -C ../<проект> switch develop` и повторите команды; после занятия верните ветку: `git -C ../<проект> switch -` |
| Учебный бэкенд «Заметки» | Без настроек и без базы | `POST /notes` с `title` → 201 и в ответе поле `id` (`main.py`, строки 28–33); `DELETE /notes/{note_id}` → 404 разобран на воркшопе всей группой |

На машине Crew запишите в раздел 1 `docs/crew-design.md` строку `Бэкенд: ветка <ветка>, коммит <хеш>` (на «Заметках» — `Бэкенд: учебный «Заметки» (templates/sample-backend), не git-репозиторий, код не менялся с практики 3`). Если поведение в разделе 1 требует работающей базы — поменяйте его сейчас на поведение из таблицы. Сразу закоммитьте и отправьте: незакоммиченная правка остановит потом `git pull`.

```bash
git add docs/crew-design.md
git commit -m "docs: record backend state for Crew"
git push
```

**Как понять, что получилось.** В разделе 1 архитектуры — ветка и коммит бэкенда (на «Заметках» — строка про учебный бэкенд), поведение для теста не требует базы. `git -C ../<проект> status --short` пуст (на «Заметках» — `ls ../sample-backend` печатает те же четыре имени). `git status --short` помощника не показывает `docs/crew-design.md`.

**Если не получилось**

- `rejected` при `git push` — другой участник уже отправил коммиты: `git pull --rebase`, затем `git push`.

- `fatal: cannot change to '../<проект>'` — подставьте имя каталога бэкенда из `AI_REPO_ROOT` в `.env` помощника.
- `git pull` ответил `error: Your local changes to the following files would be overwritten by merge` — в клоне бэкенда незакоммиченная работа по «Конфигурированию». Помощник её не трогает: пропустите `pull`, работайте с тем, что есть, и запишите это в раздел 1. То же при `switch develop` — ответ `error: Your local changes to the following files would be overwritten by checkout`: ветку не меняйте, берите поведение из строки «`settings.py` нет» таблицы.
- `git grep` ничего не напечатал при найденном `settings.py` — настройки читаются другим способом. Это не мешает: запуск теста в шаге 2.5 один для всех вариантов.

### Шаг 1.4: Индекс и загрузка модели — на машине Crew (4 мин)

**Зачем это нужно.** После `git pull` в бэкенде новые документы и docstrings (`settings.py`, ADR 003 бэкенда), а индекс `search_docs` собран по старым — Исследователь искал бы по устаревшему. Модель для агентов загружается в память один раз заранее: первый вызов после загрузки на CPU — до 10 минут, и этим вызовом не должен стать запуск Crew.

**Что сделать.** На машине Crew, из корня помощника. Сначала индекс, затем загрузка модели — по очереди, не одновременно.

1. Индекс (около 2,5 минуты).

   Git Bash:

```bash
export PYTHONUTF8=1
python -m ai.tools.rag_pipeline build
```

   PowerShell:

```powershell
$env:PYTHONUTF8 = "1"
python -m ai.tools.rag_pipeline build
```

2. Когда `build` закончился, откройте **второе окно терминала** в корне помощника и запустите в нём загрузку модели. Ответа не ждите: на CPU он может идти до 10 минут. Окно не закрывайте, а в первом окне переходите к блоку 2. Ответ проверите на сведении кода (01:10–01:20).

   Git Bash:

```bash
curl -s http://localhost:11434/api/generate -d '{"model": "qwen3:4b-instruct", "prompt": "Ответь одним словом: готово", "stream": false, "keep_alive": "3h"}' | head -c 120
```

   PowerShell:

```powershell
(Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/generate -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes('{"model": "qwen3:4b-instruct", "prompt": "Ответь одним словом: готово", "stream": false, "keep_alive": "3h"}'))).response
```

Адрес и модель — из вашего `.env` (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`). `keep_alive` держит модель в памяти три часа вместо пяти минут по умолчанию: блок 2 длится 40 минут.

**Как понять, что получилось.** `build` заканчивается строками `indexed: N files, M chunks (…)` и `skipped by secret check: …`; в списке файлов бэкенда — новые (например, `docs/adr/003-configuration.md` и `settings.py`). Во втором окне висит запрос к модели — это нормально. Когда он закончится, он напечатает начало ответа `{"model":"qwen3:4b-instruct",…,"response":"Готово"…` (PowerShell — `Готово`). Ответ модели проверяется по смыслу: одно слово, не ошибка.

**Если не получилось**

- `build`: `error: Ollama не ответила за 300 с` или `Ollama не отвечает по адресу …` — строки [Troubleshooting практики 3](practice-3.md#troubleshooting) про `build`; поднимите `AI_EMBED_TIMEOUT_S=600` в `.env`.
- Запрос к модели висит больше 10 минут или `Failed to connect` при `localhost` — в `.env` и в команде поставьте `http://127.0.0.1:11434`: на части машин `localhost` сначала пробует адрес IPv6, на котором Ollama не слушает.
- `{"error":"model \"qwen3:4b-instruct\" not found…"}` — модель не скачана на этой машине: «Подготовка», п. 2.

> **Стоп-точка (00:30)** — преподаватель: объявите деление на две пары и начало блока 2. Отметьте команды, у которых `git ls-files ai/tools/rag_pipeline.py docs/crew-design.md` в ветке `feature/crew` печатает меньше двух строк, и команды, у которых `build` не завершился ни на одной машине.

---

## Блок 2. Две пары одновременно (00:30–01:10)

Пара 1 выполняет шаги 2.1–2.3, пара 2 — шаги 2.4–2.6, одновременно, каждая на своей машине. Шаг 2.6 пара 2 делает, если к 01:05 успела 2.4 и 2.5; иначе — во время запуска Crew в шаге 3.2, перед шагом 4.3.

**Каждый коммит — сразу с `git push`, правки не оставляйте незакоммиченными.** Обе пары пушат в одну ветку, поэтому `git push` часто отвечает `rejected` — тогда `git pull --rebase`, затем `git push`. `git pull --rebase` не работает, пока в рабочей папке есть незакоммиченные правки (`error: cannot pull with rebase: You have unstaged changes`): рецепт — в «Если не получилось» шага 2.3.

**Одна машина или одна пара в команде.** Работы блока 2 на одну пару — 70 минут, она не помещается в 40. Порядок такой: 2.1 → 2.2 → 2.3 (до 01:10); сведение не нужно — сразу шаг 3.1; перед запуском 3.2 проверьте модель, как в «Сведении кода»: во втором окне шага 1.4 напечатан ответ, `ollama ps` показывает `qwen3:4b-instruct` (ошибка или модели нет — «Если не получилось» сведения). Затем запуск 3.2 (около 01:25); пока он идёт, в отдельном окне терминала — шаги 2.4 и 2.5 (pytest не обращается к Ollama), затем 2.6. На этом маршруте ожидаемые числа другие: в шаге 2.4 `python -m pytest` — прежнее число плюс 16 (`54 passed` в проверочном прогоне), шаги 2.1–2.3 уже сделаны; в шаге 2.5 `python -m pytest generated -q` — `1 passed`, а если Crew уже записал свой тест — `2 passed` или `1 failed, 1 passed` (шаг 2.5, «Как понять»). Перерыв — после шага 2.5, если запуск ещё идёт; 2.6 не успеваете — дома. Свои тесты — дома.

### Шаг 2.1 (пара 1): Обязательные тесты, красный запуск, коммит (10 мин)

**Зачем это нужно.** `write_generated` — первый инструмент курса, который пишет на диск. Ошибка в его проверке пути — запись в бэкенд или затёртый `.env` помощника. Тесты проверяют границы до того, как инструмент получит модель: путь вне `generated/`, выход через `..`, чужие имена файлов, `conftest.py`, конфигурация ruff помощника, кеш ruff.

**Что сделать**

1. Создайте `tests/test_generated_tools.py` — его не меняют под свою архитектуру. `tests/conftest.py` и `tests/test_invariants.py` практики 2 не трогайте: фикстуры `repo` (тестовый бэкенд) и `s` (настройки с корнем в нём) берутся оттуда.

```python
"""Обязательные тесты курса: запись в generated/ и второй корень run_linter.

Не меняйте их под свою архитектуру. Корень помощника подменён временным каталогом:
без CrewAI, без Ollama и без сети.
"""

import json
from unittest import mock

import pytest

import ai.tools.generated_files as gf
from ai.tools.code_tools import run_linter

GOOD_TEST = 'def test_ok():\n    assert 1 + 1 == 2\n'
BAD_TEST = 'import os\n\n\ndef test_ok():\n    assert 1 + 1 == 2\n'


@pytest.fixture
def assistant(tmp_path_factory):
    """Корень помощника — отдельный временный каталог рядом с тестовым бэкендом."""
    root = tmp_path_factory.mktemp("assistant")
    (root / "generated").mkdir()
    (root / "generated" / "conftest.py").write_text("# conftest курса\n", encoding="utf-8")
    (root / ".env").write_text("CLOUD_API_KEY=secret\n", encoding="utf-8")
    with mock.patch.object(gf, "ASSISTANT_ROOT", root):
        yield root


def test_write_creates_file_in_assistant(s, repo, assistant):
    answer = json.loads(gf.write_generated("generated/test_x.py", GOOD_TEST, s))
    assert answer["status"] == "ok"
    assert answer["path"] == "generated/test_x.py"
    assert (assistant / "generated" / "test_x.py").read_text(encoding="utf-8") == GOOD_TEST
    assert not list(repo.rglob("test_x.py"))


@pytest.mark.parametrize(
    "path",
    ["test_x.py", "ai/test_x.py", "generated/../ai/test_x.py", "../generated/test_x.py", "/tmp/test_x.py"],
)
def test_write_outside_generated_is_error(s, repo, assistant, path):
    answer = json.loads(gf.write_generated(path, GOOD_TEST, s))
    assert answer["status"] == "error"
    assert not list(assistant.rglob("test_x.py"))
    assert not list(repo.rglob("test_x.py"))


@pytest.mark.parametrize(
    "path", ["generated/conftest.py", "generated/x.py", "generated/test_x.txt", "generated/sub/test_x.py"]
)
def test_write_only_test_files(s, assistant, path):
    answer = json.loads(gf.write_generated(path, GOOD_TEST, s))
    assert answer["status"] == "error"
    assert (assistant / "generated" / "conftest.py").read_text(encoding="utf-8") == "# conftest курса\n"


def test_write_empty_content_is_error(s, assistant):
    answer = json.loads(gf.write_generated("generated/test_x.py", "  \n", s))
    assert answer["status"] == "error"
    assert not (assistant / "generated" / "test_x.py").exists()


def test_lint_generated_finds_issue(s, assistant):
    gf.write_generated("generated/test_x.py", BAD_TEST, s)
    answer = json.loads(run_linter("generated/test_x.py", s))
    assert answer["status"] == "ok"
    assert [(f["path"], f["rule"]) for f in answer["findings"]] == [("generated/test_x.py", "F401")]


def test_lint_generated_ignores_assistant_config(s, assistant):
    (assistant / "ruff.toml").write_text('[lint]\nignore = ["F401"]\n', encoding="utf-8")
    gf.write_generated("generated/test_x.py", BAD_TEST, s)
    answer = json.loads(run_linter("generated/test_x.py", s))
    assert [f["rule"] for f in answer["findings"]] == ["F401"]


def test_lint_generated_outside_is_error(s, assistant):
    (assistant / "ai").mkdir()
    (assistant / "ai" / "config.py").write_text("import os\n", encoding="utf-8")
    answer = json.loads(run_linter("generated/../ai/config.py", s))
    assert answer["status"] == "error"
    assert "generated/" in answer["message"]


def test_generated_prefix_means_assistant(s, repo, assistant):
    (repo / "generated").mkdir()
    (repo / "generated" / "test_backend.py").write_text("import os\n", encoding="utf-8")
    answer = json.loads(run_linter("generated/test_backend.py", s))
    assert answer["status"] == "error"
    assert "не найден" in answer["message"]


def test_lint_generated_writes_nothing(s, repo, assistant):
    gf.write_generated("generated/test_x.py", BAD_TEST, s)
    run_linter("generated/test_x.py", s)
    assert not (assistant / ".ruff_cache").exists()
    assert not (repo / ".ruff_cache").exists()
```

   Что здесь важно понимать, чтобы читать падения:
   - `mock.patch.object(gf, "ASSISTANT_ROOT", root)` подменяет корень помощника на временный каталог: тесты не пишут в ваш настоящий `generated/`. Корень бэкенда — фикстура `repo` практики 2.
   - `test_lint_generated_ignores_assistant_config` кладёт в корень помощника `ruff.toml`, который отключает `F401`. Замечание всё равно должно найтись: сгенерированный тест проверяется правилами ruff по умолчанию (`--isolated`), а не настройками помощника.
   - `test_generated_prefix_means_assistant` создаёт каталог `generated/` в бэкенде. Путь `generated/…` всё равно означает каталог помощника: в бэкенде файла не найдено.
   - `test_lint_generated_writes_nothing` проверяет, что ruff не оставил кеш `.ruff_cache` ни в помощнике, ни в бэкенде.

2. Запустите только этот файл из корня помощника — `python -m pytest`, а не `pytest`:

```bash
python -m pytest -q tests/test_generated_tools.py
```

   Сохраните последние строки вывода: они пойдут в описание PR как «красное до кода».

3. Закоммитьте тесты **отдельным коммитом до кода**:

```bash
git add tests/test_generated_tools.py
git commit -m "test: add generated tools tests before implementation"
git push
```

**Как понять, что получилось.** Тесты красные, потому что модуля ещё нет:

```
E   ModuleNotFoundError: No module named 'ai.tools.generated_files'
=========================== short test summary info ===========================
ERROR tests/test_generated_tools.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 2.53s
```

Других ошибок нет. `git log --oneline -1` показывает коммит `test: …`.

**Если не получилось**

- `fixture 's' not found` или `fixture 'repo' not found` — в `tests/conftest.py` практики 2 фикстуры названы иначе. Верните имена курса `repo` и `s` или добавьте в `conftest.py` фикстуры с этими именами, которые возвращают ваши.
- `ModuleNotFoundError: No module named 'ai'` — запущен `pytest`, а не `python -m pytest`, или не из корня помощника.
- `SyntaxError` в тесте — исправьте опечатку сейчас: после появления кода её легко принять за ошибку каркаса.
- `rejected` при `git push` — другая пара уже отправила свои коммиты: `git pull --rebase`, затем `git push`.

### Шаг 2.2 (пара 1): Каркас — в `ai/tools/generated_files.py` (8 мин)

**Зачем это нужно.** Проверка пути, граница `generated/`, запрет на `conftest.py` и тексты ошибок — общие для курса: на них опираются обязательные тесты и следующие занятия. В каркасе они готовы.

**Что сделать**

1. Скопируйте каркас из клона курса и сразу закоммитьте как есть:

```bash
cp <клон курса>/templates/generated_files.py ai/tools/generated_files.py
git add ai/tools/generated_files.py
git commit -m "feat: add write_generated tool skeleton"
```

   PowerShell: `Copy-Item <клон курса>\templates\generated_files.py ai\tools\generated_files.py`, затем те же `git add` и `git commit`.

2. Прочитайте в паре `check_generated_path` и `write_generated`. Navigator сверяет их с разделом 6 `docs/crew-design.md` («Кто записывает файл», «Если Tool…») и записывает в раздел «Решение» черновика ADR 004 строку `Сверка write_generated с разделом 6 crew-design.md: расхождений нет` (есть расхождения — перечислите их после двоеточия):
   - `check_generated_path` вызывает `check_path` практики 2 с корнем помощника: пустой путь, абсолютный путь, выход за корень и deny-list (`.env` помощника) — те же ошибки, что у `read_file`. Затем — граница каталога `generated/`;
   - `write_generated` пишет только `generated/test_<имя>.py` без подкаталогов: `generated/conftest.py` модель не перезапишет. Файл с тем же именем перезаписывается — так Кодер исправляет тест после линтера;
   - в бэкенд инструмент не пишет: префикс `generated/` всегда означает каталог помощника.

   Закоммитьте строку ADR 004 и отправьте оба коммита — каркас и ADR:

```bash
git add docs/adr/004-orchestration-pattern.md
git commit -m "docs: compare write_generated tool and Crew design"
git push
```

3. Запустите тесты:

```bash
python -m pytest -q tests/test_generated_tools.py
```

**Как понять, что получилось.** Тесты записи прошли, четыре теста линтера упали — `run_linter` ещё не знает о втором корне, это работа шага 2.3:

```
FAILED tests/test_generated_tools.py::test_lint_generated_finds_issue - Asser...
FAILED tests/test_generated_tools.py::test_lint_generated_ignores_assistant_config
FAILED tests/test_generated_tools.py::test_lint_generated_outside_is_error - ...
FAILED tests/test_generated_tools.py::test_generated_prefix_means_assistant
4 failed, 12 passed in 4.78s
```

**Если не получилось**

- Нет файла `<клон курса>/templates/generated_files.py` — клон не обновлён: `git -C <клон курса> pull`. Не помогло — откройте [`templates/generated_files.py`](https://github.com/andrey-limasov/agent-dev/blob/main/templates/generated_files.py) на странице репозитория курса и кнопкой Download raw file сохраните как `ai/tools/generated_files.py`.
- `ImportError: cannot import name '_ok'` (или `_fail`, `check_path`) `from 'ai.tools.code_tools'` — в вашем `code_tools.py` функция переименована. Эти имена общие для курса: верните их или допишите псевдоним (`_ok = <ваше имя>`).
- Падают и тесты записи (`test_write_…`) — сравните текст тестов с шагом 2.1: их не меняют.
- `rejected` при `git push` или `cannot pull with rebase: You have unstaged changes` — «Если не получилось» шага 2.3.

### Шаг 2.3 (пара 1): Второй корень в `run_linter` (20 мин)

**Зачем это нужно.** Кодер проверяет записанный тест тем же Tool `run_linter`, что в практике 2. Сейчас `run_linter("generated/test_x.py")` ищет файл в бэкенде и отвечает `файл или каталог не найден`. Нужно: путь с префиксом `generated/` — в репозитории помощника, с той же проверкой пути, с правилами ruff по умолчанию. Имена, поля ответа и тексты `run_linter` и `check_path` не меняются: на них обязательные тесты практики 2.

**Что сделать.** Три правки в `ai/tools/code_tools.py`.

1. В начале тела `run_linter`, сразу после docstring, замените две строки:

```python
    root = Path(s.ai_repo_root).resolve()
    target, err = check_path(path, s)
```

   на:

```python
    from ai.tools.generated_files import (  # практика 4: второй корень generated/
        check_generated_path,
        generated_settings,
        is_generated,
    )

    generated = is_generated(path)  # путь generated/... — корень помощника, а не бэкенда
    if generated:
        s = generated_settings(s)
    root = Path(s.ai_repo_root).resolve()
    target, err = check_generated_path(path, s) if generated else check_path(path, s)
```

   Импорт — **внутри** функции, а не в начале файла: `generated_files.py` сам импортирует `code_tools.py`, и импорт в начале файла даст круговую зависимость.

2. Ниже в той же функции замените строку:

```python
    cmd += _ruff_config_args(target, root)
```

   на:

```python
    cmd += ["--isolated"] if generated else _ruff_config_args(target, root)
```

   Остальное в `run_linter` не трогайте: `cwd=root` теперь корень помощника, а `--no-cache` в списке `cmd` уже стоит с практики 2 — без него ruff оставил бы `.ruff_cache` в корне помощника, и `test_lint_generated_writes_nothing` упал бы.

   `--isolated` — набор правил ruff по умолчанию без настроек помощника. В `ruff==0.17.0` он широкий: кроме `F` (неиспользуемые и неопределённые имена) в нём есть и `I001` — порядок импортов. Для ruff в корне помощника `main` бэкенда — сторонний модуль, как `fastapi`, поэтому `from main import app` должен стоять в одном блоке с `from fastapi.testclient import TestClient`, без пустой строки, по алфавиту имени модуля, а после блока импортов — ровно две пустые строки. Это правило уже есть в `CODER_BACKSTORY` каркаса (шаг 3.1): без него Кодер тратит все итерации на `I001`.

3. В обёртке `run_linter_tool` внизу файла описание параметра `path` — одна строка, она кончается точкой: `"." — весь репозиторий.` Замените её двумя строками — точка в конце первой становится точкой с запятой, вторая строка новая, чтобы модель знала о втором корне:

```python
            path: существующий файл или каталог относительно корня репозитория; "." — весь репозиторий;
                generated/test_<имя>.py — файл теста, записанный write_generated.
```

4. Запустите тесты и линтер:

```bash
python -m pytest -q tests/test_generated_tools.py
python -m pytest -q
ruff check ai/tools/code_tools.py ai/tools/generated_files.py tests/test_generated_tools.py
```

5. Закоммитьте:

```bash
git add ai/tools/code_tools.py
git commit -m "feat: lint generated/ as a second root"
git push
```

**Как понять, что получилось.** Первая команда — `16 passed`. Полный набор — прежнее число плюс 16 (в проверочном прогоне `38 passed` → `54 passed`), без `failed` и `error`; `tests/test_invariants.py` не изменён. `ruff check` — `All checks passed!`.

**Если не получилось**

- `ImportError: cannot import name 'check_generated_path' from partially initialized module` — импорт из `generated_files` поставлен в начало `code_tools.py`. Перенесите его внутрь `run_linter` (пункт 1).
- `ruff check` — `I001 Import block is un-sorted or un-formatted` в `code_tools.py` — импорт записан в одну длинную строку. `ruff check --fix ai/tools/code_tools.py` перестроит его сам.
- `test_lint_generated_ignores_assistant_config` упал — пункт 2 не сделан: для второго корня ruff нашёл ваш `ruff.toml`.
- `test_lint_generated_writes_nothing` упал — из `cmd` пропал `--no-cache`. Верните его: строка `cmd = [ruff, "check", "--output-format=json", "--no-fix", "--no-cache"]`.
- Упал тест `test_invariants.py` — правка задела путь бэкенда. Сравните с пунктами 1–2: для путей без `generated/` должен вызываться `check_path(path, s)` и `_ruff_config_args(target, root)`, как раньше.
- `test_tests_do_not_import_crewai` упал — в `generated_files.py` появился импорт CrewAI на уровне модуля. В каркасе CrewAI импортируется только внутри `crewai_tools()`.
- `rejected` при `git push` — другая пара уже отправила свои коммиты: `git pull --rebase`, затем `git push`.
- `git pull --rebase` ответил `error: cannot pull with rebase: You have unstaged changes.` — в рабочей папке незакоммиченные правки. `git status --short` покажет файлы. Ваши правки по шагам (например, `docs/crew-design.md`, `docs/adr/004-orchestration-pattern.md`) закоммитьте: `git add <файл>`, `git commit -m "docs: …"`; затем `git pull --rebase` и `git push`. Правку, которую коммитить рано, отложите: `git stash`, `git pull --rebase`, `git push`, `git stash pop`.

### Шаг 2.4 (пара 2, параллельно): `pytest.ini` и зависимости бэкенда (10 мин)

**Зачем это нужно.** Команда `python -m pytest -q` собирает все файлы `test_*.py` от корня помощника. Как только в `generated/` появится тест к бэкенду, обязательный набор начнёт зависеть от `fastapi` и от бэкенда, а на неделе 12 CI помощника, где их нет, упадёт. `testpaths = tests` ограничивает набор каталогом `tests/`; тесты из `generated/` запускаются отдельной командой. Зависимости бэкенда — в отдельном файле: CI помощника ставит только `requirements.txt`.

**Что сделать.** Строки `requirements-generated.txt` — пакеты, которые импортирует ваш бэкенд: `fastapi` всегда; `psycopg[binary]` — у бэкенда «Конфигурирования»; `python-dotenv` или `environs` — если их показал `grep` в шаге 1.3. На «Заметках» — только `fastapi`. Блоки ниже — для бэкенда «Конфигурирования» на `pydantic-settings`; вторую строку блока замените под свой бэкенд:

- «Заметки»: `printf 'fastapi\n' > requirements-generated.txt` (PowerShell: `Set-Content -Encoding ascii requirements-generated.txt "fastapi"`);
- python-dotenv или environs: допишите пакет в список — `printf 'fastapi\npsycopg[binary]\npython-dotenv\n' > requirements-generated.txt` (PowerShell: `Set-Content -Encoding ascii requirements-generated.txt "fastapi", "psycopg[binary]", "python-dotenv"`), с `environs` вместо `python-dotenv` — так же.

Git Bash:

```bash
printf '[pytest]\ntestpaths = tests\n' > pytest.ini
printf 'fastapi\npsycopg[binary]\n' > requirements-generated.txt
pip install -r requirements-generated.txt
pip check
python -m pytest
git add pytest.ini requirements-generated.txt
git commit -m "chore: add pytest testpaths and backend deps for generated tests"
git push
```

PowerShell:

```powershell
Set-Content -Encoding ascii pytest.ini "[pytest]", "testpaths = tests"
Set-Content -Encoding ascii requirements-generated.txt "fastapi", "psycopg[binary]"
pip install -r requirements-generated.txt
pip check
python -m pytest
git add pytest.ini requirements-generated.txt
git commit -m "chore: add pytest testpaths and backend deps for generated tests"
git push
```

На uv: `uv pip install -r requirements-generated.txt` и `uv pip check`.

**Как понять, что получилось.** `pip check` — `No broken requirements found.` `python -m pytest` (без `-q`: с ним заголовок не печатается) показывает в первых строках `configfile: pytest.ini` и `testpaths: tests`, в последней — **прежнее** число `passed`, как до занятия (в проверочном прогоне `38 passed`). Пара 1 уже отправила коммит с тестами (2.1), а ваш `git pull --rebase` его принёс — до коммита её каркаса (2.2) любой `python -m pytest -q` у вас печатает `ERROR tests/test_generated_tools.py`, `No module named 'ai.tools.generated_files'` и `1 error`. Это ожидаемо, продолжайте: пока пара 1 не закончила шаг 2.3, у вас будут `1 error` или `4 failed` в `tests/test_generated_tools.py` — это её незаконченная работа, а не ваша ошибка. Свои проверки сверяйте по остальным файлам: `failed` и `error` только в `tests/test_generated_tools.py`. После шага 2.3 пары 1 и `git pull` — прежнее число плюс 16.

**Если не получилось**

- В выводе pytest нет `configfile: pytest.ini` — файл лежит не в корне помощника или называется `pytest.ini.txt` (Блокнот Windows добавляет `.txt`): `ls pytest.ini`.
- `pip check` сообщает о конфликте версий — запишите строку в ADR 004; если тесты помощника после этого зелёные, продолжайте.
- `rejected` при `git push` — другая пара уже отправила свои коммиты: `git pull --rebase`, затем `git push`.

### Шаг 2.5 (пара 2, параллельно): `generated/conftest.py` и образец-тест (10 мин)

**Зачем это нужно.** Тест в `generated/` начинается со строки `from main import app`. Она выполняется, когда pytest собирает тест, — раньше любой фикстуры. К этому моменту нужны путь к бэкенду в `sys.path` и, с недели 8, переменная `DATABASE_URL`. `conftest.py` каталога pytest загружает раньше, чем собирает его тесты: всё, что задано в нём при загрузке, уже действует при импорте приложения. Совет «задать переменную через `monkeypatch.setenv`» здесь не работает: фикстура выполняется после импорта, и в проверочном прогоне тест с ней падал с `database_url Field required`.

**Что сделать**

1. Скопируйте каркас и создайте образец-тест — он проверяет только, что приложение бэкенда импортируется и отвечает, без Crew. Если приложение у вас в `app/main.py`, в образце напишите `from app.main import app`. Если у бэкенда нет `GET /`, возьмите любой `GET` без базы из шага 1.3.

```bash
mkdir -p generated
cp <клон курса>/templates/generated-conftest.py generated/conftest.py
```

   PowerShell: `New-Item -ItemType Directory -Force generated`, затем `Copy-Item <клон курса>\templates\generated-conftest.py generated\conftest.py`.

   Создайте в редакторе `generated/test_smoke.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_answers():
    response = client.get("/")
    assert response.status_code == 200
```

2. Запустите (одинаково в Git Bash и PowerShell):

```bash
python -m pytest generated -q
python -m pytest -q
git -C ../<проект> status --short
```

3. Закоммитьте — `generated/` в этой практике коммитится: преподаватель и соседняя команда увидят результат в PR, а `testpaths` не пускает эти файлы в набор помощника и в его CI:

```bash
git add generated/conftest.py generated/test_smoke.py
git commit -m "test: run generated tests against backend without changing it"
git push
```

**Как понять, что получилось.** Первая команда, пока Crew не записал свой тест (на любом маршруте), печатает `1 passed`:

```
.                                                                        [100%]
1 passed in 3.35s
```

Crew уже записал свой тест — `2 passed` или `1 failed, 1 passed` (тест Кодера упал, его разбирают шаги 3.3–3.4); этот шаг сверяйте по образцу: `python -m pytest generated/test_smoke.py -q` печатает `1 passed`. `1 passed, 1 warning` и в тексте `StarletteDeprecationWarning` — в окружении старая версия `fastapi`; тест проходит, это норма. Вторая команда — прежнее число `passed` (тест из `generated/` в набор не попал); `1 error` с `No module named 'ai.tools.generated_files'` или `4 failed` в `tests/test_generated_tools.py` — пара 1 ещё не закончила шаги 2.2–2.3 (шаг 2.4, «Как понять»), это ожидаемо. `git status --short` бэкенда пуст. На учебном бэкенде — `ls ../sample-backend`: в нём ничего не появилось.

`conftest.py` делает три вещи (docstring каркаса): добавляет корень бэкенда из `AI_REPO_ROOT` в `sys.path`; задаёт `DATABASE_URL` недоступным адресом `postgresql://user:pass@127.0.0.1:1/db`, если переменная не задана в окружении; делает текущим каталогом корень бэкенда — как при обычном запуске бэкенда, настройки читают `.env` бэкенда, а не `.env` помощника. База не поднимается: тест не выбирает поведение, которому она нужна. Адрес базы из `.env` бэкенда не подставится: переменная окружения важнее значения из `.env` и у `pydantic-settings`, и у python-dotenv — в проверочном прогоне в обоих вариантах приложение получило недоступный адрес, даже когда в `.env` бэкенда был настоящий.

**Если не получилось**

- `ModuleNotFoundError: No module named 'fastapi'` (или `'psycopg'`) — шаг 2.4: `pip install -r requirements-generated.txt` в этом окружении. Другой пакет бэкенда (`environs`, `dotenv`) — допишите его строкой в `requirements-generated.txt` (для `dotenv` — `python-dotenv`) и повторите `pip install -r`.
- `ModuleNotFoundError: No module named 'main'` — `conftest.py` лежит не в `generated/`, `AI_REPO_ROOT` в `.env` указывает не на бэкенд, или приложение в `app/main.py` (тогда `from app.main import app`).
- `ModuleNotFoundError: No module named 'ai'` в `conftest.py` — запущен `pytest`, а не `python -m pytest`, или не из корня помощника.
- `pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings` и `database_url` / `Field required`, или `INTERNALERROR` с `SystemExit: Не заданы обязательные переменные окружения: DATABASE_URL`, или `EnvNotSetError` — одна причина: `generated/conftest.py` не скопирован или лежит не в `generated/`. Если он на месте — в окне задана пустая переменная `DATABASE_URL`: закройте окно и откройте новое.
- Та же ошибка, но с другим именем переменной (`secret_key`, `SECRET_KEY`, `POSTGRES_PASSWORD`) — бэкенд требует при импорте ещё одну переменную, а в его `.env` её нет. Допишите в `generated/conftest.py` рядом со строкой `DATABASE_URL` строку `os.environ.setdefault("SECRET_KEY", "test")` со своим именем (в каркасе есть закомментированный образец). Бэкенд не правится.
- `Extra inputs are not permitted [type=extra_forbidden]` — класс настроек бэкенда не принимает ключи, для которых нет полей, а в `.env` бэкенда такие ключи есть (например, `POSTGRES_PASSWORD`, `APP_PORT` для Compose). Проверьте, что в `generated/conftest.py` есть строка `os.chdir(BACKEND_ROOT)` из каркаса: без неё бэкенд читает `.env` помощника. Строка на месте — та же ошибка будет и при запуске самого бэкенда из его корня. Ради помощника бэкенд не правится: сообщите об этом в работе по «Конфигурированию» и запишите в ADR 004, что тест не запускается до исправления бэкенда.
- `git add` ответил `The following paths are ignored by one of your .gitignore files` — в `.gitignore` помощника есть `generated/`. Уберите эту строку: в этой практике каталог коммитится.
- `rejected` при `git push` — другая пара уже отправила свои коммиты: `git pull --rebase`, затем `git push`.
- Тест долго ждёт и падает на подключении к базе — в окне задана **настоящая** `DATABASE_URL` (`echo $DATABASE_URL`, PowerShell: `$env:DATABASE_URL`): `setdefault` её не перезаписывает. `unset DATABASE_URL` (PowerShell: `Remove-Item Env:DATABASE_URL`) и повторите.
- `SyntaxError` при импорте модуля бэкенда — в бэкенде синтаксис Python 3.14, а окружение помощника — 3.11–3.13. Импорт такого модуля из окружения помощника невозможен: выберите поведение из модуля без такого синтаксиса или запишите в ADR 004, что сгенерированный тест на этой машине не запускается.

### Шаг 2.6 (пара 2, параллельно или во время запуска Crew): Раздел 8 архитектуры — по факту (10 мин)

**Зачем это нужно.** На воркшопе в разделе 8 `docs/crew-design.md` осталась строка «как дать зависимости бэкенда, путь к модулю и `DATABASE_URL`, покажет практика 4». Теперь способ есть, и он должен быть записан там, где его найдут люди и Ревьюер на peer review.

**Что сделать.** Замените в разделе 8 строку «Как человек проверяет тест на неделе 8» своим текстом: команда `python -m pytest generated -q` из корня помощника; зависимости бэкенда — `requirements-generated.txt`, в CI помощника не ставятся; путь к приложению и `DATABASE_URL` — `generated/conftest.py`; какое поведение выбрано и почему ему не нужна база. Закоммитьте:

```bash
git add docs/crew-design.md
git commit -m "docs: describe how generated tests are run"
git push
```

**Как понять, что получилось.** В разделе 8 нет слов «покажет практика 4»; есть команда запуска.

**Если не получилось.** Конфликт при `git push` (пара 1 тоже пушила) — `git pull --rebase`, затем `git push`: пары правят разные файлы и разные разделы `crew-design.md`. `cannot pull with rebase: You have unstaged changes` — «Если не получилось» шага 2.3.

> **Стоп-точка (00:50)** — преподаватель: объявите смену ролей в обеих парах. Отметьте команды, у которых нет коммита `test:`.

### Закончили раньше?

- **Пара 1:** свой тест к `write_generated` по разделу 6 архитектуры — например, что запись в `generated/.env` или в `generated/test_x.py` с путём через обратные слэши `generated\..\ai\x.py` даёт ошибку. Имена своих тестов начинайте с `test_team_`.
- **Пара 2:** попробуйте поведение из раздела 1 руками: допишите в `generated/test_smoke.py` вторую функцию с запросом и ожидаемым ответом из раздела 1. Это эталон человека: в шаге 3.4 вы сравните его с тестом Кодера. Тест упал — поведение требует базы или в разделе 1 ошибка; поправьте раздел 1 до блока 3.

### Не успеваете?

Минимум к 01:10: пара 1 — обязательные тесты зелёные (`16 passed`), коммит `test:` раньше кода; пара 2 — `pytest.ini` и `python -m pytest generated -q` → `1 passed`. Раздел 8 (шаг 2.6) — во время запуска Crew в шаге 3.2 или дома; свои тесты — дома. Одна пара в команде — маршрут в начале блока 2. Если у пары 2 к 01:10 нет `1 passed`, сведение делайте без её файлов, блок 3 начинайте: тест, который напишет Кодер, проверите дома после исправления по Troubleshooting. Линтер и запись без пары 1 не работают — пара 1 доводит свои шаги до 01:20 за счёт сведения.

> **Стоп-точка (01:10)** — преподаватель: объявите сведение кода. Команды, у которых пара 2 не получила строку `1 passed` от `python -m pytest generated -q`, — путь «Не успеваете?» блока 2.

---

## Сведение кода двух пар (01:10–01:20)

### Шаг: всё — в `feature/crew` на машине Crew (10 мин)

**Что сделать.** Обе пары уже пушили свои коммиты. Кто ещё не отправил — `git push`; отказ — `git pull --rebase`, затем `git push`. Пары правили разные файлы, конфликтов быть не должно; если `CONFLICT` — оставьте строки обеих версий, удалите маркеры, `git add <файл>`, `git rebase --continue`.

На **машине Crew** и на каждой машине, где будут запускать тест из `generated/`:

```bash
git pull
pip install -r requirements-generated.txt
python -m pytest -q
python -m pytest generated -q
```

На **машине Crew** проверьте ещё, загрузилась ли модель (шаг 1.4): во втором окне напечатан ответ, а команда

```bash
ollama ps
```

(PowerShell — та же) показывает строку `qwen3:4b-instruct` и в столбце `UNTIL` — часы (`… hours from now`), а не минуты.

**Как понять, что получилось.** `python -m pytest -q` — прежнее число плюс 16 `passed` (`54 passed` в проверочном прогоне), `python -m pytest generated -q` — `1 passed`. В `git log --oneline -8` — коммиты обеих пар. На машине Crew модель в списке `ollama ps`.

**Если не получилось**

- `git pull` ответил `error: Your local changes to the following files would be overwritten by merge: …` (или `cannot pull with rebase: You have unstaged changes`) — на этой машине незакоммиченные правки в файлах, которые другая пара уже закоммитила (обычно `docs/crew-design.md`). Закоммитьте свои: `git add <файл>`, `git commit -m "docs: …"`, затем `git pull --rebase` и `git push` — git сольёт правки разных разделов сам; `CONFLICT` — как в первом абзаце шага. Коммитить рано — `git stash`, `git pull`, `git stash pop`.
- `ModuleNotFoundError` при запуске из `generated/` — пакеты бэкенда не стоят на этой машине: `pip install -r requirements-generated.txt` и «Если не получилось» шага 2.5.
- Запрос во втором окне ещё идёт — не прерывайте его: модель загружается, к шагу 3.2 она будет готова.
- Во втором окне ошибка или `ollama ps` не показывает модель — «Если не получилось» шага 1.4, затем повторите запрос загрузки модели во втором окне.

> **Стоп-точка (01:20)** — преподаватель: объявите смену ролей и начало блока 3. Перерыв — у каждой команды, когда у неё начался запуск Crew (шаг 3.2); у команды на маршруте «одна машина или одна пара» — после шага 2.5.

---

## Блок 3. Crew (01:20–02:15)

### Шаг 3.1: `ai/run_crew.py` по вашей архитектуре (15 мин)

**Зачем это нужно.** Две задачи по порядку, у каждой свой агент со своими Tools, Кодер получает только итог Исследователя — это и есть Sequential из раздела 4 архитектуры. В каркасе собраны места, где легко ошибиться: `context`, разделение Tools, `max_iter`, `max_execution_time`, отдельный объект LLM у каждого агента, подсчёт вызовов для ADR 004.

**Что сделать** (пара 1, на машине Crew)

1. Скопируйте каркас и сразу закоммитьте как есть — тогда на peer review соседняя команда увидит ваши правки отдельно:

```bash
cp <клон курса>/templates/crewai_example.py ai/run_crew.py
git add ai/run_crew.py
git commit -m "feat: add Crew skeleton"
```

   PowerShell: `Copy-Item <клон курса>\templates\crewai_example.py ai\run_crew.py`.

2. Navigator сверяет каркас с архитектурой и вносит правки в константы в начале файла (места с пометкой `TODO по вашей архитектуре`):

| Раздел `crew-design.md` | Где в каркасе | Что проверить |
|---|---|---|
| 1. Задача разработчика | `TEST_FILE` | Имя файла теста к вашему поведению: `generated/test_<латиница, цифры, _>.py`, не `test_smoke.py`. Кодер не видит `crew-design.md`: имя доходит до него только из этой константы |
| 2. Агенты | `RESEARCHER_ROLE` / `_GOAL` / `_BACKSTORY`, `CODER_…` | `role` и `goal` замените формулировками раздела 2, если они у вас есть; нет — оставьте каркасные. Главное правило каждого агента из последнего столбца допишите в `backstory`; правила каркаса в `backstory` (чтение файла с первой строки, только литералы в тесте, порядок импортов, запись, затем линтер, «не найдено» — без теста) не удаляйте |
| 3. Tools | `tools=[…]` у агентов в `build_crew` | У Исследователя — `search_codebase`, `read_file`, `search_docs`; первый Tool практики 1, если он в разделе 3, — в начало списка, импорт `from ai.tools.<модуль> import <имя>` — в блок строк `from ai.…` по алфавиту имени модуля. У Кодера — `write_generated` и `run_linter` |
| 5. Передача контекста | `RESEARCH_OUTPUT` — `expected_output` Исследователя | Все поля итога из раздела 5, у каждого — источник; строки «не найдено» и «ошибка Tool»; тело ответа — по полям, значение литералом (имя константы из кода — только в источник) или «вычисляет сервер» (в каркасе это уже есть) |
| 6. Цикл | `CODER_BACKSTORY`, `max_iter=5` | Одно исправление: запись, линтер, запись, линтер, итог. Не больше двух проверок линтером |
| 8. Ограничения | `MAX_TASK_SECONDS` | Ваше значение из раздела 8 (в каркасе 900) |

   Приложение у вас в `app/main.py` (шаг 2.5) — в образце начала файла в `CODER_BACKSTORY` замените `from fastapi.testclient import TestClient\nfrom main import app` на `from app.main import app\nfrom fastapi.testclient import TestClient`: ruff сортирует строки импорта по имени модуля, `app` стоит раньше `fastapi`. Строку правьте в исходнике как есть, с `\n`; остальной образец (`\n\n\ndef test_`) не меняйте.

   Правки Navigator'а отдельно не коммитьте: они уйдут в коммит шага 4.1 вместе с трассой, а коммит каркаса — в `git push` того же шага (или раньше, с любым коммитом блока 2 на маршруте одной машины).

   `MAX_TASK_SECONDS` агента не прерывает: `TimeoutError` приходит после конца его работы, реальный потолок — `max_iter` (справка «Паттерны в CrewAI» в `materials-4.md`). Если в разделе 8 у вас «лимит плюс один вызов» (прежняя редакция справки), исправьте его в шаге 4.3.

   Правило курса, оно же стоп-фактор оценки: в коде помощника — файлах `.py` каталога `ai/` — не вызывается `pytest`, ни через `subprocess`, ни через `pytest.main`. Помощник не запускает код бэкенда: тест запускает человек в шаге 3.4. Трасса в `ai/traces/` под правило не попадает: в ней текст, который написала модель. Ревьюер и преподаватель ищут эти слова поиском, поэтому не пишите `pytest.main` и в промптах и комментариях — в каркасе их нет. Если в разделе 6 у вас «пишет код запуска» — сегодня Tool Кодера, смену решения запишите в ADR 004.

3. Проверьте, что Crew собирается (модель при этом не вызывается):

```bash
python -c "from ai.run_crew import build_crew; c = build_crew('x'); print([a.role for a in c.agents]); print([[t.name for t in a.tools] for a in c.agents])"
```

**Как понять, что получилось.** После импорта CrewAI (от 20 секунд до двух минут, на медленной машине дольше; терминал в это время молчит) напечатано (с вашими ролями и Tools):

```
['Исследователь кода бэкенда', 'Автор pytest-тестов']
[['search_codebase', 'read_file', 'search_docs'], ['write_generated', 'run_linter']]
```

`run_linter` — только у Кодера, `write_generated` — только у Кодера.

**Если не получилось**

- `ModuleNotFoundError: No module named 'ai.tools.generated_files'` — сведение не сделано на этой машине: `git pull`.
- `KeyError: 'search_codebase'` — в вашем `code_tools.py` обёртки названы иначе: подставьте свои имена в `code[…]`.
- `ValueError: Function must have a docstring` — у обёртки Tool удалили docstring: это описание для модели, оно обязательно.

### Шаг 3.2: Запуск 1 (20 мин)

**Что сделать.** На машине Crew. В команде — задача разработчика из раздела 1 вашей архитектуры: **замените пример своей**, без кавычек внутри. Пишите её, как в примере: «Нужен тест: » и строка раздела 1 «Что проверяет тест» — метод, путь, статус и поле ответа, а не строка «Как разработчик сказал бы её в чате»: по методу и пути Исследователь ищет обработчик. Запуск 1 начните не позже 01:40: позже он не успеет закончиться к 02:15.

Git Bash:

```bash
export PYTHONUTF8=1
python -m ai.run_crew "Нужен тест: GET /version отвечает 200, в ответе version и team" 2>&1 | tee ai/traces/run-p4-01.log
```

PowerShell:

```powershell
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
python -m ai.run_crew "Нужен тест: GET /version отвечает 200, в ответе version и team" 2>&1 | Tee-Object -FilePath ai\traces\run-p4-01.log
(Get-Content ai\traces\run-p4-01.log) | Set-Content -Encoding utf8 ai\traces\run-p4-01.log
```

Запуск идёт **10–25 минут** на CPU. Не прерывайте его и не запускайте на этой Ollama ничего другого. Пока он идёт — перерыв, затем пара 2 начинает шаг 4.3 (ADR 004: «Контекст», «Рассмотренные варианты»), Navigator пары 1 следит за трассой: какой агент работает, какой Tool вызван.

**Как понять, что получилось.** Проверка после конца запуска (Git Bash; PowerShell — `Select-String -Path ai\traces\run-p4-01.log -Pattern "Tool: write_generated","Tool: run_linter","Traceback","вызовов LLM"`):

```bash
grep -E "Tool: write_generated|Tool: run_linter|Traceback" ai/traces/run-p4-01.log | head -20
grep "вызовов LLM" ai/traces/run-p4-01.log
ls generated
git -C ../<проект> status --short
ruff check --isolated --no-cache generated/
```

- В трассе есть строки `Tool: write_generated` и `Tool: run_linter` — так в панели `Tool Execution Started` выглядит вызов инструмента; слова `Traceback` нет.
- Ближе к концу трассы, сразу после итога Кодера, есть строка `вызовов LLM: N, время: M мин`. Эти числа идут в ADR 004. Ожидаемо для двух агентов — 7–12 вызовов. Ниже неё — панель `Crew Completion` (итог повторяется целиком) и, как правило, `Tracing Status` (`Info: Tracing is disabled`) — она печатается и при `CREWAI_TRACING_ENABLED=false` в `.env`, это норма; файл заканчивается рамкой панели. Панель `Update Available` в начале трассы — CrewAI сообщает о новой версии; не обновляйте, версия закреплена в `requirements.txt`.
- В `generated/` появился `test_<кратко>.py` рядом с `conftest.py` и `test_smoke.py`.
- `git status --short` бэкенда пуст (на «Заметках» — `ls ../sample-backend` без новых файлов).
- `ruff check --isolated --no-cache generated/` (одинаково в Git Bash и PowerShell) — обязательно при любом исходе запуска: Кодер может написать в итоге «замечаний нет», даже если последний `run_linter` дал замечание. Ожидаемо `All checks passed!`. Вывод `Found 1 error.` или `Found N errors.` (под ним может быть `[*] 1 fixable with --fix`) — файл не исправляйте ни руками, ни `--fix`: код замечания (`I001`, `F401`, …) и что Кодер написал в итоге — в описание PR и в ADR 004 (шаги 4.1 и 4.3); оценку это не снижает. Что значит код — подпункты пункта про `Maximum iterations` в «Если не получилось».

Ответ модели проверяется по критериям, а не по тексту: тест записан, проверен линтером, итоговый файл проверен `ruff`, Crew завершилась. Качество теста оценивается в шаге 3.4, а не здесь. Вставки вида `[32m` и `[0m` в логе — коды цвета терминала, не ошибка.

**Если не получилось**

- В трассе есть строка `Crew не уложилась в 900 с на задачу агента: результат не получен`, сразу под ней — `вызовов LLM: N, время: M мин`. В `crewai==1.15.22` `max_execution_time` не прерывает агента: CrewAI дожидается конца его работы (до `max_iter` вызовов) и только потом выбрасывает `TimeoutError`, а итог задачи теряется. Файл в `generated/` мог быть записан — проверьте `ls generated`. Запишите в ADR 004 число вызовов и минуты из строки `вызовов LLM`; поднять `MAX_TASK_SECONDS` и повторить — только если до 02:05 есть время, иначе дома.
- Запуск идёт больше 25 минут — не прерывайте его: ADR 004 пишите по оценке, замер впишете, когда запуск закончится (или дома).
- В трассе `LLM Call Failed` и `Request timed out` — в памяти Ollama две модели для агентов или рядом идёт `build`: строка [Troubleshooting практики 3](practice-3.md#troubleshooting). Ctrl+C, оставить одну модель, повторить.
- Кодер не вызвал `write_generated`, а написал тест текстом в финальном ответе — модель не воспользовалась Tool. Проверьте, что в `CODER_BACKSTORY` есть фраза про `write_generated`, и повторите **один** раз (лог — `run-p4-01-2.log`). Повторилось — находка для ADR 004; тест из ответа в файл руками не переносите. Причину запишите в описание PR и в ADR 004 (ниже).
- Первый `run_linter` Кодера стоит в трассе раньше `write_generated` или в том же шаге и отвечает `файл или каталог не найден` (бывает и `путь вне репозитория`) — модель вызвала оба Tool разом, линтер проверял ещё не записанный файл. Если дальше идут запись и проверка тем же путём — всё в порядке; правило «по одному инструменту за шаг» есть в `CODER_BACKSTORY` каркаса, не удаляйте его. Если в `generated/` уже лежал файл с тем же именем от прошлого запуска, ответа `не найден` не будет: линтер мог проверить старую версию, поэтому итоговая проверка `ruff` из «Как понять» обязательна.
- В трассе ответ `write_generated` — `путь вне каталога generated/` или `писать можно только файл generated/test_<имя>.py` — модель дала неверный путь, Tool её остановил. Если следующим шагом она записала правильный путь — всё в порядке, это проверка Tool в работе.
- В трассе у Кодера `Maximum iterations reached. Requesting final answer.`, а его последний Tool перед итогом — `write_generated`: Кодер исчерпал `max_iter`, последнюю версию файла линтер не проверял, даже если в итоге написано «замечаний нет». Итоговая проверка `ruff` из «Как понять» здесь тоже решает; при `Found …` допишите в ADR 004 к коду замечания, что цикл исправлений не уложился в `max_iter` (раздел 6 `crew-design.md`). Коды замечаний `ruff` (при любом исходе запуска) и что проверить для запуска 2:
  - `F401` (`imported but unused`, чаще всего `import pytest`) — лишний импорт. В `CODER_BACKSTORY` должно остаться правило каркаса «импортируешь только то, что тест использует».
  - `F821` (`Undefined name`) — в тесте имя из кода бэкенда, например константа, а не значение. Посмотрите в итоге Исследователя поле тела ответа (шаг 3.3): имя или выражение вместо литерала — потеря поля, причина в итоге Исследователя; в `RESEARCH_OUTPUT` должно остаться правило «значение литералом, имя константы — только в источник», в `CODER_BACKSTORY` — «в тесте только литералы и импортированные имена». В шаге 3.4 такой тест упадёт с `NameError`.
  - `I001` — блок импортов не по правилу (шаг 2.3). Две причины: после строк импорта одна пустая строка перед `def` вместо двух; модель отделяет `from main import app` пустой строкой как «свой» модуль или ставит его выше `fastapi`. В `CODER_BACKSTORY` должны остаться образец начала файла и расшифровка `I001`. Они на месте, а `I001` остался — так бывает на `qwen3:4b-instruct` и после правил каркаса: запишите находку в ADR 004, повторять запуск ради неё не нужно.
  - `invalid-syntax` (`Invalid assignment target` и др.) — синтаксическая ошибка в первой версии файла; чаще всего модель перенесла в код тело запроса JSON-строкой с экранированными кавычками из итога Исследователя. Исправление съедает одну проверку, на следующее замечание итераций не хватает. В `CODER_BACKSTORY` должно остаться правило «тело запроса пишешь словарём Python, без экранированных кавычек».

  Правило каркаса удалили в шаге 3.1 — верните его для запуска 2. Тест всё равно запустите в шаге 3.4.
- Исследователь написал «не найдено», Кодер тест не записал — это правильное поведение по архитектуре. Проверьте, что в задаче метод и путь записаны так же, как в коде бэкенда, и повторите один раз (лог — `run-p4-01-2.log`).
- Повтор дал тот же исход (тест текстом или «не найдено») — файла теста не будет, и это не снижает оценку, если причина записана. В описание PR и в ADR 004 — строка: «теста нет: не найдено» или «теста нет: тест текстом в ответе Кодера», какая трасса (`run-p4-01.log` или `run-p4-01-2.log`) и что, по-вашему, помешало. Трасса должна это показывать: «не найдено» — в итоге Исследователя (под первой строкой `Agent Final Answer`), «тест текстом» — код теста в итоге Кодера и ни одной строки `Tool: write_generated`. Запуск 2 с исправлением дома (домашнее задание, п. 2) рекомендуется, но не обязателен.
- `Connection refused` / `ConnectionRefused` при `localhost` — в `.env` поставьте `OLLAMA_BASE_URL=http://127.0.0.1:11434`.

> **Стоп-точка (01:50)** — преподаватель: запуск Crew у каждой команды должен идти или закончиться. Отметьте команды, у которых нет файла `ai/traces/run-p4-01.log`.

### Шаг 3.3: Передача контекста — по трассе (10 мин)

**Зачем это нужно.** Кодер получает ровно итог Исследователя — его панель `Agent Final Answer` в трассе (`Task.context`). Ответы Tools Исследователя до Кодера не доходят. Чего нет в этом итоге, того Кодер не знает: он угадает или пропустит. Здесь проверяется пункт Definition of Done «агенты передают контекст без потери критической информации».

**Что сделать** (пара 2, смена ролей)

1. Найдите в трассе первую панель `Agent Final Answer` — итог Исследователя (Git Bash: `grep -n "Agent Final Answer" ai/traces/run-p4-01.log`; PowerShell: `Select-String -Path ai\traces\run-p4-01.log -Pattern "Agent Final Answer"`) и откройте файл на этой строке. Строка `Agent Final Answer` одна на каждого агента, дошедшего до итога; текст итога — ниже, после строки `Final Answer:`.
2. Заполните таблицу по полям из раздела 5 `docs/crew-design.md` — она пойдёт в описание PR:

| Поле итога Исследователя (раздел 5) | Есть в итоге Исследователя (дошло до Кодера): да / нет | Использовано в тесте Кодера | Что исправили |
|---|---|---|---|
| Эндпоинт: метод и путь | | | |
| Файл, функция, строка обработчика | | | |
| Ожидаемый статус | | | |
| Ожидаемое тело или поле ответа | | | |
| Как тест получает приложение (импорт) | | | |
| Источник каждого факта | | | |
| Статус поиска | | | |

3. Поле «нет» — исправьте в `ai/run_crew.py`: нет в итоге — допишите поле в `RESEARCH_OUTPUT` (`expected_output` Исследователя); есть в итоге, но Кодер его не использовал — правило в `CODER_BACKSTORY`. В столбце «Что исправили» — что именно; в строке, где поле дошло и использовано (или тесту не нужно), — «исправлять нечего», клетку не оставляйте пустой. Строкой под таблицей: какой агент вы назвали на воркшопе 4 «сломается первым» и сломался ли он в запуске 1 (да / нет / сломался другой — какой).

Повторный запуск с исправлением — запуск 2 в «Закончили раньше?» или дома: на паре он не помещается.

**Как понять, что получилось.** Таблица заполнена, в последнем столбце нет пустых клеток; правки в `ai/run_crew.py` сохранены (или «исправлять нечего»).

**Если не получилось.** Строка `Agent Final Answer` в трассе одна — Crew остановилась после Исследователя: смотрите строки ниже его итога (`TimeoutError`, ошибка Tool) и «Если не получилось» шага 3.2.

### Шаг 3.4: Человек запускает сгенерированный тест (10 мин)

**Зачем это нужно.** Линтер проверяет код, а не смысл: тест с придуманным статусом или телом ответа он пропустит. Тест запускает человек — помощник код бэкенда не запускает.

**Что сделать.** Прочитайте тест Кодера и сравните запрос, статус и тело с разделом 1 архитектуры. Затем (одинаково в Git Bash и PowerShell):

```bash
python -m pytest generated -q
git -C ../<проект> status --short
```

Сохраните вывод pytest: он пойдёт в описание PR **с любым результатом**.

**Как понять, что получилось.** Ожидаемо — `2 passed` (`test_smoke.py` и тест Кодера); файла теста нет (шаг 3.2) — `1 passed`, вывод всё равно идёт в PR. Тест Кодера упал — это не провал занятия, а находка: в описании PR и в ADR 004 запишите, на чём он упал (`assert 404 == 200`, `KeyError`, `NameError`, `ModuleNotFoundError`) и откуда взялось неверное — из итога Исследователя (видно в таблице шага 3.3) или от Кодера. Тест в репозиторий бэкенда сегодня не переносится: PR в бэкенд — неделя 12. `git status --short` бэкенда пуст.

**Если не получилось**

- `ModuleNotFoundError: No module named 'main'`, а образец-тест проходит — Кодер написал другой импорт, чем у вас (`from app.main import app` или наоборот). Это потеря поля «как тест получает приложение»: строка в таблицу шага 3.3.
- Тест Кодера ждёт базу (`/health` → 200, запись заметки в базу) — Исследователь выбрал поведение, которому нужна база. Находка для ADR 004; поведение в разделе 1 уточните.
- `NameError: name '…' is not defined` (в шаге 3.2 линтер давал `F821`) — Кодер вставил в тест имя из кода бэкенда, например константу, вместо её значения. Посмотрите поле тела ответа в итоге Исследователя: там имя или выражение — неверное пришло из итога Исследователя, строка «нет» в таблице шага 3.3 и правка `RESEARCH_OUTPUT`; там литерал — ошибка Кодера, правило «в тесте только литералы и импортированные имена» в `CODER_BACKSTORY`. Тест руками не исправляйте: вывод pytest и причина — в PR и в ADR 004.
- Ошибки сбора, которых нет у образца, — «Если не получилось» шага 2.5.
- `1 passed` вместо `2 passed`, а `generated/test_smoke.py` изменился — Кодер записал свой тест под именем образца. Верните образец (`git checkout -- generated/test_smoke.py`), в `TEST_FILE` поставьте другое имя; находка — строкой в ADR 004.

### Закончили раньше?

По убыванию ценности. Запуск Crew — 10–25 минут, поэтому не начинайте пункты 1–3 позже 02:00.

1. **Запуск 2** после исправления контекста (шаг 3.3): та же команда, лог `ai/traces/run-p4-02.log`. В PR — изменилась ли таблица и число вызовов.
2. **Ревьюер.** Раскомментируйте блок в конце `build_crew`: третий агент без Tools сверяет тест с итогом Исследователя. Запуск — плюс 1–2 вызова LLM; в ADR 004 — что он нашёл и сколько стоил.
3. **Hierarchical** — только после работающего Sequential: `process=Process.hierarchical` и `manager_llm=get_llm()`. Ошибки CrewAI при неверной настройке — справка «Паттерны в CrewAI» в [`materials-4.md`](materials-4.md#справка-паттерны-в-crewai). На `qwen3:4b-instruct` курс этот вариант не проверял; сравнение числа вызовов — в ADR 004.
4. **Guardrail вместо цикла у Кодера:** `Task(guardrail=<функция>)`, функция вызывает `run_linter` и возвращает замечания. Guardrail вызывает **только** `run_linter`, не pytest. Описание — [CrewAI: Tasks](https://docs.crewai.com/en/concepts/tasks), раздел *Task Guardrails*.

### Не успеваете?

Минимум к 02:15: запуск 1 закончился или идёт, трасса сохраняется, таблица шага 3.3 заполнена хотя бы по тому, что видно. Запуск закончился после 02:00 — шаги 3.3 и 3.4 делайте одновременно: пара 2 — таблица шага 3.3, пара 1 — шаг 3.4 во втором окне машины Crew (pytest не обращается к Ollama). Если запуск ещё идёт в 02:15, не прерывайте его: блок 4 делайте параллельно на другой машине, трассу и вывод шага 3.4 добавьте в PR, когда запуск закончится.

> **Стоп-точка (02:15)** — преподаватель: объявите блок 4 и назовите пары команд для peer review.

---

## Блок 4. PR, peer review, ADR (02:15–02:55)

### Шаг 4.1: Коммит и Pull Request (10 мин)

**Что сделать**

1. `git status --short`: в списке `ai/run_crew.py`, `ai/traces/run-p4-01.log`, `generated/test_<кратко>.py` (если Кодер его записал); нет `.env` и `.chroma/`. Был повтор в шаге 3.2 — допишите в `git add` ниже и `ai/traces/run-p4-01-2.log`. Тест Кодера коммитится с любым результатом шага 3.4, в том числе упавший: в PR этой практики показывают результат запуска, а не принятый тест. Если в разделе 6 `crew-design.md` у вас «коммитим только тест, который человек принял», это решение меняется — запишите его в шаге 4.3 («`generated/` коммитим»).
2. Закоммитьте и опубликуйте:

```bash
git add ai/run_crew.py ai/traces/run-p4-01.log generated/
git commit -m "feat: add Crew of researcher and coder"
git push
```

3. Откройте Pull Request `feature/crew` → `main` помощника. В описании:
   - роли в блоках 1–4 (кто в какой паре);
   - вывод `python -m pytest -q tests/test_generated_tools.py` до кода (красный, шаг 2.1) и полного `python -m pytest -q` сейчас (последняя строка с `passed`);
   - вывод `python -m pytest generated -q` (шаг 3.4) — любой;
   - строка `вызовов LLM: N, время: M мин` из трассы и на какой машине и модели шёл запуск;
   - вывод `ruff check --isolated --no-cache generated/` (шаг 3.2); при `Found …` — код замечания и что Кодер написал в итоге;
   - таблица передачи контекста из шага 3.3 и строка под ней: какой агент вы назвали на воркшопе 4 и сломался ли он; трасса — от `ai/run_crew.py` до правок шага 3.3, в коммите он уже с ними;
   - файла теста нет — причина из шага 3.2 («не найдено» или «тест текстом») и имя трассы, где это видно.
4. Ссылку на PR — в общий чат курса.

**Как понять, что получилось.** Во вкладке Files changed есть `docs/crew-design.md`, `docs/adr/004-orchestration-pattern.md`, `tests/test_generated_tools.py`, `ai/tools/generated_files.py`, `ai/tools/code_tools.py`, `pytest.ini`, `requirements-generated.txt`, `generated/conftest.py`, `generated/test_*.py` (если записан), `ai/run_crew.py`, `ai/traces/run-p4-01.log`. Во вкладке Commits коммит `test: …` с `tests/test_generated_tools.py` сделан раньше коммита с `ai/tools/generated_files.py` (сверяйте время, а не место в списке). Если PR практики 3 не влит (шаг 1.2, «Влить сейчас нельзя»), в Files changed будут и его файлы — напишите об этом в первой строке описания.

**Если не получилось.** `rejected` при `git push` — `git pull --rebase`, затем `git push`.

> **Стоп-точка (02:25)** — преподаватель: попросите каждую команду отправить ссылку на свой PR в общий чат одним сообщением и начните peer review.

### Шаг 4.2: Peer review (15 мин)

Первые 8 минут читаете PR пары и оставляете комментарии в строках diff, следующие 7 — разбираете замечания к своему. Формула: **что заметил → чем грозит → что предлагаю**.

**Чек-лист для проверки чужого PR**

- [ ] Нет `.env` и `.chroma/` ни в Files changed, ни в коммитах; есть `pytest.ini` с `testpaths = tests` и `requirements-generated.txt`; в `requirements.txt` пакетов бэкенда (`fastapi`, `psycopg`) нет.
- [ ] В Commits коммит с `tests/test_generated_tools.py` раньше коммита с `generated_files.py`; обязательные тесты не изменены (сравните с шагом 2.1).
- [ ] В `generated_files.py` и `code_tools.py` нет `shell=True`, `os.system`, записи вне `generated/`; в файлах `.py` каталога `ai/` нет `pytest` в `subprocess` и нет `pytest.main` (трасса в `ai/traces/` не в счёт; строка `python -m pytest generated -q` в docstring каркаса — подсказка человеку, а не вызов).
- [ ] `ai/run_crew.py`: у каждого агента `role`, `goal`, `backstory`, `max_iter=5`, `max_execution_time`; `write_generated` и `run_linter` — только у Кодера; у Кодера `context` с задачей Исследователя.
- [ ] `RESEARCH_OUTPUT` перечисляет поля из раздела 5 их `crew-design.md`, включая источник и «не найдено».
- [ ] В трассе `run-p4-01.log` (или `run-p4-01-2.log`) `Traceback` нет, есть строка `вызовов LLM: N, время: M мин`; есть `Tool: write_generated` и `Tool: run_linter` — или файла теста нет, а причина названа в PR и в ADR 004 (шаг 3.2). В описании PR — вывод `ruff check --isolated --no-cache generated/`: `All checks passed!` или код замечания, он же в ADR 004.
- [ ] Сгенерированный тест: запрос, статус и тело совпадают с разделом 1 их архитектуры; тест не требует базы.
- [ ] В описании PR — таблица передачи контекста и вывод `python -m pytest generated -q`.
- [ ] Если всё остальное проверено и есть доступ к их репозиторию: в клоне их ветки `python -m pytest -q` зелёный. Ollama для тестов не нужна.

### Шаг 4.3: ADR 004 «Принято» и архитектура по факту (15 мин)

Доведите `docs/adr/004-orchestration-pattern.md` по [каркасу ADR 004](materials-4.md#каркас-adr-004) до статуса «Принято»: в «Решение» допишите замер, в «Последствия» — минус. Обновите в `docs/crew-design.md` то, что решили иначе, чем на воркшопе: раздел 4 — число вызовов по замеру рядом с оценкой, 5 — поля итога после шага 3.3, 6 — кто пишет файл (`write_generated`), сколько было вызовов `run_linter`, `generated/` коммитим, 8 — `max_execution_time` и время запуска по факту. ADR 003 бэкенда и ADR 003 помощника называйте вместе с репозиторием. Закоммитьте в ту же ветку:

```bash
git add docs/adr/004-orchestration-pattern.md docs/crew-design.md
git commit -m "docs: accept ADR 004 with measured Crew run"
git push
```

Что дописать в ADR 004 (остальные разделы — из черновика):

```markdown
**Статус:** Принято

## Решение
…(из черновика)…
Замер запуска 1: <N> вызовов LLM, <M> мин, <машина: CPU / GPU>, модель <…>.
Оценка из crew-design.md, раздел 4: <…> вызовов, <…> мин. Расхождение: <почему>.
Запись теста — Tool Кодера write_generated, только файлы generated/test_*.py;
run_linter проверяет generated/ вторым корнем с --isolated.
Итоговая проверка ruff check --isolated generated/: <All checks passed! / код замечания и что Кодер написал в итоге>.
max_execution_time: <…> с — <почему это число по замеру>.

## Последствия
Минус: <например: запуск 15 минут на CPU; Кодер видит только итог Исследователя,
поле … терялось; линтер не проверяет смысл теста — его проверяет человек>.
```

**Как понять, что получилось.** В ADR 004 статус «Принято», есть числа вызовов и минут; не осталось заполнителей каркаса в угловых скобках (`<N>`, `<…>`, `<почему>`). В разделах 4, 5, 6, 8 `crew-design.md` нет `…` и `<…>`.

**Документация.** [adr.github.io](https://adr.github.io/) — шаблоны; глубину аргументации берите из ADR 001–003 помощника.

---

## Итог (02:55–03:00)

Команда отвечает по чек-листу самопроверки: всё закрыто или что именно осталось. Незакрытое уходит в домашнее задание, в тот же PR.

> **Стоп-точка (02:55)** — преподаватель: соберите у команд ответ — закрыт ли чек-лист самопроверки (да / что осталось).

---

## Чек-лист самопроверки команды

**Репозиторий**

- [ ] `feature/crew` отведена от `main` с кодом практик 1–3 (или он подтянут в неё, и это сказано в PR); PR в `main` открыт, ссылка в чате.
- [ ] `pytest.ini` с `testpaths = tests`; `requirements-generated.txt`; пакеты бэкенда не в `requirements.txt`.
- [ ] `.env` и `.chroma/` нет в diff; в репозитории бэкенда ничего не изменено.

**Tools и тесты**

- [ ] `tests/test_generated_tools.py` без изменений, коммит `test:` раньше кода; `tests/test_invariants.py` без изменений; `python -m pytest -q` зелёный.
- [ ] `write_generated` пишет только `generated/test_<имя>.py`; `run_linter` проверяет `generated/` вторым корнем.
- [ ] `python -m pytest generated -q` запускается из корня помощника, бэкенд не меняется.

**Crew**

- [ ] `ai/run_crew.py` по `docs/crew-design.md`: два агента, `max_iter=5`, `max_execution_time`; в коде `ai/` нет запуска pytest.
- [ ] `run-p4-01.log` — `Tool: write_generated`, `Tool: run_linter`, строка числа вызовов, без `Traceback`; тест Кодера в `generated/`; `ruff check --isolated --no-cache generated/` — `All checks passed!` или код замечания в PR и в ADR 004. Теста нет — причина («не найдено» или «тест текстом») в PR и в ADR 004.
- [ ] Таблица передачи контекста и вывод запуска сгенерированного теста — в описании PR.

**Документы**

- [ ] ADR 004 «Принято» с замером и минусом; `docs/crew-design.md` обновлён по факту.
- [ ] Роли — в описании PR; замечания peer review — в PR.

---

## Что сдаётся по итогам занятия

Одна **ссылка на Pull Request** `feature/crew` → `main` в репозитории помощника, отправленная в общий чат до конца пары. В нём: архитектура, Tool записи и второй корень с тестами, настройка запуска тестов из `generated/`, Crew, трасса, сгенерированный тест (или причина, почему его нет, — шаг 3.2), ADR 004, роли, выводы `pytest` и таблица передачи контекста в описании, комментарии соседней команды. Незаконченное доделывается дома в тот же PR (домашнее задание, п. 1).

---

## Troubleshooting

| Симптом | Вероятная причина | Что сделать |
|---|---|---|
| `ModuleNotFoundError: No module named 'ai.tools.generated_files'` | Каркас ещё не скопирован — до шага 2.2 это ожидаемо; на машине Crew — не сделано сведение | Шаг 2.2; `git pull` |
| Четыре теста `test_lint_generated_…` / `test_generated_prefix_means_assistant` падают | `run_linter` не правлен под второй корень | Шаг 2.3 |
| `cannot import name 'check_generated_path' from partially initialized module` | Импорт из `generated_files` в начале `code_tools.py` | Импорт — внутри `run_linter` (шаг 2.3, п. 1) |
| `ruff check`: `I001` в `code_tools.py` | Импорт в одну длинную строку | `ruff check --fix ai/tools/code_tools.py` |
| `test_lint_generated_writes_nothing` или `test_linter_skips_denied_and_writes_nothing` упал | Из команды ruff пропал `--no-cache` | Вернуть `--no-cache` в `cmd` |
| `test_tests_do_not_import_crewai` упал | Импорт CrewAI на уровне модуля в `generated_files.py` или тестах | Импорт — только внутри `crewai_tools()` |
| `python -m pytest -q` собирает `generated/` и падает на импорте бэкенда | Нет `pytest.ini` в корне помощника или файл называется `pytest.ini.txt` | Шаг 2.4; в выводе `python -m pytest` без `-q` должно быть `configfile: pytest.ini` |
| `ModuleNotFoundError: No module named 'fastapi'` / `'psycopg'` при `python -m pytest generated -q` | Зависимости бэкенда не стоят в этом окружении | `pip install -r requirements-generated.txt` |
| `ModuleNotFoundError: No module named 'environs'` / `'dotenv'` или другой пакет бэкенда | Пакета нет в `requirements-generated.txt` | Дописать его строкой (`dotenv` — `python-dotenv`), `pip install -r requirements-generated.txt` (шаг 2.4) |
| `ModuleNotFoundError: No module named 'main'` | `conftest.py` не в `generated/`; неверный `AI_REPO_ROOT`; приложение в `app/main.py` | Шаг 2.5, «Если не получилось» |
| `ModuleNotFoundError: No module named 'ai'` в `generated/conftest.py` | Запущен `pytest`, а не `python -m pytest`, или не из корня помощника | `python -m pytest generated -q` из корня помощника |
| `ValidationError: 1 validation error for Settings` / `database_url` / `Field required` | `DATABASE_URL` не задана к импорту приложения: нет `generated/conftest.py` | Скопировать каркас в `generated/conftest.py` (шаг 2.5) |
| `INTERNALERROR` … `SystemExit: Не заданы обязательные переменные окружения: DATABASE_URL` | То же, бэкенд с `os.environ` или python-dotenv | То же |
| `EnvNotSetError` | То же, бэкенд с environs | То же |
| `ValidationError` / `Field required` или `Не заданы обязательные переменные окружения` с другим именем (`secret_key`, `SECRET_KEY`) | Бэкенд требует при импорте ещё одну переменную, а в его `.env` её нет | Строка `os.environ.setdefault("<ИМЯ>", "test")` в `generated/conftest.py` рядом с `DATABASE_URL` (шаг 2.5) |
| `Extra inputs are not permitted [type=extra_forbidden]` | Настройки бэкенда прочитали `.env` с ключами, для которых нет полей: нет `os.chdir(BACKEND_ROOT)` в `generated/conftest.py` или такие ключи в `.env` самого бэкенда | Вернуть строку из каркаса; если она есть — запись в ADR 004, бэкенд не правится (шаг 2.5) |
| `1 passed, 1 warning`, `StarletteDeprecationWarning` | Старая версия `fastapi` в окружении помощника | Норма, тест проходит |
| `The following paths are ignored by one of your .gitignore files` при `git add generated/…` | В `.gitignore` помощника есть `generated/` | Убрать строку: в этой практике `generated/` коммитится |
| Тест долго ждёт и падает на подключении к базе | В окне задана настоящая `DATABASE_URL`, `setdefault` её не перезаписывает | `unset DATABASE_URL` (PowerShell: `Remove-Item Env:DATABASE_URL`) |
| `SyntaxError` при импорте модуля бэкенда | Синтаксис Python 3.14 в бэкенде, окружение помощника 3.11–3.13 | Другое поведение из модуля без такого синтаксиса или запись в ADR 004 (шаг 2.5) |
| Тест бэкенда в своём каталоге `generated/` не виден `run_linter` | Префикс `generated/` всегда означает каталог помощника | Так задумано: бэкенд проверяйте путями без `generated/` |
| Ответ `write_generated`: `путь вне каталога generated/` или `писать можно только файл generated/test_<имя>.py` | Модель дала неверный путь или имя | Норма, если следующим шагом она записала верный путь; иначе — правило в `CODER_BACKSTORY` |
| `run_linter("generated/…")` → `файл или каталог не найден` в трассе | Кодер проверил файл до записи или `run_linter` не правлен | Шаг 2.3; порядок «запись, затем линтер» — в `CODER_BACKSTORY` |
| `Crew не уложилась в … с на задачу агента` | Агент работал дольше `MAX_TASK_SECONDS`; CrewAI сообщает об этом только после конца работы агента | Записать замер в ADR 004; поднять `MAX_TASK_SECONDS` и повторить, если есть время (шаг 3.2) |
| Число вызовов в строке `вызовов LLM` вдвое больше, чем вызовов в трассе | Один объект LLM на два агента: CrewAI суммирует счётчик по агентам | У каждого агента свой `llm=get_llm()`, как в каркасе |
| Запрос к модели или запуск висит, `Connection refused` при `localhost` | `localhost` сначала пробует IPv6, Ollama слушает IPv4 | `OLLAMA_BASE_URL=http://127.0.0.1:11434` в `.env` и в командах |
| `LLM Call Failed`, `Request timed out` | В памяти две модели для агентов или рядом идёт `build` | `ollama ps`, лишнюю — `ollama stop <модель>`; одна долгая команда на машину |
| Первый вызов LLM идёт 8–10 минут | Модель загружалась в память во время запуска | Шаг 1.4: загрузка с `keep_alive` до блока 3 |
| `Sync handler error … 'charmap' codec` в логе | Не задан `PYTHONUTF8=1` | Шаг 3.2 |
| Лог в PR показан как двоичный | `Tee-Object` в Windows PowerShell 5.1 пишет UTF-16 | `(Get-Content <лог>) \| Set-Content -Encoding utf8 <лог>` |
| `untracked working tree files would be overwritten` при `git switch feature/crew` | У вас своя незакоммиченная копия архитектуры, в ветке — закоммиченная | Шаг 1.2, «Если не получилось» |

---

## Домашнее задание (СРС, 1,5–2 часа)

**Срок — до воркшопа 5.**

1. **Хвосты с пары (30–60 мин).** Закройте замечания peer review, доделайте трассу, таблицу передачи контекста, ADR 004 и разделы 4–6, 8 архитектуры. Затем влейте PR в `main` помощника (одобряет участник, который не автор PR): практика 5 начнётся с ветки от `main`, где уже есть Crew, `write_generated` и `generated/conftest.py`. Влить нельзя — напишите в описании PR, что мешает.
2. **Запуск 2 (20–30 мин, машина считает сама).** Рекомендуется, если на паре не успели или файла теста нет (шаг 3.2), но не обязателен: запуск с исправлением из шага 3.3, лог `ai/traces/run-p4-02.log`, затем `python -m pytest generated -q`. В PR и в ADR 004 — изменилась ли таблица и число вызовов.
3. **README помощника (15 мин).** Раздел «Crew»: агенты и их роли, команда запуска `python -m ai.run_crew "…"` и что получает человек (файл в `generated/`, трасса), как запустить сгенерированный тест (`python -m pytest generated -q`, `requirements-generated.txt`), что нужна Ollama с моделью для агентов и моделью эмбеддингов, а индекс строится до запуска. Это требования «Definition of Done» к README.
4. **Бэкенд обновился (10 мин).** Если после пары в бэкенд влили изменения (например, `settings.py` при GitFlow попал в `main`): `git -C ../<проект> pull`, `python -m pytest generated -q` — проходит ли тест Кодера. Ответ — строкой в ADR 004. На учебных «Заметках» пункт пропустите: это не git-репозиторий, и он не обновляется.
5. **Если в команде есть облачный ключ (20 мин).** Один запуск по пути Б (`LLM_PROVIDER=cloud`, ключ — в `CLOUD_API_KEY` в `.env`, как в практике 1, шаг 2.2: другие имена переменных, например `OPENROUTER_API_KEY`, помощник не читает; эмбеддинги остаются локальными), лог — `ai/traces/run-p4-01-cloud.log`. Один запуск — 7–12 запросов из 50 бесплатных в сутки на OpenRouter. В ADR 004 — число вызовов и минуты по сравнению с Ollama. Помните: код бэкенда и найденные фрагменты документации уходят провайдеру.

Тест из `generated/` в репозиторий бэкенда сейчас не переносите: Pull Request теста в бэкенд по его `CONTRIBUTING.md` — неделя 12, когда в бэкенде появятся pytest и тесты в CI.

---

## Сводка ссылок

**CrewAI**

- [Tasks](https://docs.crewai.com/en/concepts/tasks) — *Task Dependencies and Context*, *Task Guardrails*.
- [Agents](https://docs.crewai.com/en/concepts/agents) — *Agent Attributes*: `max_iter`, `max_execution_time`.
- [Crews](https://docs.crewai.com/en/concepts/crews) — *Crew Usage Metrics*, *Crew Output Attributes* (`token_usage`).
- [Processes](https://docs.crewai.com/en/concepts/processes) — Sequential и Hierarchical.
- [Справка курса «Паттерны в CrewAI»](materials-4.md#справка-паттерны-в-crewai), [каркас `crew-design.md`](materials-4.md#каркас-docscrew-designmd), [каркас ADR 004](materials-4.md#каркас-adr-004).

**pytest и FastAPI**

- [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/) — `TestClient`.
- [pytest: python -m pytest и sys.path](https://docs.pytest.org/en/stable/explanation/pythonpath.html) — *Invoking pytest versus python -m pytest*.
- [pytest: conftest.py](https://docs.pytest.org/en/stable/how-to/writing_plugins.html#conftest-py-local-per-directory-plugins) — `conftest.py` каталога.
- [pytest: Configuration](https://docs.pytest.org/en/stable/reference/customize.html) — `pytest.ini`, `testpaths`.
- [python-dotenv](https://pypi.org/project/python-dotenv/) — *Getting Started*: `load_dotenv()` не перезаписывает заданные переменные (`override=False`).

**Ollama**

- [Ollama API: Generate a response](https://docs.ollama.com/api/generate) — `keep_alive`, `stream`.

**Каркасы курса и процесс**

- [`templates/crewai_example.py`](../templates/crewai_example.py), [`templates/generated_files.py`](../templates/generated_files.py), [`templates/generated-conftest.py`](../templates/generated-conftest.py).
- [Conventional Commits (рус.)](https://www.conventionalcommits.org/ru/v1.0.0/).
- [Architectural Decision Records](https://adr.github.io/).

---

## История изменений

| Дата | Что изменено |
|---|---|
| 2026-10-27 | Первая версия: вливание PR практики 3 и ветка `feature/crew` (маршруты «ветка уже есть», «влить нельзя», «архитектура в рабочей папке», «архитектуры нет»); состояние бэкенда недели 8 и выбор поведения без базы; индекс и загрузка модели с `keep_alive` до Crew; две пары: Tool `write_generated` и второй корень `run_linter` (`--isolated`, корень помощника) с обязательными тестами до кода, запуск теста из `generated/` — `pytest.ini` с `testpaths = tests`, `requirements-generated.txt`, `generated/conftest.py` (путь к бэкенду, `DATABASE_URL`, текущий каталог — корень бэкенда); каркасы `templates/crewai_example.py`, `templates/generated_files.py`, `templates/generated-conftest.py`; Crew Исследователь → Кодер, строка числа вызовов LLM и времени, сообщение при превышении `max_execution_time`; таблица передачи контекста по трассе; запуск сгенерированного теста человеком; ADR 004 «Принято» с замером |
