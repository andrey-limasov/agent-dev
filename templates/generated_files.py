"""Каталог результата помощника generated/: Tool записи write_generated и второй корень run_linter.

Каркас практики 4. Копируется в репозиторий помощника:

    cp <клон курса>/templates/generated_files.py ai/tools/generated_files.py

generated/ лежит в корне репозитория помощника, а не бэкенда: помощник бэкенд
только читает. Путь с префиксом generated/ всегда означает этот каталог — даже если
в бэкенде есть свой каталог с таким именем, через инструменты он недоступен.

Что готово и не меняется (на это опираются обязательные тесты
tests/test_generated_tools.py и следующие занятия): имена GENERATED_DIR,
check_generated_path, write_generated, тексты их ошибок. write_generated — первый
инструмент курса, который пишет на диск: только файл generated/test_<имя>.py,
та же проверка пути, что у check_path практики 2 (граница корня, deny-list),
вне generated/ — ошибка. generated/conftest.py инструмент не перезапишет: имя
файла должно начинаться с test_.

run_linter из code_tools.py проверяет generated/ вторым корнем после трёх правок
в его теле (шаг 2.3 практики 4): путь с префиксом generated/ проверяется
check_generated_path, корень и рабочий каталог ruff — корень помощника, ruff
запускается с --isolated (правила ruff по умолчанию, конфигурация помощника
к сгенерированному тесту не применяется). Имена, поля и тексты run_linter
и check_path не меняются.

Внутренние функции получают настройки явным аргументом s, как в code_tools.py.
CrewAI импортируется только внутри crewai_tools(): тесты не загружают CrewAI.
Инструмент не запускает сгенерированный тест: его запускает человек pytest'ом.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from ai.config import AISettings
from ai.tools.code_tools import _fail, _ok, check_path

GENERATED_DIR = "generated"  # каталог результата помощника, от корня помощника
ASSISTANT_ROOT = Path(__file__).resolve().parents[2]  # ai/tools/generated_files.py -> корень
MAX_CONTENT_CHARS = 20_000  # потолок размера одного файла теста, символов
TEST_NAME = re.compile(r"test_[A-Za-z0-9_]+\.py")  # без «:» и пробелов: имя одинаково на всех ОС


def _outside() -> str:
    return _fail(
        "путь вне каталога generated/",
        hint="пиши и проверяй только файлы generated/test_<имя>.py в репозитории помощника",
    )


def assistant_root() -> Path:
    """Корень репозитория помощника (тесты подменяют ASSISTANT_ROOT)."""
    return Path(ASSISTANT_ROOT).resolve()


def is_generated(path: object) -> bool:
    """Путь от модели начинается с generated/ (прямые или обратные слэши, ./ в начале)."""
    if not isinstance(path, str) or not path.strip():
        return False
    parts = PurePosixPath(path.strip().replace("\\", "/")).parts
    return bool(parts) and parts[0] == GENERATED_DIR


def generated_settings(s: AISettings) -> AISettings:
    """Те же настройки (deny-list, таймаут), но корень — репозиторий помощника."""
    return s.model_copy(update={"ai_repo_root": assistant_root()})


def check_generated_path(path: str, s: AISettings) -> tuple[Path | None, str | None]:
    """Путь от модели -> (абсолютный путь внутри generated/, None) или (None, JSON ошибки).

    Сначала check_path практики 2 с корнем помощника (пустой путь, абсолютный путь,
    выход за корень, deny-list), затем граница каталога generated/.
    """
    if not is_generated(path):
        return None, _outside()
    # Обратные слэши — как прямые и на Linux / macOS: путь от модели значит одно и то же на всех ОС.
    target, err = check_path(path.replace("\\", "/"), generated_settings(s))
    if err:
        return None, err
    if not target.is_relative_to(assistant_root() / GENERATED_DIR):
        return None, _outside()  # generated/../ai/config.py
    return target, None


def write_generated(path: str, content: str, s: AISettings) -> str:
    """Записать (или перезаписать) файл теста generated/test_<имя>.py."""
    target, err = check_generated_path(path, s)
    if err:
        return err
    directory = assistant_root() / GENERATED_DIR
    if target.parent != directory or not TEST_NAME.fullmatch(target.name):
        return _fail(
            "писать можно только файл generated/test_<имя>.py",
            hint="имя: test_, затем латинские буквы, цифры и _, в конце .py; без подкаталогов",
        )
    if not isinstance(content, str) or not content.strip():
        return _fail("пустое содержимое файла", hint="передай в content полный текст теста")
    if len(content) > MAX_CONTENT_CHARS:
        return _fail(
            f"файл длиннее {MAX_CONTENT_CHARS} символов",
            hint="один тест на одно поведение — короткий файл",
        )
    try:
        directory.mkdir(exist_ok=True)
        target.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8", newline="\n")
    except OSError as exc:
        return _fail(f"файл не удалось записать: {exc.__class__.__name__}")
    rel = target.relative_to(assistant_root()).as_posix()
    return _ok(
        path=rel,
        lines=len(content.splitlines()),
        hint=f"проверь файл линтером: run_linter с path='{rel}'",
    )


# ---------------------------------------------------------------------------
# Обёртка для агента (CrewAI импортируется только здесь)
# ---------------------------------------------------------------------------


def crewai_tools(s: AISettings | None = None) -> list:
    """Инструмент write_generated для Agent(tools=...). Настройки по умолчанию — из .env."""
    from crewai.tools import tool

    s = s or AISettings()

    @tool("write_generated")
    def write_generated_tool(path: str, content: str) -> str:
        """Записывает файл pytest-теста в каталог generated/ репозитория помощника.
        Файл с тем же именем перезаписывается: так исправляют тест после замечаний
        линтера. Бэкенд этим инструментом изменить нельзя. После записи проверь файл
        инструментом run_linter с тем же path.

        Args:
            path: только generated/test_<имя>.py, прямые слэши.
            content: полный текст файла теста на Python.

        Returns:
            JSON-строка. Успех: {"status": "ok", "path", "lines", "hint"}.
            Ошибка: {"status": "error", "message", "hint"}.
        """
        return write_generated(path, content, s)

    return [write_generated_tool]
