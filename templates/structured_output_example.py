"""Контракт итога Crew: модель Pydantic, проверки кодом и отказ вместо traceback.

Каркас практики 5. Копируется в репозиторий помощника:

    cp <клон курса>/templates/structured_output_example.py ai/crew_result.py

Источник правды для полей — раздел 2 docs/result-contract.md вашей команды. Здесь
обязательный минимум курса: имена и типы полей не меняйте, все поля минимума обязательны,
пустое значение — пустая строка или пустой список.

Что готово:
- CrewResult — итог последней задачи Crew, для output_pydantic. Значения Literal —
  латиницей, описаний Field нет: схема модели попадает в промпт, а кириллица уходит
  туда как \\uXXXX. Шаблоны pattern только полные, от ^ до $: на неполный Ollama
  отвечает 400, на пути конвертера это ConverterError. expected_fields — список
  объектов; list[tuple] на qwen3:4b-instruct отвергался.
- check_result — проверки, которые форма итога сделать не может: пара метод и путь есть
  в схеме, файл теста есть и записан в этом запуске, при found есть и тест-кейс, и файл,
  при статусе не found ни один файл теста в этом запуске не записан.
- run_and_check — запуск Crew: отказ формата, отказ проверки кодом и сбой запуска (LLM
  недоступна, обрыв соединения) становятся сообщением и кодом возврата 1, файл в
  generated/ при этом остаётся.

Что дописывает команда (пометка «TODO по вашему контракту»): свои поля и ограничения
по столбцу «Что при нарушении». «Отказ формата» — это Field или Literal здесь, «отказ
кода» — строка в check_result, «заметит человек» — ни то, ни другое.

Версия crewai==1.15.22 закреплена: в 1.15.37 на том же ответе исключения нет, а
result.pydantic равен None. Ветка «итог не разобран» закрывает и этот случай.

CrewAI здесь не импортируется, обязательные тесты его не загружают: ConverterError
передаётся аргументом converter_errors из ai/run_crew.py.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from ai.tools.generated_files import assistant_root

KEEP_FILE = "Файл в generated/, если он записан, остаётся: проверьте его сами."


class ExpectedField(BaseModel):
    field: str
    value: str | int | float | bool | None  # литерал или «вычисляет сервер»


class GeneratedTest(BaseModel):
    """Элемент test_cases. Имя не начинается с Test: иначе pytest примет класс за набор тестов."""

    name: str = Field(pattern=r"^test_[A-Za-z0-9_]+$")
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str = Field(pattern=r"^/.*$")  # как в схеме, с параметром: /notes/{note_id}
    expected_status: int = Field(ge=100, le=599)
    expected_fields: list[ExpectedField]
    source: str = Field(min_length=1)
    # TODO по вашему контракту: свои поля элемента, со значением по умолчанию: обязательные тесты их не передают


class CrewResult(BaseModel):
    """Итог последней задачи Crew: минимум курса, таблица раздела 2 docs/result-contract.md."""

    search_status: Literal["found", "not_found", "tool_error"]
    test_file: str = Field(pattern=r"^(generated/test_[A-Za-z0-9_]+\.py)?$")  # пустая, если теста нет
    test_cases: list[GeneratedTest] = Field(max_length=3)
    linter_result: str
    note: str = Field(min_length=1)
    # TODO по вашему контракту: свои поля итога, со значением по умолчанию: обязательные тесты их не передают


def _file_problems(test_file: str, started: float, root: Path) -> list[str]:
    """Файл есть и изменён не раньше начала запуска: старый файл не считается результатом."""
    try:
        modified = (root / test_file).stat().st_mtime
    except (OSError, ValueError):  # нет файла; не путь, а текст теста
        return [f"файла {test_file[:80]} нет на диске"]
    if modified < started:
        return [f"файл {test_file} не записан в этом запуске: write_generated его не менял"]
    return []


def _fresh_tests(started: float, root: Path) -> list[str]:
    """Файлы generated/test_*.py, изменённые в этом запуске: поле test_file заполняет модель."""
    fresh = []
    for path in sorted((root / "generated").glob("test_*.py")):
        try:
            if path.stat().st_mtime >= started:
                fresh.append(f"generated/{path.name}")
        except OSError:  # файл исчез между просмотром каталога и stat
            continue
    return fresh


def check_result(result: CrewResult, schema: dict, started: float, root: Path | None = None) -> list[str]:
    """Проверки кодом -> список нарушений; пустой список — проверки пройдены."""
    root = Path(root) if root is not None else assistant_root()
    problems: list[str] = []
    paths = schema.get("paths", {})
    for case in result.test_cases:
        operations = paths.get(case.path)
        if not isinstance(operations, dict) or case.method.lower() not in operations:
            problems.append(f"пары {case.method} {case.path} нет в схеме")
    if result.search_status == "found" and not result.test_cases:
        problems.append("search_status found, а test_cases пуст")
    if result.search_status == "found" and not result.test_file:
        problems.append("search_status found, а test_file пуст")
    if result.test_file:
        problems.extend(_file_problems(result.test_file, started, root))
    if result.search_status != "found":
        for name in _fresh_tests(started, root):
            problems.append(f"search_status {result.search_status}, а файл {name} записан в этом запуске")
    # TODO по вашему контракту: строки «отказ кода» из столбца «Что при нарушении».
    return problems


def _refuse(kind: str, details: str) -> int:
    print(f"{kind}: {details}")
    print(KEEP_FILE)
    return 1


def run_and_check(
    kickoff,
    schema: dict,
    root: Path | None = None,
    converter_errors: tuple = (),
    timeout_s: int | None = None,
) -> int:
    """Запустить Crew и проверить итог -> код возврата: 0 — объект и проверки, 1 — отказ."""
    started = time.time()
    try:
        result = kickoff()
    except TimeoutError:
        limit = f" в {timeout_s} с" if timeout_s else ""
        return _refuse(f"Crew не уложилась{limit} на задачу агента", "результат не получен.")
    except ValidationError as exc:
        fields = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or 'итог'}: {error['msg']}" for error in exc.errors()
        )
        return _refuse("Отказ формата", f"итог не прошёл проверку контракта ({fields}).")
    except converter_errors as exc:
        return _refuse("Отказ формата", f"итог не удалось привести к контракту ({exc.__class__.__name__}).")
    except Exception as exc:  # noqa: BLE001 — граница запуска: LLM недоступна, обрыв соединения
        return _refuse("Сбой запуска", f"{exc.__class__.__name__}: {str(exc)[:300]}")
    if result.pydantic is None:
        return _refuse("Отказ формата", f"итог не разобран, объекта нет. Текст итога: {str(result.raw)[:500]}")
    problems = check_result(result.pydantic, schema, started, root)
    if problems:
        print(result.pydantic.model_dump_json(indent=2))
        return _refuse("Отказ кода", "; ".join(problems) + ".")
    print(result.pydantic.model_dump_json(indent=2))
    return 0
