"""Три инструмента для работы с кодом бэкенда: read_file, search_codebase, run_linter.

Каркас практики 2. Копируется в репозиторий помощника под именем модуля
с подчёркиваниями (модуль с дефисом в имени не импортируется):

    cp <клон курса>/templates/tool-lsp-example.py ai/tools/code_tools.py

Аналоги из темы недели: ctags (где определено имя) — search_codebase(kind="symbol"),
grep — search_codebase(kind="text"), диагностика LSP — run_linter, «открыть файл
на строке» — read_file с start_line.

Что готово и не меняется: единый формат ответа (_fail, _ok), единая проверка
пути (check_path, is_denied), обход дерева без выхода за корень и без ссылок
(iter_files), подсказка при нуле совпадений у search_codebase, run_linter целиком
(вызов ruff, коды 0/1/2, конфигурация ruff, фильтр находок по deny-list).
Что дописывает команда: места с пометкой «TODO по вашей v2» — лимиты и краевые
случаи read_file и search_codebase из вашей спецификации docs/tools-spec-cycle2.md.
Имена параметров, поля ответа и тексты ошибок read_file и search_codebase можно
привести к своей v2 (вместе с обёртками в crewai_tools() внизу файла), кроме ответов
check_path («путь вне репозитория», «доступ к файлу запрещён политикой»): их
read_file и search_codebase возвращают как есть. У check_path и run_linter имена,
поля и тексты общие для курса — на них опираются обязательные тесты.

Внутренние функции получают настройки явным аргументом s: тесты передают
AISettings(ai_repo_root=tmp_path, _env_file=None) и не зависят от .env.
CrewAI импортируется только внутри crewai_tools(): pytest его не загружает.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import os
import subprocess
import time
from pathlib import Path, PurePosixPath, PureWindowsPath

from ai.config import AISettings

# ---------------------------------------------------------------------------
# Формат ответа (как _fail практики 1, плюс подсказка агенту hint)
# ---------------------------------------------------------------------------


def _fail(message: str, **extra) -> str:
    """Единый формат ошибки, который вернётся агенту."""
    return json.dumps({"status": "error", "message": message, **extra}, ensure_ascii=False)


def _ok(**fields) -> str:
    """Единый формат успешного ответа."""
    return json.dumps({"status": "ok", **fields}, ensure_ascii=False)


def _split(value: str) -> list[str]:
    """Строка настройки через запятую -> список без пустых элементов."""
    return [part.strip() for part in value.split(",") if part.strip()]


def _as_int(value, name: str, default: int, low: int, high: int) -> tuple[int | None, str | None]:
    """Число из аргумента модели: не число -> ошибка, вне диапазона -> к границе."""
    if value is None:
        return default, None
    if isinstance(value, bool):
        return None, _fail(f"{name} должен быть целым числом от {low} до {high}")
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None, _fail(f"{name} должен быть целым числом от {low} до {high}, получено {value!r}")
    return max(low, min(number, high)), None


# ---------------------------------------------------------------------------
# Единая проверка пути: её вызывают все три инструмента (готово)
# ---------------------------------------------------------------------------


def is_denied(rel: PurePosixPath | Path, globs: list[str]) -> bool:
    """Компонент относительного пути совпал с шаблоном AI_DENY_GLOBS (без учёта регистра)."""
    return any(
        fnmatch.fnmatchcase(part.lower(), glob.lower()) for part in rel.parts for glob in globs
    )


def check_path(path: str, s: AISettings) -> tuple[Path | None, str | None]:
    """Путь от модели -> (абсолютный путь внутри корня, None) или (None, JSON ошибки)."""
    root = Path(s.ai_repo_root).resolve()
    outside = _fail(
        "путь вне репозитория",
        hint="используй путь относительно корня репозитория — как в ответе search_codebase",
    )
    # 1. До обращения к диску: пустой, нулевой байт, абсолютный, с диском, UNC.
    if not isinstance(path, str) or not path.strip() or "\x00" in path:
        return None, _fail("пустой или недопустимый путь", hint="путь относительно корня репозитория")
    if PureWindowsPath(path).anchor or PurePosixPath(path).is_absolute():
        return None, outside
    # 2. Нормализация: раскрываются .., символические ссылки и junction.
    try:
        candidate = (root / path).resolve()
    except (OSError, ValueError, RuntimeError):
        return None, _fail("путь не удалось разобрать", hint="путь относительно корня репозитория")
    # 3. Граница корня.
    if not candidate.is_relative_to(root):
        return None, outside
    # 4. Deny-list по каждому компоненту нормализованного пути.
    if is_denied(candidate.relative_to(root), _split(s.ai_deny_globs)):
        return None, _fail("доступ к файлу запрещён политикой")
    return candidate, None


def iter_files(start: Path, root: Path, s: AISettings, name_glob: str):
    """Файлы под start, подходящие под шаблон имени; без выхода за корень (готово)."""
    deny = _split(s.ai_deny_globs)
    exclude = {d.lower() for d in _split(s.ai_exclude_dirs)}
    if start.is_file():
        yield start
        return
    for dirpath, dirnames, filenames in os.walk(start, followlinks=False):
        current = Path(dirpath)
        # Отсечь до входа: исключённые, под deny-list, ссылки и junction.
        # os.walk(followlinks=False) на Windows заходит в junction, а
        # os.path.isjunction есть только с Python 3.12 — поэтому resolve():
        # у обычного каталога он путь не меняет, у ссылки и junction — меняет
        # (junction внутрь корня иначе зациклил бы обход).
        dirnames[:] = [
            d
            for d in dirnames
            if d.lower() not in exclude
            and not is_denied(PurePosixPath(d), deny)
            and (current / d).resolve() == current / d
        ]
        for name in filenames:
            if not fnmatch.fnmatchcase(name.lower(), name_glob.lower()):
                continue
            checked, _ = check_path((current / name).relative_to(root).as_posix(), s)
            if checked is not None:  # файл под deny-list не читается вообще
                yield checked


# ---------------------------------------------------------------------------
# read_file
# ---------------------------------------------------------------------------


def read_file(path: str, s: AISettings, start_line: int = 1, max_lines: int = 200) -> str:
    """Фрагмент текстового файла с номерами строк."""
    root = Path(s.ai_repo_root).resolve()
    target, err = check_path(path, s)
    if err:
        return err
    start_line, err = _as_int(start_line, "start_line", 1, 1, 10**9)
    if err:
        return err
    max_lines, err = _as_int(max_lines, "max_lines", 200, 1, 400)
    if err:
        return err
    if not target.exists():
        return _fail("файл не найден", hint="найди правильный путь через search_codebase")
    if target.is_dir():
        return _fail("это каталог, а не файл", hint="найди файл через search_codebase с параметром path")
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return _fail("файл не удалось прочитать")
    # TODO по вашей v2 (каждый случай — проверка здесь и тест на неё):
    # - бинарный файл: нулевой байт в первых 8 КБ и нет BOM UTF-16 -> _fail("файл не текстовый");
    # - start_line за концом непустого файла -> _fail(...) с total_lines в тексте;
    # - BOM UTF-8 отбросить, BOM UTF-16 -> читать файл как UTF-16;
    # - не UTF-8 -> "encoding_warning": true в ответе;
    # - длинная строка -> обрезать (например, до 500 символов) с пометкой;
    # - потолок размера до чтения (например, stat().st_size больше 1 МБ -> error).
    lines = text.splitlines()
    part = lines[start_line - 1 : start_line - 1 + max_lines]
    content = "\n".join(f"{start_line + i}: {line}" for i, line in enumerate(part))
    return _ok(
        path=target.relative_to(root).as_posix(),
        start_line=start_line,
        end_line=start_line + len(part) - 1,
        total_lines=len(lines),
        truncated=start_line - 1 + len(part) < len(lines),
        content=content,
    )


# ---------------------------------------------------------------------------
# search_codebase
# ---------------------------------------------------------------------------


def search_codebase(
    query: str,
    s: AISettings,
    kind: str = "text",
    path: str = ".",
    path_glob: str = "*.py",
    max_results: int = 20,
) -> str:
    """Подстрока (kind="text") или определение def/class (kind="symbol")."""
    root = Path(s.ai_repo_root).resolve()
    q = query.strip() if isinstance(query, str) else ""
    if kind not in ("text", "symbol"):
        return _fail("kind должен быть text или symbol")
    if kind == "text" and not 3 <= len(q) <= 100:
        return _fail("запрос слишком короткий или длинный", hint="передай имя функции, класса или переменной целиком")
    if kind == "symbol" and not q.isidentifier():
        return _fail("для kind=symbol нужно одно имя функции или класса")
    if (
        not isinstance(path_glob, str)
        or not path_glob
        or len(path_glob) > 50
        or any(bad in path_glob for bad in ("/", "\\", "..", ":"))
    ):
        return _fail("path_glob — только шаблон имени файла", hint="подкаталог передай в path")
    max_results, err = _as_int(max_results, "max_results", 20, 1, 50)
    if err:
        return err
    start, err = check_path(path, s)
    if err:
        return err
    if not start.exists():
        return _fail(
            "файл или каталог не найден",
            hint="повтори этот же поиск с path='.' (весь репозиторий), прежде чем отвечать",
        )

    matches: list[dict] = []
    total = 0
    started = time.monotonic()
    timed_out = False
    for file in iter_files(start, root, s, path_glob):
        if time.monotonic() - started > s.ai_tool_timeout_s:
            timed_out = True
            break
        rel = file.relative_to(root).as_posix()
        try:
            text = file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if kind == "symbol":
            try:
                tree = ast.parse(text)
            except (SyntaxError, ValueError):
                continue  # TODO по вашей v2: считать такие файлы в "skipped"
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == q:
                    total += 1
                    if len(matches) < max_results:
                        keyword = "class" if isinstance(node, ast.ClassDef) else "def"
                        matches.append({"path": rel, "line": node.lineno, "kind": keyword})
        else:
            for number, line in enumerate(text.splitlines(), 1):
                if q in line:
                    total += 1
                    if len(matches) < max_results:
                        # TODO по вашей v2: 200 символов вокруг фрагмента, а не от начала строки.
                        matches.append({"path": rel, "line": number, "text": line.strip()[:200]})
    # TODO по вашей v2 (каждый случай — проверка здесь и тест на неё):
    # - слишком общий запрос: total больше 500 -> ok, matches пустой,
    #   hint «запрос слишком общий: найдено N совпадений, уточни запрос»;
    # - файлы, которые ast не разобрал, -> "skipped": N в ответе.
    extra = {}
    if total == 0:  # без подсказки модель отвечает «такого нет», не проверив весь репозиторий
        if path_glob != "*.py" or path.strip() not in (".", ""):
            extra["hint"] = (
                "ничего не найдено в этой части репозитория: повтори с path='.' и "
                "path_glob='*.py', прежде чем отвечать, что этого нет"
            )
        elif kind == "symbol":
            extra["hint"] = (
                "определения с таким именем нет: имя может быть переменной или импортом — "
                "попробуй kind='text'"
            )
        else:
            extra["hint"] = "ничего не найдено: проверь написание или поищи часть имени"
    return _ok(
        query=q,
        kind=kind,
        total_matches=total,
        returned=len(matches),
        truncated=total > len(matches),
        timed_out=timed_out,
        matches=matches,
        **extra,
    )


# ---------------------------------------------------------------------------
# run_linter (готово целиком)
# ---------------------------------------------------------------------------


def _ruff_config_in(directory: Path) -> Path | None:
    """Файл конфигурации ruff в каталоге: ruff.toml, .ruff.toml или pyproject.toml с [tool.ruff]."""
    for name in ("ruff.toml", ".ruff.toml"):
        if (directory / name).is_file():
            return directory / name
    pyproject = directory / "pyproject.toml"
    try:
        if pyproject.is_file() and "[tool.ruff" in pyproject.read_text(encoding="utf-8", errors="replace"):
            return pyproject
    except OSError:
        return None
    return None


def _ruff_config_args(target: Path, root: Path) -> list[str]:
    """Чья конфигурация ruff: бэкенда, если она есть; иначе правила ruff по умолчанию.

    Конфигурация помощника к бэкенду не применяется: свои правила помощник не навязывает.
    """
    directory = target if target.is_dir() else target.parent
    while True:
        if _ruff_config_in(directory):
            return []  # конфигурация бэкенда: ruff найдёт её сам (cwd=root)
        if directory == root:
            break
        directory = directory.parent
    # --isolated: не подхватывать конфигурации выше корня бэкенда и пользовательскую.
    return ["--isolated"]


def _ruff_bin() -> str | None:
    """Путь к бинарнику ruff из окружения помощника или None, если ruff не установлен.

    Не «python -m ruff»: на Windows эта обёртка запускает ruff.exe дочерним процессом,
    и по таймауту subprocess.run убивает обёртку, а ruff продолжает работать.
    """
    try:
        from ruff import find_ruff_bin

        return find_ruff_bin()
    except (ImportError, FileNotFoundError):
        return None


def run_linter(path: str, s: AISettings, max_findings: int = 30) -> str:
    """ruff check без исправлений и без кеша; коды 0 и 1 -> ok, 2 и выше -> error."""
    root = Path(s.ai_repo_root).resolve()
    target, err = check_path(path, s)
    if err:
        return err
    max_findings, err = _as_int(max_findings, "max_findings", 30, 1, 100)
    if err:
        return err
    if not target.exists():  # иначе ruff вернёт код 1 и «замечание» E902
        return _fail("файл или каталог не найден", hint="найди путь через search_codebase")
    rel = target.relative_to(root).as_posix() or "."
    ruff = _ruff_bin()
    if ruff is None:
        return _fail(
            "ruff не установлен в окружении агента",
            hint="проверка не выполнена, сообщи об этом пользователю",
        )
    deny = _split(s.ai_deny_globs)
    cmd = [ruff, "check", "--output-format=json", "--no-fix", "--no-cache"]
    cmd += _ruff_config_args(target, root)
    for glob in deny:
        cmd += ["--extend-exclude", glob]
    cmd += ["--", rel]
    try:
        result = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=s.ai_tool_timeout_s,
            shell=False,
            check=False,  # коды возврата разбираем сами: 1 — не ошибка
        )
    except subprocess.TimeoutExpired:
        return _fail(
            f"проверка не уложилась в {s.ai_tool_timeout_s} с",
            hint="проверь конкретный файл или подкаталог",
        )
    except OSError as exc:
        return _fail(f"ruff не удалось запустить: {exc.__class__.__name__}")
    stderr = (result.stderr or "").replace(str(root), ".")
    if result.returncode not in (0, 1):
        return _fail(
            "ruff завершился аварийно",
            stderr=stderr[-500:],
            hint="проверка не выполнена, результат неизвестен — не сообщай, что замечаний нет",
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return _fail("не удалось разобрать вывод ruff", head=(result.stdout or stderr)[:300])

    findings = []
    resolved: dict[str, Path | None] = {}  # файлов мало, находок много: resolve() — раз на файл
    for item in data:
        filename = item.get("filename")
        rel_file = None
        if filename:
            if filename not in resolved:
                try:
                    resolved[filename] = Path(filename).resolve().relative_to(root)
                except (ValueError, OSError):
                    resolved[filename] = None
            rel_file = resolved[filename]
            if rel_file is None:
                continue  # файл вне корня (ссылка наружу) — не показываем
            if is_denied(rel_file, deny):
                continue  # --extend-exclude учитывает регистр, deny-list — нет
        location = item.get("location") or {}
        findings.append(
            {
                "path": rel_file.as_posix() if rel_file else None,
                "line": location.get("row"),
                "rule": item.get("code") or "invalid-syntax",
                "message": item.get("message"),
            }
        )

    def priority(finding: dict) -> int:
        rule = finding["rule"]
        return 0 if rule == "invalid-syntax" else 1 if rule.startswith("F") else 2

    findings.sort(key=priority)
    by_rule: dict[str, int] = {}
    for finding in findings:
        by_rule[finding["rule"]] = by_rule.get(finding["rule"], 0) + 1
    return _ok(
        path=rel,
        total_findings=len(findings),
        returned=min(len(findings), max_findings),
        truncated=len(findings) > max_findings,
        by_rule=by_rule,
        findings=findings[:max_findings],
    )


# ---------------------------------------------------------------------------
# Обёртки для агента (CrewAI импортируется только здесь)
# ---------------------------------------------------------------------------


def crewai_tools(s: AISettings | None = None) -> list:
    """Три инструмента для Agent(tools=...). Настройки по умолчанию — из .env."""
    from crewai.tools import tool

    s = s or AISettings()

    @tool("read_file")
    def read_file_tool(path: str, start_line: int = 1, max_lines: int = 200) -> str:
        """Возвращает фрагмент текстового файла из репозитория бэкенда с номерами строк.
        Вызывай, когда уже знаешь путь к файлу — из ответа search_codebase или run_linter.
        Длинный файл читай частями через start_line.

        Args:
            path: путь к файлу относительно корня репозитория, прямые слэши.
            start_line: номер первой строки, от 1.
            max_lines: сколько строк вернуть, от 1 до 400.

        Returns:
            JSON-строка. Успех: {"status": "ok", "path", "start_line", "end_line",
            "total_lines", "truncated", "content"}. Ошибка: {"status": "error", "message", "hint"}.
        """
        return read_file(path, s, start_line=start_line, max_lines=max_lines)

    @tool("search_codebase")
    def search_codebase_tool(
        query: str, kind: str = "text", path: str = ".", path_glob: str = "*.py", max_results: int = 20
    ) -> str:
        """Ищет в файлах репозитория бэкенда. kind="text" — точная подстрока: где имя
        используется. kind="symbol" — где определена функция или класс с этим именем
        (только .py). Ищи имя целиком, а не общие слова языка. По умолчанию ищет по всему
        репозиторию: сужай path, только если видел этот каталог в ответе инструмента.

        Args:
            query: для text — от 3 до 100 символов; для symbol — одно имя Python.
            kind: text или symbol.
            path: подкаталог или файл относительно корня репозитория; оставь ".", если не знаешь,
                какие каталоги есть.
            path_glob: шаблон имени файла без слэшей; оставь "*.py", если не знаешь точное имя файла.
            max_results: от 1 до 50.

        Returns:
            JSON-строка. Успех: {"status": "ok", "total_matches", "returned", "truncated",
            "matches": [{"path", "line", ...}]}. Ошибка: {"status": "error", "message", "hint"}.
        """
        return search_codebase(query, s, kind=kind, path=path, path_glob=path_glob, max_results=max_results)

    @tool("run_linter")
    def run_linter_tool(path: str, max_findings: int = 30) -> str:
        """Запускает линтер ruff без исправлений на файле или каталоге репозитория бэкенда
        и возвращает замечания. Вызывай, чтобы проверить код перед ревью. Если ответ
        status=error, результат проверки неизвестен: не сообщай, что замечаний нет.

        Args:
            path: существующий файл или каталог относительно корня репозитория; "." — весь репозиторий.
            max_findings: сколько замечаний вернуть, от 1 до 100.

        Returns:
            JSON-строка. Успех: {"status": "ok", "total_findings", "by_rule", "findings":
            [{"path", "line", "rule", "message"}]}. Ошибка: {"status": "error", "message", "hint"}.
        """
        return run_linter(path, s, max_findings=max_findings)

    return [read_file_tool, search_codebase_tool, run_linter_tool]
