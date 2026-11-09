"""Точка входа помощника: python -m ai <сценарий>.

Каркас практики 5. Копируется в репозиторий помощника под именем ai/__main__.py:

    cp <клон курса>/templates/assistant-cli.py ai/__main__.py

Запуск из корня помощника:

    python -m ai generate-tests "Нужен тест: GET /version отвечает 200, в ответе version и team"

Коды возврата: 0 — итог получен и прошёл проверки; 1 — отказ (формат, проверка кодом,
время, схема не получена); 2 — ошибка вызова (нет сценария или задачи).

CrewAI импортируется внутри сценария: python -m ai без аргументов отвечает за секунды,
а тесты CLI не загружают CrewAI. Новый сценарий — функция и строка в SCENARIOS.
"""

import sys


def generate_tests(args: list[str]) -> int:
    """Сценарий generate-tests: Crew пишет тест в generated/ по задаче разработчика."""
    if len(args) != 1 or not args[0].strip():
        print('Укажите задачу разработчика: python -m ai generate-tests "Нужен тест: …"')
        return 2
    from ai.run_crew import main as run_crew

    return run_crew(["python -m ai generate-tests", args[0]])


SCENARIOS = {"generate-tests": generate_tests}


def _print_scenarios() -> None:
    print("Сценарии: " + ", ".join(sorted(SCENARIOS)))
    print('Запуск: python -m ai generate-tests "Нужен тест: …"')


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        _print_scenarios()
        return 2
    scenario = SCENARIOS.get(argv[1])
    if scenario is None:
        print(f"Неизвестный сценарий: {argv[1]}")
        _print_scenarios()
        return 2
    return scenario(argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
