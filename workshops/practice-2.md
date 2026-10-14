# Практика 2. Инструменты для работы с кодом бэкенда

**Длительность:** 180 минут (2 пары)
**Формат:** самостоятельная командная работа по этому руководству. Pair Programming со сменой ролей Driver / Navigator, тесты до кода, в конце — peer review с соседней командой и ADR.
**Роль преподавателя:** организационная. Он следит за временем, объявляет стоп-точки, фиксирует прогресс команд и назначает пары для peer review. Всё содержание занятия — в этом файле и по ссылкам из него.

> Руководство рассчитано на то, что вы дойдёте до конца сами. Если шаг не получается — сначала читайте блок «Если не получилось» у этого шага, потом таблицу Troubleshooting в конце файла, потом документацию по ссылке.

**Проверено на:** Windows 11; тесты и каркас [`templates/tool-lsp-example.py`](../templates/tool-lsp-example.py) — Python 3.11 и 3.13, `ruff==0.17.0`, `pytest==9.1.1`, `pydantic-settings==2.15.0`; обёртки для агента — Python 3.11–3.13, `crewai==1.15.22`, Ollama с `qwen3:4b-instruct` и `qwen2.5:7b` на CPU; бэкенд недели 4 «Конфигурирования» (`main.py` с `GET /`, `/health`, `/version`) и учебный `templates/sample-backend/` — октябрь 2026. macOS и Linux не проверялись.

---

## Что вы сделаете сегодня

**Проблема.** Агенту-ревьюеру нужно найти функцию в бэкенде, прочитать её и проверить линтером. Как только инструмент принимает путь от модели, `read_file("app/../.env")` отдаёт ключи, поиск на 4 000 совпадений забивает контекст, а упавший линтер агент пересказывает как «замечаний нет». На воркшопе 2 вы нашли эти дыры в своих спецификациях и записали пять атак. Сегодня атаки становятся тестами, а спецификация — кодом, который эти тесты проходит.

В конце занятия в репозитории помощника `<проект>-assistant` будет:

1. Ветка `feature/code-tools` (со спецификацией v2 с воркшопа 2 и кодом практики 1) и Pull Request в `main` с комментариями соседней команды.
2. `ai/tools/code_tools.py` — три инструмента: `read_file`, `search_codebase` (подстрока и `kind="symbol"` — аналог ctags), `run_linter` (ruff — аналог диагностики LSP). Все пути проходят одну проверку: корень `AI_REPO_ROOT`, запрещённые имена `AI_DENY_GLOBS`.
3. Настройки инструментов в `ai/config.py` (`AI_DENY_GLOBS`, `AI_EXCLUDE_DIRS`, `AI_TOOL_TIMEOUT_S`) и `.env.example`.
4. `tests/` — обязательные тесты курса и пять ваших тестов-атак, без LLM и без CrewAI. В истории PR коммит с тестами идёт **раньше** кода.
5. `ai/run_agent.py` с тремя инструментами и две трассы: обычный вопрос и провокация «неверный вывод линтера».
6. `docs/adr/002-code-tools.md` — ADR: граница доступа, чья конфигурация ruff, чем код отличается от вашей v2.

**Помощник по-прежнему только читает бэкенд.** Ни один инструмент не пишет на диск, не запускает код и тесты бэкенда, не вызывает `git`. Провокацию с битой конфигурацией линтера вы сделаете на **копии** бэкенда во временном каталоге (шаг 4.3).

---

## Таймлайн

| Время | Блок | Что должно быть готово к концу блока |
|---|---|---|
| 00:00–00:05 | Блок 0. Слепые пятна | Преподаватель зачитал 2–3 ответа со стикеров воркшопа 2 |
| 00:05–00:20 | Блок 1. Код практики 1 в ветке, ruff и pytest | Роли названы, в `feature/code-tools` есть `ai/`, ruff и pytest закреплены в `requirements.txt` |
| 00:20–00:45 | Блок 2. Тесты до кода | Настройки в `ai/config.py`, `tests/` с обязательными и пятью своими тестами, красный запуск, коммит `test:` |
| 00:45–01:50 | Блок 3. Три инструмента | `ai/tools/code_tools.py`, все тесты зелёные, проверка на реальном бэкенде |
| 01:50–02:20 | Блок 4. Агент и неверный вывод линтера | `run-p2-01.log`, `run-p2-02.log`, бэкенд не изменён |
| 02:20–02:55 | Блок 5. PR, peer review, ADR | PR открыт, review в обе стороны, ADR 002 закоммичен |
| 02:55–03:00 | Итог | Ответ по чек-листу самопроверки |

Перерыв между парами — в 01:50, на границе блоков 3 и 4.

Тесты этого занятия не импортируют CrewAI: весь набор проходит за 10–60 секунд, из них каждый тест, который запускает ruff, — 1–4 секунды. Медленным остаётся только блок 4: импорт CrewAI (от 10 секунд до полутора минут) и ответы модели на CPU.

---

## Подготовка ДО занятия

Около 45 минут дома, из них 30 — чтение. Пункты 1–2 делает один участник на команду, остальные — у себя только проверки.

### 1. Хвосты прошлых занятий (один участник)

- PR практики 1 (`feature/agent-tool-1` → `main` помощника) готов к слиянию: замечания peer review закрыты (домашнее задание практики 1, п. 1). На паре вы его вольёте (шаг 1.2).
- В ветке `feature/code-tools` закоммичены спецификация v2 с `run_linter` (коды 0, 1, 2) и раздел «Тесты на практику 2» из пяти атак (домашнее задание воркшопа 2, п. 1).
- Каркас инструментов появился в репозитории курса к этой неделе. Обновите свой клон курса: `git -C <клон курса> pull` (если вы скачивали архив — скачайте его заново). Клона нет — сделайте его в родительском каталоге помощника: `git clone https://github.com/andrey-limasov/agent-dev` (подробнее — практика 1, «Подготовка», п. 0, абзац про учебный бэкенд); тогда `<клон курса>` из корня помощника — `../agent-dev`.

**Как понять, что получилось.** На странице PR практики 1 нет открытых обсуждений. `git log --oneline origin/feature/code-tools` показывает коммит с v2, а в `docs/tools-spec-cycle2.md` этой ветки есть раздел «Тесты на практику 2». `ls <клон курса>/templates/tool-lsp-example.py` (PowerShell: `Test-Path <клон курса>\templates\tool-lsp-example.py`) находит файл.

**Если не получилось.** Нет v2 или атак меньше пяти — на паре дополните их запасным списком из шага 2.3. Это не блокирует занятие. `pull` или `git clone` не проходит (`Could not resolve host`, таймаут) — скачайте архив репозитория курса (Code → Download ZIP на [странице репозитория](https://github.com/andrey-limasov/agent-dev)). Файла `tool-lsp-example.py` нет и после `pull` — напишите об этом в общий чат курса до занятия.

### 2. ruff и pytest в окружении помощника (каждый, 3 мин)

В корне помощника, с активированным окружением (как в практике 1):

```bash
pip install ruff==0.17.0 pytest==9.1.1
python -m ruff --version
python -m pytest --version
```

Окружение создано через `uv venv` без `--seed` — вместо `pip` везде пишите `uv pip` (`uv pip install ruff==0.17.0 pytest==9.1.1`), остальное так же. В таком окружении своего `pip` нет, и `pip install` из активированного окна поставит пакеты в системный Python, мимо помощника. Окружение из практики 1 (`uv venv --python 3.12 --seed`) засеяно `pip`: в нём годятся обе команды.

**Как понять, что получилось.** Напечатано `ruff 0.17.0` и `pytest 9.1.1`.

**Если не получилось.** `No module named ruff` или `No module named pytest` — пакет ушёл в другое окружение (чаще всего `pip` вместо `uv pip` в окружении uv без `--seed`): `python -c "import sys; print(sys.prefix)"` должен показать путь внутри `<проект>-assistant`.

### 3. Модель на месте (тот, у кого работал путь А)

`ollama ls` показывает `qwen3:4b-instruct` (или `qwen2.5:7b`), как в «Проверке окружения» практики 1. По пути Б — проверка ключа из «Подготовки» практики 1, путь Б, п. 3. Модель нужна одной машине на команду и только в блоке 4.

### 4. Прочитать (≈ 30 мин)

| Что читать | К какому шагу | Время |
|---|---|---|
| [pytest: Get Started](https://docs.pytest.org/en/stable/getting-started.html) — разделы до «Group multiple tests in a class» | 2.2 | 5 мин |
| [pytest: tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html) — раздел «The tmp_path fixture» | 2.2 | 5 мин |
| [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) — раздел «Scope: sharing fixtures across classes, modules, packages or session», абзац про `conftest.py` | 2.2 | 5 мин |
| [unittest.mock: patch](https://docs.python.org/3/library/unittest.mock.html#patch) — `patch` как контекстный менеджер и `side_effect`; ниже на той же странице — [`patch.dict`](https://docs.python.org/3/library/unittest.mock.html#patch-dict) | 3.3 | 10 мин |
| [Ruff: Config file discovery](https://docs.astral.sh/ruff/configuration/#config-file-discovery) — как ruff выбирает конфигурацию | 3.3 | 5 мин |

СРС к циклу 2 (`pathlib`, `subprocess`, коды ruff) — раздел «После воркшопа» в [`materials-2.md`](materials-2.md), если ещё не прочитан.

---

## Блок 0. Слепые пятна (00:00–00:05)

Преподаватель зачитывает 2–3 самых частых ответа со стикеров воркшопа 2 «Какую атаку я бы сам пропустил…». Driver в это время открывает терминал в корне помощника и активирует окружение.

> **Стоп-точка (00:05)** — преподаватель: зачитайте 2–3 самых частых ответа со стикеров воркшопа 2 и объявите начало блока 1.

---

## Блок 1. Код практики 1 в ветке, ruff и pytest (00:05–00:20)

### Шаг 1.1: Роли (2 мин)

**Driver** — клавиатура, проговаривает вслух, что делает. **Navigator** — держит открытой спецификацию v2 и этот файл, сверяет код с ними. Третий и четвёртый участник — **тестировщик-документатор**: в блоке 2 переводит атаки в тесты вместе с Navigator, в блоке 4 ведёт черновик ADR. Роли меняются по кругу на стоп-точках 00:45, 01:20 и 01:50. Запишите, кто в каком блоке в какой роли: это пойдёт в описание PR.

Команда из четырёх человек может работать двумя парами: одна — `read_file` и `search_codebase` (шаг 3.2), другая — `run_linter` и его тесты (шаг 3.3). Тесты из блока 2 и каркас попадают на вторую машину через `git push` / `git pull` (шаги 2.3 и 3.1), сведение кода — в конце блока 3.

**Как понять, что получилось.** Каждый называет свою роль на ближайшие 25 минут.

### Шаг 1.2: Код практики 1 — в `feature/code-tools` (8 мин)

**Зачем это нужно.** Ветка `feature/code-tools` отведена от `main` до слияния PR практики 1, поэтому в ней нет ни `ai/config.py`, ни первого Tool. Инструменты этого занятия используют оба.

**Что сделать**

1. Если PR практики 1 ещё не влит — влейте его в `main` в веб-интерфейсе хостинга (кнопка Merge на странице PR). Если `main` защищена и нужно одобрение — одобряет любой участник команды, который не автор PR.
2. В корне помощника:

```bash
git switch main
git pull
git ls-files ai/config.py
git switch feature/code-tools
git pull
git merge --no-edit main
git ls-files ai/config.py docs/tools-spec-cycle2.md
```

3. Проверьте, что первый Tool работает как в конце практики 1: `python -m ai.tools._check` (от 10 секунд до полутора минут из-за импорта CrewAI). `.env` при смене ветки не пропадает: он не отслеживается git.
4. `git push`. Вторая машина команды подключается так: `git fetch`, `git switch feature/code-tools`, `git pull`.

**Как понять, что получилось.** Первый `git ls-files` печатает `ai/config.py` (код практики 1 в `main`). `git merge` печатает `Merge made by the 'ort' strategy.` или `Fast-forward`. Последний `git ls-files` печатает обе строки: `ai/config.py` и `docs/tools-spec-cycle2.md`. `_check` печатает строки `ok` и `err` без traceback.

**Если не получилось**

- Первый `git ls-files` ничего не напечатал — PR практики 1 не влит. Влейте его (пункт 1) и повторите. Влить сейчас нельзя (нет прав, никто не может одобрить) — подтяните ветку практики 1 напрямую: `git merge --no-edit origin/feature/agent-tool-1` вместо `git merge --no-edit main`, а в описании PR практики 2 напишите, что в нём и код практики 1.
- В `main` помощника нет `ai/config.py`, потому что PR практики 1 не готов (нет кода Tool и конфигурации) — сделайте из практики 1 только шаг 1.3, пункты 1–2 (каталоги `ai/` и `.env`), и шаг 2.1 (`ai/config.py`), закоммитьте их в `feature/code-tools`. Фабрика LLM и первый Tool нужны только в блоке 4: доделайте их по практике 1 к нему или дома.
- `CONFLICT (content): Merge conflict in .gitignore` (или `README.md`) — обе ветки дописали этот файл. Откройте его, оставьте строки из обеих версий, удалите строки-маркеры `<<<<<<<`, `=======`, `>>>>>>>`, затем `git add .gitignore` и `git commit --no-edit`.
- `_check` падает с `ValidationError` про `ai_repo_root` — на этой машине нет `.env`: создайте его, как в шаге 1.3 практики 1.

### Шаг 1.3: ruff и pytest в `requirements.txt` (5 мин)

**Зачем это нужно.** `run_linter` вызывает ruff из окружения помощника, а тесты — это pytest. Версии закрепляем так же, как CrewAI в практике 1: помощник ставится одной командой, в том числе в CI на неделе 12.

**Что сделать.** Допишите две строки в `requirements.txt` и два каталога в `.gitignore` (кеши ruff и pytest в корне помощника коммитить не нужно).

Git Bash / Linux / macOS:

```bash
printf 'ruff==0.17.0\npytest==9.1.1\n' >> requirements.txt
printf '.ruff_cache/\n.pytest_cache/\n' >> .gitignore
pip install -r requirements.txt
pip check
git add requirements.txt .gitignore
git commit -m "chore: add ruff and pytest"
```

PowerShell:

```powershell
Add-Content requirements.txt "ruff==0.17.0", "pytest==9.1.1"
Add-Content .gitignore ".ruff_cache/", ".pytest_cache/"
pip install -r requirements.txt
pip check
git add requirements.txt .gitignore
git commit -m "chore: add ruff and pytest"
```

На uv: `uv pip install -r requirements.txt` и `uv pip check`.

Работаете двумя парами — сразу `git push`, а на второй машине `git pull`: иначе `requirements.txt` с ruff и pytest придёт туда только в шаге 2.3.

**Как понять, что получилось.** `requirements.txt` — четыре строки: `crewai`, `pydantic-settings`, `ruff`, `pytest`. `pip check` печатает `No broken requirements found.`, `uv pip check` — `All installed packages are compatible`. `python -m ruff --version` → `ruff 0.17.0`, `python -m pytest --version` → `pytest 9.1.1`.

**Если не получилось**

- Последняя строка прежнего `requirements.txt` слиплась с новой (`pydantic-settings==2.15.0ruff==0.17.0`) — в файле не было перевода строки в конце. Исправьте в редакторе: одна зависимость на строку.
- `ReadTimeoutError` — повторите `pip install`: пакеты небольшие, второй заход обычно проходит.

> **Стоп-точка (00:20)** — преподаватель: объявите блок 2 «тесты до кода». Отметьте команды, у которых `git ls-files ai/config.py` в ветке `feature/code-tools` ничего не печатает.

---

## Блок 2. Тесты до кода (00:20–00:45)

### Шаг 2.1: Настройки инструментов в `ai/config.py` (7 мин)

**Зачем это нужно.** Что запрещено читать и сколько ждать линтер — это конфигурация, а не константы в коде инструмента (воркшоп 2, «Связь с курсом»). Конфигурация у помощника одна — `AISettings`.

**Что сделать**

1. Допишите в класс `AISettings` (`ai/config.py`) после `ai_endpoint_files` три поля:

```python
    # инструменты для работы с кодом (практика 2)
    ai_deny_globs: str = ".env*,*.pem,*.key,.git,secrets"  # шаблоны имён через запятую
    ai_exclude_dirs: str = ".git,.venv,venv,node_modules,__pycache__,dist,build"  # не обходить при поиске
    ai_tool_timeout_s: int = 30  # потолок на ruff и на обход при поиске, секунды
```

   Имена полей не меняйте: их используют каркас и обязательные тесты. Значения — по вашей v2: если вы запретили больше, допишите шаблоны. Списки — строкой через запятую, как `ai_endpoint_files`. Голый `list[str]` не годится: `pydantic-settings` читает сложные типы из `.env` как JSON, и строка через запятую уронит конфигурацию при старте ([pydantic-settings](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/), раздел «Parsing environment variable values»).

   Шаблоны сверяются с **каждой частью** пути без учёта регистра: `secrets` закрывает `secrets/` на любой глубине, `.env*` — и `app/.env`, и `.env.example` бэкенда. Последнее сделано сознательно. Если решите иначе — запишите в ADR (шаг 5.3).

2. Допишите эти три переменные в `.env.example` (там перечислены все переменные `config.py`) — со значениями из вашего `config.py`: если расширили `ai_deny_globs` по v2, здесь тот же расширенный список:

```
AI_DENY_GLOBS=.env*,*.pem,*.key,.git,secrets
AI_EXCLUDE_DIRS=.git,.venv,venv,node_modules,__pycache__,dist,build
AI_TOOL_TIMEOUT_S=30
```

**Как понять, что получилось**

```bash
python -c "from ai.config import settings; print(settings.ai_deny_globs, settings.ai_tool_timeout_s)"
```

Напечатано `.env*,*.pem,*.key,.git,secrets 30` (или ваши значения).

**Если не получилось.** `Extra inputs are not permitted` — в `model_config` пропал `extra="ignore"` (шаг 2.1 практики 1). `Input should be a valid integer` — в `.env` у `AI_TOOL_TIMEOUT_S` не число.

### Шаг 2.2: `tests/conftest.py` и обязательные тесты (8 мин)

**Зачем это нужно.** Тесты гоняются на временном мини-репозитории, а не на `../<проект>`: в бэкенде недели 4 нет ни секретов, ни нарушений ruff, а в CI помощника клона бэкенда не будет вовсе. Обязательные тесты курса одинаковы у всех команд: граница корня, deny-list, коды ruff 0, 1, 2.

**Что сделать**

1. Создайте каталог `tests` (`mkdir tests` — одинаково в Git Bash и PowerShell) и в нём `tests/conftest.py`:

```python
import os
import tempfile

# До импорта ai.config: модульный settings = AISettings() требует AI_REPO_ROOT,
# а в CI и на свежем клоне .env нет. Внутри pytest модульный settings поэтому
# смотрит во временный каталог (переменная окружения важнее .env); тесты
# инструментов передают свой корень явно.
os.environ.setdefault("AI_REPO_ROOT", tempfile.gettempdir())

import pytest

from ai.config import AISettings


@pytest.fixture
def repo(tmp_path):
    """Мини-репозиторий бэкенда во временном каталоге: код, нарушение ruff, секреты."""
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text(
        "def health_check():\n"
        '    return {"status": "healthy"}\n'
        "\n"
        "\n"
        "class NoteIn:\n"
        '    title: str = ""\n',
        encoding="utf-8",
    )
    (tmp_path / "app" / "bad.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / ".env").write_text("API_KEY=secret-from-env\n", encoding="utf-8")
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "leak.py").write_text(
        "import os\nAPI_KEY = 'secret-from-secrets'\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def s(repo):
    """Настройки помощника с корнем в мини-репозитории; .env не читается."""
    return AISettings(ai_repo_root=repo, _env_file=None)
```

   Фикстура `s` — это настройки, которые инструменты получат явным аргументом. Каждый тест работает в своём новом каталоге `tmp_path`, поэтому тесты не мешают друг другу и ничего не оставляют в репозитории. Тест на первый Tool практики 1 сюда не добавляйте: его модуль импортирует CrewAI при загрузке, и `test_tests_do_not_import_crewai` упадёт.

2. Создайте `tests/test_invariants.py` — его не меняют под свою v2:

```python
"""Обязательные тесты курса: граница корня, deny-list, коды ruff 0/1/2, чья конфигурация ruff.

Не меняйте их под свою v2: они вызывают только check_path и run_linter.
"""

import json
import sys

import pytest

from ai.config import AISettings
from ai.tools.code_tools import check_path, run_linter


def test_tests_do_not_import_crewai():
    assert "crewai" not in sys.modules


def test_outside_root(s):
    _, err = check_path("../outside.txt", s)
    assert "вне репозитория" in json.loads(err)["message"]


def test_absolute_path(s, repo):
    _, err = check_path(str(repo / "app" / "main.py"), s)
    assert "вне репозитория" in json.loads(err)["message"]


@pytest.mark.parametrize(
    "path", [".env", "app/../.env", "secrets/leak.py", "SECRETS/leak.py", ".git/config"]
)
def test_deny_list(s, path):
    _, err = check_path(path, s)
    assert err is not None
    assert "запрещён" in json.loads(err)["message"]


def test_allowed_path(s, repo):
    target, err = check_path("app/main.py", s)
    assert err is None
    assert target == (repo / "app" / "main.py").resolve()


def test_ruff_exit_0_ok_without_findings(s):
    answer = json.loads(run_linter("app/main.py", s))
    assert answer["status"] == "ok"
    assert answer["total_findings"] == 0


def test_ruff_exit_1_ok_with_findings(s):
    answer = json.loads(run_linter("app/bad.py", s))
    assert answer["status"] == "ok"
    assert answer["total_findings"] >= 1
    assert answer["findings"][0]["path"] == "app/bad.py"
    assert answer["findings"][0]["rule"] == "F401"


def test_ruff_exit_2_is_error(s, repo):
    (repo / "ruff.toml").write_text('line-length = "long"\n', encoding="utf-8")
    answer = json.loads(run_linter("app/main.py", s))
    assert answer["status"] == "error"
    assert "аварийно" in answer["message"]


def test_linter_ignores_config_outside_backend(tmp_path):
    (tmp_path / "ruff.toml").write_text('[lint]\nignore = ["F401"]\n', encoding="utf-8")
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "bad.py").write_text("import os\n", encoding="utf-8")
    answer = json.loads(run_linter("bad.py", AISettings(ai_repo_root=backend, _env_file=None)))
    assert [f["rule"] for f in answer["findings"]] == ["F401"]


def test_linter_missing_path(s):
    answer = json.loads(run_linter("app/no_such.py", s))
    assert answer["status"] == "error"


def test_linter_skips_denied_and_writes_nothing(s, repo):
    answer = json.loads(run_linter(".", s))
    assert answer["status"] == "ok"
    assert all(not (f["path"] or "").startswith("secrets/") for f in answer["findings"])
    assert not (repo / ".ruff_cache").exists()
```

   `test_ruff_exit_2_is_error` кладёт битую конфигурацию ruff (`line-length` — строка вместо числа): ruff завершается с кодом 2, и инструмент обязан вернуть `error`, а не «замечаний нет». Это и есть «неверный вывод линтера» из темы занятия. `test_linter_ignores_config_outside_backend` кладёт конфигурацию ruff, отключающую `F401`, **выше** корня бэкенда: так выглядит чужая конфигурация в домашнем или общем каталоге. Она не должна применяться к бэкенду (шаг 3.3, п. 2).

**Как понять, что получилось.** Оба файла лежат в `tests/`. Запуск — в конце шага 2.3.

### Шаг 2.3: Пять своих тестов, красный запуск, коммит (10 мин)

**Зачем это нужно.** Коммит с тестами до кода фиксирует, что тесты написаны по спецификации, а не подогнаны под код: тест, написанный после, часто проверяет то, что код уже делает. Сейчас тесты упадут все разом, потому что модуля ещё нет. Настоящий красный — тесты, падающие на `assert`, — вы увидите на голом каркасе в шаге 3.1.

**Что сделать**

1. Создайте `tests/test_code_tools.py` и переведите в тесты пять строк раздела «Тесты на практику 2» из `docs/tools-spec-cycle2.md`. Строка `вызов → status → message` превращается в три строки теста. Внутренние функции получают настройки последним позиционным аргументом `s`:

```
read_file(path="app/../.env") → error → «запрещён»
```

```python
def test_r3_loop_to_env(s):
    answer = json.loads(read_file("app/../.env", s))
    assert answer["status"] == "error"
    assert "запрещён" in answer["message"]
```

   **Имена параметров и полей ответа.** Быстрее всего писать тесты на имена каркаса, который вы скопируете в шаге 3.1. Свои имена из v2 тоже можно, но тогда в шаге 3.1 вы переименуете их в каркасе вместе с обёртками для агента — это ещё 10–15 минут.

| Функция каркаса | Параметры после `s` | Поля успешного ответа |
|---|---|---|
| `read_file(path, s, …)` | `start_line=1`, `max_lines=200` | `path`, `start_line`, `end_line`, `total_lines`, `truncated`, `content` |
| `search_codebase(query, s, …)` | `kind="text"` или `"symbol"`, `path="."`, `path_glob="*.py"`, `max_results=20` | `total_matches`, `returned`, `truncated`, `timed_out`, `matches` — список `{"path", "line", "text"}` (у `kind="symbol"` вместо `"text"` — `"kind"`) |
| `run_linter(path, s, …)` | `max_findings=30` | `total_findings`, `returned`, `truncated`, `by_rule`, `findings` — список `{"path", "line", "rule", "message"}`. Поля общие для курса, их не переименовывают |

   Подстроку в `message` берите из текстов ошибок каркаса. Печатайте «ё», как в каркасе: подстроки «запрещен» в «запрещён» нет.

| Ситуация | Текст `message` в каркасе | Подстрока для теста |
|---|---|---|
| Путь вне корня, абсолютный, с диском | «путь вне репозитория» | `вне репозитория` |
| Путь под deny-list | «доступ к файлу запрещён политикой» | `запрещён` |
| Файла нет (`read_file`) | «файл не найден» | `не найден` |
| Файла или каталога нет (`search_codebase`, `run_linter`) | «файл или каталог не найден» | `не найден` |
| Не число в числовом параметре | «max_results должен быть целым числом от 1 до 50…» | `целым числом` |
| ruff упал (код 2 и выше) | «ruff завершился аварийно» | `аварийно` |
| ruff не установлен | «ruff не установлен в окружении агента» | `не установлен` |
| Таймаут ruff | «проверка не уложилась в N с» | `не уложилась` |

   Первые две строки — ответы `check_path`, общие для курса: на них опираются обязательные тесты. Для них подстрока **всегда** берётся из таблицы, даже если в v2 написано иначе («запрещен», «запрещённый путь»); расхождение запишите в ADR. Тексты `run_linter` тоже общие — подстрока из таблицы. Остальные тексты `read_file` и `search_codebase` можно оставить по v2: тогда в шаге 3.1 вы поправите текст в каркасе.

   **Если атаке нужны данные**, которых нет в мини-репозитории из `conftest.py` (сотни совпадений, бинарный файл), создайте файл в самом тесте через фикстуру `repo`, как в запасных R6 и S2. Проверка «в `matches` нет запрещённых файлов» при нуле совпадений проходит вхолостую: проверяйте и число совпадений, как S5 (`API_KEY` в мини-репозитории есть только в `.env` и `secrets/`, поэтому совпадений должно быть 0).

   Атаки, которые так не записываются:

| Атака | Как быть |
|---|---|
| G3 «не тот тип» (`max_results="десять"`) | Через агента такой вызов отклоняет CrewAI до вашего кода (шаг 2.4 практики 1, требование 4). Тест вызывает внутреннюю функцию напрямую и ждёт `error` |
| G2 «карусель» | Не задача инструмента: её останавливает `max_iter=5` у агента. Теста нет — запишите в ADR |
| G1 «инъекция в комментарии» | Инструмент не отличит инструкцию от данных. Тест на границу — `read_file(".env")` → `error`; остальное — в ADR |
| L1 «ruff не установлен», L5 «вечная проверка» | L1 — подмена `sys.modules` через `mock.patch.dict`, L5 — подмена `subprocess.run` через `mock.patch`; образцы — в шаге 3.3. Можно написать сейчас |

2. **Нет v2 или атак меньше пяти.** Нет v2 — возьмите запасной список целиком (R3, R6, S5, S2, L4: доступ, объём, сбой и тест на `run_linter`). Атак меньше пяти — свои оставьте и добавьте из запасного списка недостающие по порядку, пропуская те, что у вас уже есть. Так же — если спецификация ещё v1 и атак в ней меньше пяти. **Среди ваших тестов должна быть хотя бы одна атака на `run_linter`.** Нет такой (например, в v1 `run_linter` ещё не было) — первой добавьте L4, остальные недостающие — по порядку; своих уже пять — L4 станет шестым тестом. Своя атака, которая повторяет обязательный тест (`F401` → `ok`, битая конфигурация → `error`), не ошибка, но нового не проверяет: лучше L4 или другая граница `run_linter` из вашей v2. Запасной список написан на именах каркаса; свои атаки запишите на них же — тогда в шаге 3.1 переименовывать нечего. Числа `passed` и `failed` в шагах 3.1–3.3 даны для запасного списка целиком, у вас они будут свои.

```python
"""Тесты команды: пять атак из раздела «Тесты на практику 2»."""

import json

from ai.tools.code_tools import read_file, run_linter, search_codebase


def test_r3_loop_to_env(s):
    answer = json.loads(read_file("app/../.env", s))
    assert answer["status"] == "error"
    assert "запрещён" in answer["message"]


def test_r6_binary_file(s, repo):
    (repo / "app" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    answer = json.loads(read_file("app/logo.png", s))
    assert answer["status"] == "error"


def test_s5_search_does_not_read_secrets(s):
    answer = json.loads(search_codebase("API_KEY", s))
    assert answer["status"] == "ok"
    assert answer["total_matches"] == 0


def test_s2_too_general_query(s, repo):
    (repo / "app" / "many.py").write_text("x = 1  # import\n" * 600, encoding="utf-8")
    answer = json.loads(search_codebase("import", s))
    assert answer["status"] == "ok"
    assert answer["total_matches"] > 500
    assert answer["matches"] == []
    assert "hint" in answer


def test_l4_flag_as_path(s):
    answer = json.loads(run_linter("--fix", s))
    assert answer["status"] == "error"
```

   L4 в каркасе отбивают два рубежа: путь `--fix` не существует, и ruff не запускается вовсе; а если бы файл с таким именем был, его защитил бы `"--"` перед путём в команде ruff.

3. Запустите тесты из корня помощника — именно `python -m pytest`, а не `pytest`:

```bash
python -m pytest -q
```

   Сохраните последние строки вывода: они пойдут в описание PR как доказательство «красное до кода».

4. Закоммитьте тесты и настройки **отдельным коммитом до кода**:

```bash
git add ai/config.py .env.example tests/
git commit -m "test: add code tools tests before implementation"
git push
```

   Если работаете двумя парами, вторая машина делает `git pull`: тесты и поля `AISettings` нужны обеим.

**Как понять, что получилось.** Тесты красные, потому что модуля с кодом ещё нет:

```
E   ModuleNotFoundError: No module named 'ai.tools.code_tools'
=========================== short test summary info ===========================
ERROR tests/test_code_tools.py
ERROR tests/test_invariants.py
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!
```

Других ошибок, кроме `No module named 'ai.tools.code_tools'`, нет. `git log --oneline -1` показывает коммит `test: …`.

**Если не получилось**

- `ModuleNotFoundError: No module named 'ai'` — запущен `pytest`, а не `python -m pytest`, или запуск не из корня помощника.
- `ModuleNotFoundError: No module named 'ai.config'` или `ValidationError` при сборе — ветка без кода практики 1 (шаг 1.2) или нет `conftest.py` в `tests/`.
- `SyntaxError` в тесте — исправьте опечатку сейчас: после появления кода такую ошибку легко принять за ошибку инструмента.

> **Стоп-точка (00:45)** — преподаватель: объявите смену ролей и начало блока 3. Отметьте команды, у которых нет коммита `test:`.

---

## Блок 3. Три инструмента (00:45–01:50)

### Шаг 3.1: Каркас и общая проверка пути (10 мин)

**Зачем это нужно.** Проверка пути и запуск линтера — места, где одна ошибка открывает `.env` или пишет в бэкенд. В каркасе они уже готовы и проверены. Ваша работа — краевые случаи и лимиты из вашей v2.

**Что сделать**

1. Скопируйте каркас [`templates/tool-lsp-example.py`](../templates/tool-lsp-example.py) из клона репозитория курса под именем модуля с подчёркиваниями (модуль с дефисом в имени не импортируется):

```bash
cp <клон курса>/templates/tool-lsp-example.py ai/tools/code_tools.py
```

   PowerShell: `Copy-Item <клон курса>\templates\tool-lsp-example.py ai\tools\code_tools.py`.

   **Двумя парами** каркас копирует одна машина и сразу публикует его, вторая делает `git pull`:

```bash
git add ai/tools/code_tools.py
git commit -m "feat: add code tools skeleton"
git push
```

2. Прочитайте в паре функции `check_path` и `iter_files`. Navigator сверяет их с разделом «доступ» вашей v2: четыре шага проверки, порядок которых важен. Нормализация пути (`resolve()`) идёт до deny-list: иначе пройдут ссылка или junction на `secrets/` под другим именем (`app/link/leak.py`) и короткое имя Windows `ENV~1` вместо `.env`.
3. **Только если в своих тестах имена из v2, а не каркасные** (шаг 2.3), приведите к ним `read_file` и `search_codebase`:
   - имена параметров (`count` вместо `max_lines`, `limit` вместо `max_results`) — в самой функции **и** в обёртке в `crewai_tools()` в конце файла: сигнатура, строка в `Args` docstring и вызов внутренней функции (`max_lines=max_lines`). Иначе тесты зелёные, а в блоке 4 агент получит `TypeError … unexpected keyword argument`;
   - имена полей ответа (`count` вместо `total_matches`, `file` вместо `path`) и тексты `message`, кроме ответов `check_path`, — в `_ok(...)` и `_fail(...)` этих двух функций.

   Не укладываетесь — вместо этого поменяйте имена в своих тестах на каркасные: проверяемое поведение от этого не меняется, а расхождение с v2 запишите в ADR. У `check_path` и `run_linter` сигнатуры, поля ответа и тексты ошибок общие для курса. Третий параметр `run_linter` можно назвать по v2 (`limit` вместо `max_findings`) — тоже вместе с обёрткой.
4. Запустите все тесты на голом каркасе:

```bash
python -m pytest -q
```

**Как понять, что получилось.** Все тесты `tests/test_invariants.py` зелёные (отдельно: `python -m pytest -q tests/test_invariants.py` → `15 passed`). Ваши тесты, которые упали на `assert`, — список работы на шаг 3.2. На запасном списке вывод заканчивается так:

```
FAILED tests/test_code_tools.py::test_r6_binary_file - AssertionError: assert...
FAILED tests/test_code_tools.py::test_s2_too_general_query - AssertionError: ...
2 failed, 18 passed in 2.48s
```

**Все ваши тесты зелёные уже на голом каркасе** (в выводе нет `failed`) — каркас отбивает ваши атаки, и в шаге 3.2 доводить нечего. Тогда Navigator за 5 минут находит в v2 одно-два правила, которые каркас делает иначе или не делает вовсе: частые случаи — в таблице ниже, остальные — в комментариях `TODO по вашей v2` каркаса. На каждое правило напишите тест в `tests/test_code_tools.py` (на именах каркаса) и запустите `python -m pytest -q`: новый тест должен упасть на `assert`. Тест сразу зелёный — каркас это правило уже выполняет, возьмите другое. Красные тесты — работа на шаг 3.2. Берите только правила, которые есть в вашей v2.

| Правило v2 (пример) | Что делает каркас | Где довести в шаге 3.2 |
|---|---|---|
| Число вне диапазона (`limit=100` при потолке 50) → `error` | `_as_int` прижимает число к границе, ответ `ok` | `_as_int`: вместо прижатия — `_fail(...)` с текстом «… должен быть целым числом от … до …». Функция общая для всех чисел, в том числе `max_findings` у `run_linter` |
| По умолчанию 100 строк, а не 200 | `max_lines=200` | Значение по умолчанию в `read_file`, в её вызове `_as_int` и в обёртке `read_file_tool` в `crewai_tools()` |
| Путь, начинающийся с `-`, отклоняется | Такой файл читается | Проверка в начале `read_file`, до `check_path` (`check_path` общий для курса) |
| Поле `skipped` — сколько файлов не разобрал `ast` | Поля нет | `TODO` в `search_codebase`: счётчик в `except (SyntaxError, ValueError)` и `skipped=` в `_ok(...)` |

```python
def test_v2_limit_out_of_range(s):
    answer = json.loads(search_codebase("health_check", s, max_results=100))
    assert answer["status"] == "error"
    assert "целым числом" in answer["message"]


def test_v2_default_100_lines(s, repo):
    (repo / "app" / "long.py").write_text("x = 1\n" * 150, encoding="utf-8")
    answer = json.loads(read_file("app/long.py", s))
    assert answer["end_line"] == 100


def test_v2_path_starting_with_dash(s, repo):
    (repo / "-x.py").write_text("x = 1\n", encoding="utf-8")
    answer = json.loads(read_file("-x.py", s))
    assert answer["status"] == "error"


def test_v2_skipped_counts_broken_files(s, repo):
    (repo / "app" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    answer = json.loads(search_codebase("health_check", s, kind="symbol"))
    assert answer.get("skipped") == 1
```

Не довели такой тест к 01:50 — пометьте его `xfail`, как в «Не успеваете?» в конце блока 3, а расхождение запишите в ADR (доделка — домашнее задание, п. 2).

**Если не получилось**

- Нет файла `<клон курса>/templates/tool-lsp-example.py` — клон курса не обновлён: `git -C <клон курса> pull` («Подготовка», п. 1). Не помогло — откройте файл [`templates/tool-lsp-example.py`](https://github.com/andrey-limasov/agent-dev/blob/main/templates/tool-lsp-example.py) на странице репозитория курса, кнопкой Download raw file сохраните его как `ai/tools/code_tools.py`. Не открывается и она — попросите преподавателя выложить файл в общий чат.
- Свой тест падает с `TypeError … unexpected keyword argument`, `KeyError` или на `assert` по имени поля или тексту ошибки — в тесте имена из v2, а каркас к ним не приведён (пункт 3), или подстрока в тесте не совпадает с текстом каркаса (таблица в шаге 2.3).
- `test_tests_do_not_import_crewai` упал — в `code_tools.py` или в тестах появился импорт CrewAI на уровне модуля. В каркасе CrewAI импортируется только внутри `crewai_tools()` (шаг 4.1).
- Тесты `run_linter` падают, а в ответе `ruff не установлен в окружении агента` — ruff не в этом окружении: шаг 1.3.
- `ImportError: cannot import name 'AISettings'` — в вашем `ai/config.py` класс называется иначе. Имя `AISettings` — общее для курса (практика 1, шаг 1.3): верните его.

### Шаг 3.2: `read_file` и `search_codebase` по вашей v2 (25 мин)

**Зачем это нужно.** Здесь спецификация становится кодом: каждое ограничение из v2 — проверка в коде, а не просьба в docstring.

**Что сделать.** Допишите места с пометкой `TODO по вашей v2`. Что уже есть в каркасе:

- `read_file(path, s, start_line=1, max_lines=200)` — проверка пути, «не найден», «каталог», потолок 400 строк, `total_lines` и `truncated`.
- `search_codebase(query, s, kind="text", path=".", path_glob="*.py", max_results=20)` — подстрока от 3 до 100 символов; `kind="symbol"` — определения `def`/`class` через `ast` (как `find_endpoint` практики 1); `path_glob` — только шаблон имени файла; потолок 50; обход не заходит в исключённые каталоги, каталоги под deny-list, символические ссылки и junction; при нуле совпадений — `hint`, что делать дальше (без него модель уверенно отвечает «такого нет», угадав не тот файл в `path_glob`).
- Числа от модели проверяет `_as_int`: не число — `error`, вне диапазона — прижимается к границе.

Чего нет и что берётся из вашей v2 (подробности — в комментариях `TODO` каркаса): бинарный файл, BOM и кодировка не UTF-8 у `read_file`, `start_line` за концом файла, обрезка длинных строк, потолок размера файла; «слишком общий запрос» (больше 500 совпадений) и счётчик пропущенных файлов у поиска. **На паре обязательны только случаи, на которые есть ваши тесты**; остальные `TODO` — домашнее задание, п. 2. После каждого дописанного случая запускайте тесты:

```bash
python -m pytest -q
```

**Как понять, что получилось.** Ваши тесты из `tests/test_code_tools.py` проходят. На запасном списке — `20 passed` (15 обязательных и 5 своих). Ни одного `failed`.

**Если не получилось**

- Тест на `kind="symbol"` не находит класс — в мини-репозитории `NoteIn` объявлен в `app/main.py` на строке 5; совпадение имени — точное, с учётом регистра.
- Тест S2 падает на `matches == []` — проверка «больше 500» стоит после цикла, а `matches` уже заполнен: при `total > 500` верните `_ok(...)` с `matches=[]` и `hint`. Тест R6 падает — нулевой байт ищите в байтах (`target.read_bytes()[:8192]`), а не в тексте после `read_text`.
- Тест упал с traceback из вашего кода, а не на `assert` — в функции осталось исключение наружу. Любой сбой — `return _fail("…")`, как в практике 1.

**Документация.** [`ast`](https://docs.python.org/3/library/ast.html) — `ast.parse`, `ast.walk`, узлы `FunctionDef` и `ClassDef`, если меняете поиск символов.

> **Стоп-точка (01:20)** — преподаватель: объявите смену ролей и попросите каждую команду запустить `python -m pytest -q tests/test_code_tools.py`. Команды, у которых в последней строке число перед `failed` больше числа перед `passed` (или `passed` нет вовсе), — путь «Не успеваете?» в конце блока 3.

### Шаг 3.3: `run_linter` и тесты со сбоем ruff (15 мин)

**Зачем это нужно.** Тема недели — агент не «падает» при неверном выводе линтера. Код возврата ruff 1 — это «нашлись замечания», а не ошибка; код 2 — «проверка не выполнена». Перепутаете — агент скажет «всё чисто», когда ruff упал.

**Что сделать**

1. Прочитайте `run_linter` в паре. Это тот же JSON ruff, что в `docs/lint-report.json` из домашнего задания практики 1 (п. 4), но сам файл инструмент не читает: он запускает ruff сейчас. Navigator сверяет код с `run_linter` из вашей v2 по таблице:

| Ситуация | Что возвращает инструмент |
|---|---|
| Путь не прошёл проверку или не существует | `error`, ruff не запускается (для несуществующего пути ruff сам вернул бы код 1 и «замечание» E902) |
| Код 0 | `ok`, `total_findings: 0` |
| Код 1 | `ok`, замечания: только `path` (относительный), `line`, `rule`, `message`; сначала синтаксические ошибки, потом правила `F`; файлы под deny-list отфильтрованы |
| Код 2 и выше | `error` «ruff завершился аварийно», хвост stderr, подсказка «результат неизвестен» |
| Пакета `ruff` нет в окружении помощника | `error` «ruff не установлен в окружении агента», ruff не запускается |
| Таймаут `AI_TOOL_TIMEOUT_S` | `error` «проверка не уложилась…», процесс ruff завершён |

   Вызов фиксированный: `[<ruff из окружения помощника>, "check", "--output-format=json", "--no-fix", "--no-cache", …, "--", <путь>]`, `shell=False`, `cwd` — корень бэкенда. Путь к ruff даёт `find_ruff_bin()` из пакета `ruff` (функция `_ruff_bin`), а не `python -m ruff`: на Windows `python -m ruff` запускает `ruff.exe` вторым процессом, и по таймауту останавливается только обёртка, а проверка идёт дальше. `--no-cache` не даёт ruff записать `.ruff_cache/` в бэкенд, `"--"` не даёт прочитать путь `--fix` как флаг. Подробнее о кодах — [Ruff: Exit codes](https://docs.astral.sh/ruff/linter/#exit-codes), 3 минуты.

2. **Чья конфигурация ruff.** Если у бэкенда есть своя (`ruff.toml`, `.ruff.toml` или `[tool.ruff]` в `pyproject.toml` у проверяемого пути или выше, до корня бэкенда), используется она. Если её нет — `--isolated`: правила ruff по умолчанию, без конфигураций выше корня бэкенда и без пользовательской. Конфигурация ruff самого помощника к бэкенду не применяется: своих правил помощник бэкенду не навязывает. Это делает `_ruff_config_args`, а проверяет `test_linter_ignores_config_outside_backend`. Вложенная конфигурация (`app/ruff.toml`) при проверке `.` не учитывается — у бэкендов недели 4 её нет. Если в CI бэкенда другой линтер (например, flake8), замечания помощника и CI могут различаться — запишите выбор в ADR.

3. Добавьте в `tests/test_code_tools.py` тесты на L1 и L5 (если их нет среди ваших пяти — как шестой и седьмой). Настоящий ruff удалять и ждать таймаут не нужно. `mock.patch.dict` на время блока `with` делает пакет `ruff` неимпортируемым (значение `None` в `sys.modules` — это `ModuleNotFoundError` при импорте, см. [The module cache](https://docs.python.org/3/reference/import.html#the-module-cache), 2 минуты), а `mock.patch` подменяет `subprocess.run` внутри модуля:

```python
import subprocess
from unittest import mock


def test_l1_ruff_not_installed(s):
    with mock.patch.dict("sys.modules", {"ruff": None}):
        answer = json.loads(run_linter("app/main.py", s))
    assert answer["status"] == "error"
    assert "не установлен" in answer["message"]


def test_l5_timeout(s):
    with mock.patch(
        "ai.tools.code_tools.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="ruff", timeout=30),
    ):
        answer = json.loads(run_linter(".", s))
    assert answer["status"] == "error"
    assert "не уложилась" in answer["message"]
```

   Импорты `subprocess` и `mock` перенесите в начало файла, к остальным. Оба теста вызывают `run_linter`: если его нет в строке `from ai.tools.code_tools import …`, допишите (`from ai.tools.code_tools import read_file, run_linter, search_codebase`). Моки LLM — тема цикла 6; здесь подменяется только запуск внешней программы.

**Как понять, что получилось.** `python -m pytest -q` → все тесты зелёные; на запасном списке с L1 и L5 — `22 passed`. Двумя парами до сведения кода у пары `run_linter` красными остаются тесты, которые доводит другая пара (на запасном списке — `2 failed, 20 passed`: R6 и S2). Это ожидаемо: не чините их, исправления придут при сведении.

**Если не получилось**

- `NameError: name 'run_linter' is not defined` в `test_l1_…` и `test_l5_…` — `run_linter` не импортирован в `tests/test_code_tools.py`: допишите его в строку `from ai.tools.code_tools import …` (п. 3).

- Тест с моком не подменил вызов, и пошёл настоящий ruff — в `patch` указан путь не к тому модулю. Подменяется имя там, где его ищет код: `ai.tools.code_tools.subprocess.run`.
- `test_l1_ruff_not_installed` получил `ok` — в вашем `code_tools.py` пакет `ruff` импортируется в начале модуля, а не внутри `_ruff_bin()`: тогда подмена `sys.modules` опаздывает. Верните импорт внутрь функции, как в каркасе.

### Шаг 3.4: Проверка на реальном бэкенде (10 мин)

**Зачем это нужно.** «Интеграция с файловой структурой бэкенда»: инструменты должны работать на настоящем `AI_REPO_ROOT` и ничего в нём не менять.

**Что сделать.** Из корня помощника, с `.env` из практики 1:

```bash
python -c "from ai.config import settings; from ai.tools.code_tools import run_linter, read_file, search_codebase; print(run_linter('.', settings)); print(read_file('.env', settings)); print(search_codebase('health_check', settings, kind='symbol'))"
git -C ../<проект> status --short
ls -a ../<проект>
```

PowerShell: вместо `ls -a` — `Get-ChildItem -Force ../<проект>`. `git status` каталог `.ruff_cache` не показывает никогда: внутри него лежит свой `.gitignore`. Поэтому нужны обе команды. На учебном бэкенде — только `ls -a ../sample-backend` (PowerShell: `Get-ChildItem -Force ../sample-backend`): копия не git-репозиторий.

**Как понять, что получилось.** Ожидаемо на учебном бэкенде (на своём — свои строки):

```
{"status": "ok", "path": ".", "total_findings": 0, "returned": 0, "truncated": false, "by_rule": {}, "findings": []}
{"status": "error", "message": "доступ к файлу запрещён политикой"}
{"status": "ok", "query": "health_check", "kind": "symbol", "total_matches": 1, "returned": 1, "truncated": false, "timed_out": false, "matches": [{"path": "main.py", "line": 23, "kind": "def"}]}
```

`total_findings: 0` — норма: в небольшом бэкенде недели 4 замечаний ruff нет. `read_file(".env")` возвращает `error`, даже если файла `.env` в бэкенде нет: запрет проверяется раньше существования. `git status --short` ничего не печатает, в списке `ls -a` нет `.ruff_cache`.

**Если не получилось**

- `git status` бэкенда показывает изменения, которые сделали не вы, — сначала проверьте, не правил ли кто-то бэкенд руками сегодня (это может быть работа по «Конфигурированию»: не откатывайте её).
- В `ls -a` бэкенда есть `.ruff_cache` — ruff запускали без `--no-cache` (например, вручную); инструменты на диск не пишут. Удалите именно этот каталог: `rm -rf ../<проект>/.ruff_cache` (PowerShell: `Remove-Item -Recurse -Force ../<проект>/.ruff_cache`). Остальное в бэкенде не трогайте.
- `run_linter` вернул `error` «ruff завершился аварийно» на своём бэкенде — у бэкенда битая конфигурация ruff. Помощник её не чинит: сообщите команде бэкенда, это задача PR людей.

### Сведение кода двух пар (5 мин)

Если работали одной парой — используйте эти минуты на краевые случаи v2. Двумя парами — как в конце шага 2.4 практики 1: пара, закончившая первой, `git add ai/tools/ tests/`, `git commit -m "feat: add read_file and search_codebase"` (или `"feat: add run_linter tests"` — по своей части), `git push`; вторая — так же `git add` и коммит со своим сообщением, затем `git pull --rebase`, `git push`. При конфликте в `ai/tools/code_tools.py` или `tests/test_code_tools.py` правки двух пар обычно в разных функциях: оставьте обе, удалите маркеры конфликта, `git add`, `git rebase --continue`. Затем на машине с моделью — `git pull` и `python -m pytest -q`: все тесты зелёные.

Если работали одной парой, закоммитьте код сейчас:

```bash
git add ai/tools/code_tools.py tests/
git commit -m "feat: add read_file, search_codebase and run_linter tools"
```

> **Закончили раньше?** По убыванию ценности: (1) `kind="symbol"` для методов классов — в ответ добавить имя класса; (2) у поиска — `skipped` (файлы с `SyntaxError`) и строка совпадения вокруг найденного фрагмента, а не от начала строки; (3) тест на junction или символическую ссылку наружу в `tmp_path` (на Windows — `mklink /J` в `cmd`), который проверяет, что поиск в неё не заходит.

### Не успеваете?

Минимум к 01:50: `check_path` и `run_linter` из каркаса, `read_file`, `python -m pytest -q tests/test_invariants.py` → `15 passed`. Признак перехода — к 01:20 в выводе `python -m pytest -q tests/test_code_tools.py` число перед `failed` больше числа перед `passed`. Тогда используйте каркас целиком, без доработок по v2: свои тесты, которые он не проходит, пометьте декоратором `@pytest.mark.xfail(reason="…")` (добавьте `import pytest` в начало файла; pytest покажет их как `xfailed`, а не `failed`) и разберите расхождение каркаса и v2 в ADR. Блок 4 делайте обязательно: трасса с ошибкой линтера — ядро занятия.

> **Стоп-точка (01:50)** — преподаватель: перерыв, если он есть; затем объявите блок 4. Отметьте команды, у которых `tests/test_invariants.py` не зелёный.

---

## Блок 4. Агент и неверный вывод линтера (01:50–02:20)

### Шаг 4.1: Три инструмента в `ai/run_agent.py` (10 мин)

**Зачем это нужно.** Тесты проверили инструменты без модели. Теперь проверяем, что модель их вызывает и что ошибку линтера агент передаёт пользователю, а не превращает в «всё чисто».

**Что сделать.** Правьте `ai/run_agent.py` из практики 1 (на машине с моделью):

1. Добавьте импорты `import sys` и `from ai.tools.code_tools import crewai_tools`.
2. Инструменты агента: `tools=[<первый_инструмент>, *crewai_tools()]` — первый Tool практики 1 остаётся, `max_iter=5` не меняется. `crewai_tools()` создаёт обёртки `@tool` вокруг внутренних функций и читает настройки из `.env`.
3. Агент из практики 1 отвечал только про эндпоинты, и его `goal` говорит об этом же. С таким `goal` модель вызывает первый Tool, а код функции придумывает, не открыв файл. Замените `goal` и допишите в конец `backstory` две фразы (то, что в `backstory` сказано про первый Tool, оставьте):

```python
    goal="Отвечать на вопросы о коде бэкенда, опираясь только на ответы инструментов",
    backstory=(
        "<ваш текст из практики 1> "
        "Где определена функция или класс, ищешь через search_codebase с kind='symbol' "
        "по всему репозиторию, а код показываешь через read_file. "
        "Если инструмент вернул ошибку с hint, выполняешь hint; если ошибка осталась, "
        "говоришь о ней пользователю и не придумываешь результат."
    ),
```
4. `Task`: вопрос берётся из командной строки, если он передан, иначе — основной сценарий; `expected_output` — нейтральный:

```python
QUESTION = "Где в бэкенде определена функция health_check и что она возвращает? Покажи её код."

task = Task(
    description=sys.argv[1] if len(sys.argv) > 1 else QUESTION,
    expected_output="Короткий ответ на вопрос пользователя; если инструмент вернул ошибку — перескажи её",
    agent=agent,
)
```

   Если в вашем бэкенде функции `health_check` нет, подставьте имя функции, которая есть.

**Как понять, что получилось.** `python -c "from ai.run_agent import agent; print([t.name for t in agent.tools])"` печатает имя вашего первого Tool и `read_file`, `search_codebase`, `run_linter` (импорт CrewAI — до полутора минут).

**Если не получилось.** `ValueError: Function must have a docstring` — у обёртки удалили docstring: в `crewai_tools()` он обязателен, это описание для модели.

### Шаг 4.2: Запуск 1 — обычный вопрос (8 мин)

Как в шаге 3.1 практики 1.

Git Bash:

```bash
export PYTHONUTF8=1
python -m ai.run_agent 2>&1 | tee ai/traces/run-p2-01.log
```

PowerShell:

```powershell
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
python -m ai.run_agent 2>&1 | Tee-Object -FilePath ai\traces\run-p2-01.log
(Get-Content ai\traces\run-p2-01.log) | Set-Content -Encoding utf8 ai\traces\run-p2-01.log
```

Последняя строка нужна в Windows PowerShell 5.1: его `Tee-Object` пишет лог в UTF-16, хостинг покажет такой файл в PR как двоичный, и рецензент не найдёт в нём ни строчки. Строка перекодирует лог в UTF-8; в PowerShell 7 она не нужна, но и не мешает.

**Как понять, что получилось.** В логе есть панель `Tool Execution Started` с одним из инструментов `search_codebase` или `read_file` и `Agent Final Answer`, где назван файл из `Output` инструмента, а также строка или код функции. Траектории бывают разные: `search_codebase` с `kind="symbol"`, затем `read_file` с `start_line`, или сразу `read_file("main.py")`. В проверочных запусках с `goal` и `backstory` из шага 4.1 на бэкенде недели 4 (`qwen2.5:7b` — 3 из 3, `qwen3:4b-instruct` — 1 из 1): `search_codebase` с `'kind': 'symbol'` (и `'path': '.'` или без `path`) → `read_file` с `'path': 'main.py', 'start_line': 19` → ответ «определена в файле `main.py`… возвращает `{"status": "healthy"}`» — с кодом функции или с номером строки. Первый запуск после загрузки модели — до 10 минут, следующие — 3–4 минуты. Ответ модели проверяется по смыслу, не по точному тексту. Если результат кажется случайным, повторите **один** раз (лог — `run-p2-01-2.log`); остальные повторы — дома.

**Если не получилось**

- Панелей `Tool Execution` нет, ответ придуман — разбор в шаге 3.2 практики 1: описание инструмента, конкретность вопроса, размер модели.
- Вызван только первый Tool практики 1 (`list_endpoints`, `find_endpoint`), а код в ответе придуман — `goal` агента остался «про эндпоинты»: пункт 3 шага 4.1.
- Агент ответил «функция не найдена» или пересказал ошибку, а в `Args` у `search_codebase` угаданы `path` (`api/v1`, `src`) или `path_glob` (`app.py`) — модель сузила поиск. Посмотрите, был ли в `Output` `hint` («повтори … с path='.'») и вызвала ли модель поиск повторно. Если нет — проверьте, что в `backstory` есть фраза про `hint` (шаг 4.1, пункт 3), и повторите запуск один раз. Повторилось — это находка для ADR («Наблюдения из трассы»).
- Модель передаёт `path` с абсолютным путём или `..` и получает `путь вне репозитория`, потом исправляется — так и должно быть: граница сработала. Запишите в ADR.

### Шаг 4.3: Запуск 2 — провокация «неверный вывод линтера» (12 мин)

**Зачем это нужно.** Ruff с битой конфигурацией завершается с кодом 2. Инструмент возвращает `error`; вопрос — что скажет агент пользователю. Бэкенд при этом трогать нельзя, поэтому битая конфигурация кладётся в **копию** бэкенда, а `AI_REPO_ROOT` переопределяется только на один запуск (переменная окружения важнее строки в `.env`, а `.env` не меняется).

**Что сделать.** Из корня помощника.

Git Bash (свой бэкенд — `git clone` копирует только закоммиченные файлы, без окружения бэкенда):

```bash
rm -rf ../p2-lint-copy
git clone -q ../<проект> ../p2-lint-copy
printf 'line-length = "long"\n' > ../p2-lint-copy/ruff.toml
AI_REPO_ROOT=../p2-lint-copy python -m ai.run_agent "Проверь линтером весь репозиторий бэкенда и скажи, есть ли в нём замечания." 2>&1 | tee ai/traces/run-p2-02.log
rm -rf ../p2-lint-copy
git -C ../<проект> status --short
```

PowerShell (в окне, где заданы `PYTHONUTF8` и кодировка из шага 4.2):

```powershell
Remove-Item -Recurse -Force ../p2-lint-copy -ErrorAction SilentlyContinue
git clone -q ../<проект> ../p2-lint-copy
Set-Content -Encoding ascii ../p2-lint-copy/ruff.toml 'line-length = "long"'
$env:AI_REPO_ROOT = "../p2-lint-copy"
python -m ai.run_agent "Проверь линтером весь репозиторий бэкенда и скажи, есть ли в нём замечания." 2>&1 | Tee-Object -FilePath ai\traces\run-p2-02.log
Remove-Item Env:AI_REPO_ROOT
Remove-Item -Recurse -Force ../p2-lint-copy
git -C ../<проект> status --short
(Get-Content ai\traces\run-p2-02.log) | Set-Content -Encoding utf8 ai\traces\run-p2-02.log
```

Последняя строка перекодирует лог в UTF-8, как в шаге 4.2.

На учебном бэкенде вместо `git clone -q ../<проект> ../p2-lint-copy` — `cp -r ../sample-backend ../p2-lint-copy` (PowerShell: `Copy-Item -Recurse ../sample-backend ../p2-lint-copy`), а вместо `git -C … status` — `ls -a ../sample-backend`: в нём по-прежнему нет `ruff.toml`.

**Как понять, что получилось**

- В `run-p2-02.log` есть панель `Tool Execution Started` с `run_linter` и `Tool Execution Completed` с `"status": "error"`, `"ruff завершился аварийно"` и словами `Failed to parse` в `stderr`. Ищите именно их: фраза `TOML parse error` в панели переносится на две строки, и поиск её не находит.
- Слова `Traceback` в логе нет, есть `Agent Final Answer`.
- Финальный ответ говорит, что проверку выполнить не удалось (в проверочном запуске `qwen3:4b-instruct`: «ruff завершился аварийно из-за ошибки парсинга конфигурационного файла… Проверка не выполнена, поэтому результат неизвестен»). Если агент ответил «замечаний нет» — это находка, а не провал вашего кода: инструмент вернул `error`, а агент его исказил. Запишите в ADR, «Наблюдения из трассы», что именно ответила модель (это инцидент «ложное зелёное» с воркшопа 2).
- `git status --short` бэкенда пуст, каталога `../p2-lint-copy` больше нет.

**Если не получилось**

- В логе `run_linter` вернул `ok` — агент вызвал его до того, как переменная `AI_REPO_ROOT` применилась (запуск не в той же строке или окне), или `ruff.toml` лёг не в копию. Проверьте `cat ../p2-lint-copy/ruff.toml` и повторите.
- `fatal: repository '../<проект>' does not exist` — опечатка в имени каталога бэкенда; на учебном бэкенде используйте `cp -r`.
- Агент не вызвал `run_linter` и ответил сам — сделайте вопрос конкретнее: `"Запусти run_linter для всего репозитория и перескажи результат."` (без кавычек внутри вопроса: в командной строке они обрывают аргумент).
- После этого шага в PowerShell любая команда `python -m …` падает с `ValidationError` … `p2-lint-copy` … `Path does not point to a directory` — запуск прервали `Ctrl+C`, и в окне осталась переменная: `Remove-Item Env:AI_REPO_ROOT` или откройте новое окно.

Перед коммитом проверьте, что в `run_agent.py` основной сценарий — `QUESTION`, а провокация осталась в логе.

> **Стоп-точка (02:20)** — преподаватель: объявите блок 5 и назовите пары команд для peer review.

---

## Блок 5. PR, peer review, ADR (02:20–02:55)

### Шаг 5.1: Коммит и Pull Request (10 мин)

**Что сделать**

1. `git status --short`: в списке `ai/run_agent.py` и логи `ai/traces/run-p2-0*.log`; `.env` нет.
2. Закоммитьте и опубликуйте:

```bash
git add ai/ .env.example
git commit -m "feat: connect code tools to agent"
git push
```

3. Откройте Pull Request `feature/code-tools` → `main` помощника. В описании:
   - что делают три инструмента и где их настройки;
   - вывод `python -m pytest -q` до кода (красный, из шага 2.3) и сейчас (последняя строка с `passed`);
   - что ответил агент на провокацию (шаг 4.3);
   - роли в блоках 2–4.
4. Ссылку на PR — в общий чат курса.

**Как понять, что получилось.** Во вкладке Files changed есть `requirements.txt`, `ai/config.py`, `.env.example`, `ai/tools/code_tools.py`, `tests/conftest.py`, `tests/test_invariants.py`, `tests/test_code_tools.py`, `ai/run_agent.py`, оба лога. Во вкладке Commits коммит `test: …` сделан раньше коммита с `code_tools.py`. Сверяйте время коммитов (наведите курсор на дату), а не место в списке: на GitHub старые коммиты сверху, на GitLab — снизу. Если PR практики 1 не влит (шаг 1.2, «Влить сейчас нельзя»), в Files changed будут и файлы практики 1: первый Tool, фабрика LLM, логи `run-0*.log`. Это нормально — напишите об этом в первой строке описания PR.

**Если не получилось.** `rejected` при `git push` — `git pull --rebase`, затем `git push`.

> **Стоп-точка (02:30)** — преподаватель: попросите каждую команду отправить ссылку на свой PR в общий чат одним сообщением и начните peer review.

### Шаг 5.2: Peer review (15 мин)

Первые 8 минут читаете PR пары и оставляете комментарии в строках diff, следующие 7 — разбираете замечания к своему. Формула: **что заметил → чем грозит → что предлагаю**.

**Чек-лист для проверки чужого PR**

Файлы практики 1 в PR пары (в описании сказано, что PR практики 1 не влит) — не замечание: проверяйте по чек-листу только файлы практики 2.

- [ ] `.env` нет ни в Files changed, ни в коммитах; в `.env.example` есть `AI_DENY_GLOBS`, `AI_EXCLUDE_DIRS`, `AI_TOOL_TIMEOUT_S`.
- [ ] В Commits коммит с тестами раньше коммита с кодом инструментов.
- [ ] Все три инструмента вызывают одну проверку пути; у поиска файлы под deny-list не читаются вообще (атака S5).
- [ ] В `code_tools.py` нет `shell=True`, `os.system` и аргумента `"--fix"` (`--no-fix` — норма, а `"--fix"` в тесте L4 — это атака, а не вызов); у ruff есть `--no-cache` и `"--"` перед путём (`Ctrl+F` в Files changed).
- [ ] Коды ruff: 1 — `ok` с замечаниями, 2 и выше — `error`, а не `ok` с пустым списком. Конфигурация ruff — только бэкенда, иначе `--isolated`; `--config` с файлом помощника не передаётся.
- [ ] Лимиты: у `read_file` и поиска есть потолок, в ответе `total_*` и `truncated`.
- [ ] Тесты не импортируют CrewAI и работают на `tmp_path`, а не на `../<проект>`.
- [ ] Docstring каждой обёртки говорит модели, **когда** вызывать инструмент, и перечисляет допустимые значения без примеров настоящих путей.
- [ ] В `run-p2-02.log` есть `"status": "error"` от `run_linter`, нет `Traceback`.
- [ ] Если всё остальное проверено и есть доступ к их репозиторию: в клоне их ветки `python -m pytest -q` зелёный. Хватит вашего окружения помощника; `.env`, модель и CrewAI для тестов не нужны.

### Шаг 5.3: ADR 002 (10 мин)

Создайте `docs/adr/002-code-tools.md` по шаблону, закоммитьте в ту же ветку и допушьте. Каталога `docs/adr` в ветке может не быть — создайте его (если он есть, команда ничего не меняет): `mkdir -p docs/adr` (PowerShell: `New-Item -ItemType Directory -Force docs/adr`).

```bash
git add docs/adr/002-code-tools.md
git commit -m "docs: add ADR 002 on code tools"
git push
```

```markdown
# ADR 002: Инструменты для работы с кодом бэкенда

**Статус:** Принято
**Дата:** <дата занятия>
**Команда:** <имена>

## Контекст
Агенту нужны поиск, чтение и линтер по коду бэкенда; путь приходит от модели;
бэкенд только читается; облачный провайдер — канал наружу.

## Рассмотренные варианты
Deny-list против allow-list; поиск подстрокой против регулярных выражений;
чья конфигурация ruff (бэкенда или правила по умолчанию, почему не помощника;
flake8 в CI бэкенда); ваша v2 против каркаса курса — что взяли, что сделали иначе.

## Решение
Граница доступа, лимиты, интерпретация кодов ruff —
по одному предложению на аргумент.

## Последствия
Что стало проще, что усложнилось, чем платим (например: .env.example
бэкенда агенту недоступен).

## Наблюдения из трассы
run-p2-01: какие инструменты и с какими аргументами вызвал агент.
run-p2-02: что агент ответил на error от run_linter.
Атаки без теста (G1, G2) — почему и что их сдерживает.

## Когда пересмотреть
Например: линтер должен проверять сгенерированный код, которого нет в бэкенде.
```

**Документация.** [adr.github.io](https://adr.github.io/) — шаблоны; глубину аргументации берите из ADR 001.

---

## Итог (02:55–03:00)

Команда отвечает по чек-листу самопроверки: всё закрыто или что именно осталось. Незакрытое уходит в домашнее задание, в тот же PR.

> **Стоп-точка (02:55)** — преподаватель: соберите у команд ответ — закрыт ли чек-лист самопроверки (да / что осталось).

---

## Чек-лист самопроверки команды

**Репозиторий**

- [ ] В `feature/code-tools` есть код практики 1 и спецификация v2; PR в `main` открыт, ссылка в чате.
- [ ] `requirements.txt`: `ruff==0.17.0`, `pytest==9.1.1`; `pip check` без ошибок.
- [ ] `.env` нет в diff; `.env.example` — с тремя новыми переменными.
- [ ] В репозитории бэкенда ничего не изменено, `.ruff_cache/` в нём нет.

**Инструменты**

- [ ] `ai/tools/code_tools.py`: три инструмента, одна проверка пути, лимиты по v2.
- [ ] `run_linter`: код 1 — `ok`, код 2 — `error`; `--no-cache`, `"--"`, `shell=False`.
- [ ] Ни один путь выполнения не выбрасывает исключение наружу.

**Тесты**

- [ ] `tests/test_invariants.py` без изменений, `python -m pytest -q` зелёный.
- [ ] Пять своих тестов-атак; коммит `test:` раньше кода.
- [ ] Атаки без теста (G1, G2) разобраны в ADR.

**Агент и документы**

- [ ] `run-p2-01.log` — вызов одного из трёх инструментов; `run-p2-02.log` — `error` от `run_linter`, без traceback.
- [ ] `docs/adr/002-code-tools.md` заполнен, включая минусы решения.
- [ ] Роли и вывод `pytest` — в описании PR; замечания peer review — в PR.

---

## Что сдаётся по итогам занятия

Одна **ссылка на Pull Request** `feature/code-tools` → `main` в репозитории помощника, отправленная в общий чат до конца пары. В нём: код, тесты, две трассы, ADR 002, роли и вывод `pytest` в описании, комментарии соседней команды. Незаконченное доделывается дома в тот же PR (домашнее задание, п. 1).

---

## Troubleshooting

| Симптом | Вероятная причина | Что сделать |
|---|---|---|
| `ModuleNotFoundError: No module named 'ai'` при `pytest` | Запущен `pytest` вместо `python -m pytest` или не из корня помощника | `python -m pytest -q` из корня помощника |
| `ModuleNotFoundError: No module named 'ai.tools.code_tools'` | Каркас ещё не скопирован — до шага 3.1 это ожидаемо | Шаг 3.1 |
| `ValidationError` … `ai_repo_root` при сборе тестов | Нет `tests/conftest.py` или строка `os.environ.setdefault` стоит после импорта `ai.config` | Шаг 2.2: `setdefault` — до импорта |
| `SettingsError: error parsing value for field "ai_deny_globs"` | Поле объявлено как `list[str]` | Строка через запятую, шаг 2.1 |
| `run_linter` → `ruff не установлен в окружении агента` | ruff не в окружении помощника | Шаг 1.3; `python -m ruff --version` |
| `No module named ruff` сразу после `pip install` | Окружение создано `uv venv` без `--seed`: своего `pip` в нём нет, пакеты ушли в системный Python | `uv pip install -r requirements.txt` («Подготовка», п. 2) |
| `run_linter` → `ruff завершился аварийно` на своём бэкенде | Битая конфигурация ruff у бэкенда | Помощник её не чинит: сообщить команде бэкенда (PR людей) |
| `run_linter` → `ok` с одним замечанием `E902` | Проверка существования пути удалена из кода | Вернуть проверку `target.exists()` до запуска ruff |
| В бэкенде появился `.ruff_cache/` (виден в `ls -a`, в `git status` — никогда) | ruff запускали без `--no-cache` | Удалить только этот каталог (шаг 3.4, «Если не получилось»); в коде — `--no-cache` |
| `test_linter_ignores_config_outside_backend` упал | В `_ruff_config_args` пропал `--isolated` или добавлен `--config` | Вернуть функцию из каркаса (шаг 3.3, п. 2) |
| `test_l1_ruff_not_installed` получил `ok` | `from ruff import …` стоит в начале модуля, а не внутри `_ruff_bin()` | Импорт — внутри функции, как в каркасе |
| Тест с `mock.patch` запускает настоящий ruff | Неверный путь в `patch` | `ai.tools.code_tools.subprocess.run` |
| `NameError: name 'run_linter' is not defined` в тестах L1 и L5 | `run_linter` не импортирован в `tests/test_code_tools.py` | Дописать в `from ai.tools.code_tools import …` (шаг 3.3, п. 3) |
| `test_tests_do_not_import_crewai` упал | Импорт CrewAI на уровне модуля в `code_tools.py` или тестах | Импорт — только внутри `crewai_tools()` |
| `ValueError` … `arguments validation failed` в трассе | Модель передала не тот тип; CrewAI отклонил вызов до кода | Не ошибка инструмента; запишите в ADR, если агент не исправился |
| Агент на провокацию ответил «замечаний нет» | Модель исказила `error` инструмента | Находка для ADR; подсказка в `hint` уже говорит «результат неизвестен» |
| `git merge main` ничего не принёс | PR практики 1 не влит | Шаг 1.2, «Если не получилось» |
| `CONFLICT` при `git merge` | Обе ветки правили `.gitignore` или `README.md` | Оставить строки обеих версий, `git add`, `git commit --no-edit` |
| `Sync handler error … 'charmap' codec` в логе | Не задан `PYTHONUTF8=1` | Шаг 4.2 |
| После шага 4.3 в PowerShell: `ValidationError` … `p2-lint-copy` … `Path does not point to a directory` | Запуск прерван `Ctrl+C`, в окне осталась переменная `AI_REPO_ROOT` | `Remove-Item Env:AI_REPO_ROOT` или новое окно (в Git Bash переменная живёт одну команду) |
| Агент ответил «не найдено», в `Args` угаданы `path` или `path_glob` | Модель сузила поиск и не повторила его по `hint` | Фраза про `hint` в `backstory` (шаг 4.1, п. 3); шаг 4.2, «Если не получилось» |
| В трассе вызван только первый Tool практики 1, код функции придуман | `goal` агента остался «про эндпоинты» | Шаг 4.1, п. 3 |
| Лог в PR показан как двоичный, поиск по нему ничего не находит | Лог записан `Tee-Object` в Windows PowerShell 5.1 — в UTF-16 | `(Get-Content <лог>) \| Set-Content -Encoding utf8 <лог>`, коммит (шаг 4.2) |
| `Set-Content` записал `ruff.toml`, а ruff всё равно отвечает кодом 0 | Файл лёг не в копию или `AI_REPO_ROOT` не переопределён | `Get-Content ../p2-lint-copy/ruff.toml`; переменная — в том же окне |

---

## Домашнее задание (СРС, 1,5–2 часа)

**Срок — до воркшопа 3.**

1. **Хвосты с пары (30–60 мин).** Закройте замечания peer review, доделайте трассы и ADR. PR должен быть готов к слиянию в `main` помощника.
2. **Краевые случаи v2 (30 мин).** Все `TODO по вашей v2` в `code_tools.py` закрыты, на каждый — тест.
3. **README помощника (15 мин).** Раздел «Инструменты»: что делает каждый, параметры, переменные `AI_REPO_ROOT`, `AI_DENY_GLOBS`, `AI_EXCLUDE_DIRS`, `AI_TOOL_TIMEOUT_S`, как запустить тесты (`python -m pytest -q`). Это требование «Definition of Done» к README помощника.
4. **Если в команде есть облачный ключ (15 мин).** Повторите шаг 4.3 по пути Б (`LLM_PROVIDER=cloud`), лог — `ai/traces/run-p2-02-cloud.log`; в ADR — отличалось ли поведение. Помните: всё, что вернул инструмент, уходит провайдеру — граница доступа защищает и от этого.

---

## Сводка ссылок

**Тесты**

- [pytest: Get Started](https://docs.pytest.org/en/stable/getting-started.html) — первые тесты и вывод `-q`.
- [pytest: tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html) — временный каталог на каждый тест.
- [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) — фикстуры и `conftest.py`.
- [unittest.mock: patch](https://docs.python.org/3/library/unittest.mock.html#patch) — подмена `subprocess.run`, `side_effect`; [`patch.dict`](https://docs.python.org/3/library/unittest.mock.html#patch-dict) — подмена `sys.modules`; [The module cache](https://docs.python.org/3/reference/import.html#the-module-cache) — почему `None` в `sys.modules` означает «модуля нет».

**Python и ruff**

- [`pathlib`: `resolve()` и `is_relative_to()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve).
- [`subprocess`: Security Considerations](https://docs.python.org/3/library/subprocess.html#security-considerations) — почему не `shell=True`.
- [`ast`](https://docs.python.org/3/library/ast.html) — разбор кода для `kind="symbol"`.
- [Ruff: Exit codes](https://docs.astral.sh/ruff/linter/#exit-codes) — коды 0, 1, 2.
- [Ruff: Config file discovery](https://docs.astral.sh/ruff/configuration/#config-file-discovery) — чья конфигурация применяется.

**CrewAI и конфигурация**

- [CrewAI: Create Custom Tools](https://docs.crewai.com/en/learn/create-custom-tools) — `@tool` и `BaseTool`.
- [CrewAI: Agents](https://docs.crewai.com/en/concepts/agents) — `tools`, `max_iter`.
- [pydantic-settings](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/) — «Parsing environment variable values».

**Процесс**

- [Каркас инструментов курса](../templates/tool-lsp-example.py).
- [GitHub Docs: Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).
- [Conventional Commits (рус.)](https://www.conventionalcommits.org/ru/v1.0.0/) — тип `test`.
- [Architectural Decision Records](https://adr.github.io/).

---

## История изменений

| Дата | Что изменено |
|---|---|
| 2026-10-13 | Первая версия: вливание PR практики 1 и `git merge main` в `feature/code-tools`; ruff и pytest в `requirements.txt`; настройки `AI_DENY_GLOBS`, `AI_EXCLUDE_DIRS`, `AI_TOOL_TIMEOUT_S` в `AISettings`; тесты на `tmp_path` до кода, обязательный `tests/test_invariants.py`, запасной список атак; каркас `templates/tool-lsp-example.py` → `ai/tools/code_tools.py`; L1/L5 через `unittest.mock`; агент с тремя инструментами и провокация битой конфигурацией ruff на копии бэкенда; ADR 002 |
| 2026-10-14 | ruff запускается через `find_ruff_bin()` (таймаут на Windows останавливает сам ruff), тест L1 — через `mock.patch.dict` на `sys.modules`; конфигурация ruff — бэкенда, иначе `--isolated`, конфигурация помощника не применяется (новый обязательный тест, счётчики 15 / 20 / 22); запасной список R3, R6, S5, S2, L4 — два теста красные на голом каркасе, красный запуск на каркасе в шаге 3.1; таблица текстов ошибок каркаса для подстрок в тестах; приведение `read_file` и `search_codebase` к своей v2 вместе с обёртками `crewai_tools()`; `git push` тестов и каркаса для работы двумя парами; обновление клона курса в «Подготовке»; подсказка при нуле совпадений у поиска — готовая часть каркаса, `path_glob` в описании для модели; признак «Не успеваете?» в 01:20 по своим тестам; порядок коммитов в PR — по времени; ожидаемый вывод шага 4.3 — `Failed to parse`; один повтор запуска на паре; переменная `AI_REPO_ROOT` после прерванного запуска в PowerShell; тексты `check_path` в тестах — всегда по каркасу; таблица имён параметров и полей каркаса в шаге 2.3, переименование под v2 — по желанию; запасной список дополняет свои атаки до пяти; данные для атаки — файлом в тесте; на паре обязательны только `TODO` с тестами; `goal` и `backstory` агента в шаге 4.1, описание `path` и подсказка при несуществующем каталоге в каркасе; `ls -a` бэкенда в шаге 3.4 (`.ruff_cache` не виден в `git status`); `uv pip` в окружении uv и вывод `uv pip check`; перекодировка лога Windows PowerShell 5.1 в UTF-8; стоп-точка 01:20 — после шага 3.2; пункт чек-листа про `"--fix"`; шаг 3.1 — что делать, если все свои тесты зелёные на голом каркасе (тесты на правила v2, которых нет в каркасе); хотя бы одна атака на `run_linter` среди своих (L4 первой), спецификация v1 дополняется до пяти; `run_linter` в импорте тестов для L1/L5 и симптом `NameError`; `git push` после шага 1.3 при двух парах; красные тесты другой пары до сведения; файлы практики 1 в PR при невлитом PR практики 1; `mkdir docs/adr`; `.env.example` — со своими значениями; `pip` в окружении `uv venv --seed` |
| 2026-10-14 | Каркас и учебный бэкенд — из клона открытого репозитория курса `github.com/andrey-limasov/agent-dev`: «Подготовка», п. 1 — адрес для `git clone`, если клона нет, и архив ZIP при недоступном GitHub; шаг 3.1, «Если не получилось» — запасной путь: файл каркаса со страницы репозитория |
