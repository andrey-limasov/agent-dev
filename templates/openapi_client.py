"""Tool чтения OpenAPI-схемы работающего бэкенда: только GET <адрес стенда>/openapi.json.

Каркас практики 5. Копируется в репозиторий помощника:

    cp <клон курса>/templates/openapi_client.py ai/tools/openapi_client.py

Что готово: запрос только одного метода и одного пути, адрес — из настройки
ai_backend_url (AI_BACKEND_URL в .env), у Tool нет аргументов URL и метода: агенту
нечем попросить другой адрес. Таймауты и повтор — только для этого запроса; повторы
вызовов LLM и переход на запасную модель — неделя 12. Ошибка возвращается через _fail,
как у всех Tools курса: агент получает сообщение, а не исключение.

Что получает агент — сводка, а не файл схемы: метод, путь, параметры, поля тела запроса,
коды ответов. Текстовых описаний (description, summary) и JSON раздела components
в сводке нет: схема — недоверенный контент, её текст стал бы текстом промпта.
Сводка длиннее MAX_SUMMARY_CHARS обрезается целыми операциями с пометкой truncated,
как у read_file. Сверка метода и пути в ai/crew_result.py идёт по полной схеме из
fetch_schema, поэтому обрезка на неё не влияет.

Что может поменять команда — значения констант и тексты ошибок по разделу 4 своего
docs/result-contract.md. Состав сводки — по решению команды, description в неё не возвращать.

Внутренние функции получают настройки явным аргументом s, как в code_tools.py.
Аргумент transport нужен только тестам: туда передаётся httpx.MockTransport, сети нет.
CrewAI импортируется только внутри crewai_tools(): тесты не загружают CrewAI.
"""

from __future__ import annotations

import json
import time

import httpx

from ai.config import AISettings
from ai.tools.code_tools import _fail, _ok

SCHEMA_PATH = "/openapi.json"  # единственный путь, который читает помощник
CONNECT_TIMEOUT_S = 5.0  # подключение; намного меньше одного вызова LLM
READ_TIMEOUT_S = 10.0  # ожидание ответа
MAX_ATTEMPTS = 2  # первая попытка и один повтор: приложение могло ещё запускаться
RETRY_PAUSE_S = 1.0  # пауза перед повтором
MAX_SUMMARY_CHARS = 6000  # потолок сводки: у Ollama на ноутбуке контекст 4096 токенов
HTTP_METHODS = ("get", "post", "put", "patch", "delete")  # методы контракта результата


def fetch_schema(s: AISettings, transport: httpx.BaseTransport | None = None) -> tuple[dict | None, str | None]:
    """Полная схема со стенда -> (схема, None) или (None, JSON ошибки)."""
    url = s.ai_backend_url.rstrip("/") + SCHEMA_PATH
    timeout = httpx.Timeout(READ_TIMEOUT_S, connect=CONNECT_TIMEOUT_S)
    error = ""
    with httpx.Client(timeout=timeout, transport=transport, trust_env=False) as client:  # без прокси окружения
        for attempt in range(1, MAX_ATTEMPTS + 1):
            if attempt > 1:
                time.sleep(RETRY_PAUSE_S)
            try:
                response = client.get(url)
            except (httpx.InvalidURL, httpx.UnsupportedProtocol):
                return None, _fail("адрес стенда в AI_BACKEND_URL неверный: нужен вид http://127.0.0.1:8000")
            except httpx.ReadTimeout:
                error = f"стенд не ответил за {READ_TIMEOUT_S:g} с: схема не получена"
                continue
            except httpx.TransportError:  # отказ в подключении, таймаут подключения, обрыв
                error = "стенд не отвечает: схема не получена; стенд поднимает человек"
                continue
            if response.status_code == 404:
                return None, _fail("схема отключена: нужен APP_ENV=dev на стенде")
            if response.status_code >= 500:
                error = f"стенд ответил {response.status_code}: схема не получена"
                continue
            if response.status_code != 200:
                return None, _fail(f"стенд ответил {response.status_code}: схема не получена")
            try:
                schema = response.json()
            except (ValueError, RecursionError):
                return None, _fail("по адресу схемы ответ не JSON: проверьте порт")
            if not isinstance(schema, dict) or not isinstance(schema.get("paths"), dict):
                return None, _fail("по адресу схемы не OpenAPI-схема: проверьте порт")
            return schema, None
    return None, _fail(error)


def _resolve(node: object, schema: dict) -> dict:
    """Узел схемы; ссылка $ref внутри документа заменяется узлом, на который указывает."""
    if not isinstance(node, dict):
        return {}
    ref = node.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return node
    current: object = schema
    for part in ref[2:].split("/"):
        current = current.get(part) if isinstance(current, dict) else None
    return current if isinstance(current, dict) else {}


def _type_name(node: object) -> str:
    """Короткое имя типа: string, array[string], string|null; вложенная ссылка — имя модели."""
    if not isinstance(node, dict):
        return "any"
    if isinstance(node.get("$ref"), str):
        return node["$ref"].rsplit("/", 1)[-1]
    variants = node.get("anyOf") or node.get("oneOf")
    if isinstance(variants, list):
        return "|".join(_type_name(item) for item in variants)
    if node.get("type") == "array":
        return f"array[{_type_name(node.get('items'))}]"
    return str(node.get("type", "any"))


def _parameters(path_item: dict, operation: dict, schema: dict) -> list[dict]:
    result = []
    for raw in [*path_item.get("parameters", []), *operation.get("parameters", [])]:
        item = _resolve(raw, schema)
        result.append(
            {
                "name": item.get("name", ""),
                "in": item.get("in", ""),
                "required": bool(item.get("required", False)),
                "type": _type_name(item.get("schema")),
            }
        )
    return result


def _request_body(operation: dict, schema: dict) -> dict | None:
    if "requestBody" not in operation:
        return None
    body = _resolve(operation["requestBody"], schema)
    content = body.get("content") if isinstance(body.get("content"), dict) else {}
    media = content.get("application/json") or next(iter(content.values()), {})
    model = _resolve(media.get("schema") if isinstance(media, dict) else None, schema)
    required = model.get("required", [])
    properties = model.get("properties") if isinstance(model.get("properties"), dict) else {}
    return {
        "required": bool(body.get("required", False)),
        "fields": [
            {"name": name, "type": _type_name(node), "required": name in required}
            for name, node in properties.items()
        ],
    }


def summarize_schema(schema: dict, max_chars: int = MAX_SUMMARY_CHARS) -> dict:
    """Сводка для агента: операции по порядку путей, без текстов описаний."""
    operations = []
    for path, path_item in sorted(schema.get("paths", {}).items()):
        if not isinstance(path_item, dict):
            continue
        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if isinstance(operation, dict):
                operations.append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "parameters": _parameters(path_item, operation, schema),
                        "request_body": _request_body(operation, schema),
                        "responses": sorted(str(code) for code in operation.get("responses", {})),
                    }
                )
    kept, size = [], len(json.dumps({"total_operations": len(operations), "returned": 0, "truncated": True}))
    for item in operations:
        size += len(json.dumps(item, ensure_ascii=False)) + 2
        if size > max_chars:
            break  # целыми операциями: JSON ответа не рвётся
        kept.append(item)
    return {
        "total_operations": len(operations),
        "returned": len(kept),
        "truncated": len(kept) < len(operations),
        "operations": kept,
    }


def get_openapi_schema(s: AISettings, transport: httpx.BaseTransport | None = None) -> str:
    """Ответ Tool: сводка схемы стенда или ошибка в едином формате."""
    schema, err = fetch_schema(s, transport=transport)
    if err:
        return err
    try:
        return _ok(**summarize_schema(schema))
    except (AttributeError, TypeError, ValueError, RecursionError):
        return _fail("схему не удалось разобрать: проверьте, что по адресу стенда отвечает нужное приложение")


# ---------------------------------------------------------------------------
# Обёртка для агента (CrewAI импортируется только здесь)
# ---------------------------------------------------------------------------


def crewai_tools(s: AISettings | None = None) -> list:
    """Инструмент get_openapi_schema для Agent(tools=...). Настройки по умолчанию — из .env."""
    from crewai.tools import tool

    s = s or AISettings()

    @tool("get_openapi_schema")
    def get_openapi_schema_tool() -> str:
        """Возвращает сводку OpenAPI-схемы работающего бэкенда: какие методы и пути есть в API,
        их параметры, поля тела запроса и коды ответов. Вызывай без аргументов, первым шагом:
        адрес задан в настройках. Статус и тело ответа для теста бери из кода, а не из схемы.

        Returns:
            JSON-строка. Успех: {"status": "ok", "total_operations", "returned", "truncated",
            "operations": [{"method", "path", "parameters", "request_body", "responses"}]}.
            Ошибка: {"status": "error", "message"}.
        """
        return get_openapi_schema(s)

    return [get_openapi_schema_tool]
