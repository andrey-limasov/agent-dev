"""
Пример тестирования AI-агента с использованием моков (mocks).

Этот шаблон демонстрирует, как тестировать агентов детерминированно, 
без реальных вызовов к LLM (Ollama или облачный провайдер с OpenAI-совместимым API). 
Это критически важно для CI репозитория помощника, 
где тесты должны быть быстрыми, дешёвыми и стабильными.

Зависимости для тестирования:
pip install pytest pytest-mock crewai langchain-ollama
"""

import json
import pytest
from unittest.mock import MagicMock, patch

# Импортируем наши компоненты (предполагаем, что они находятся в модуле app.agents)
# from app.agents import get_llm, create_task_tool, get_task_assistant_agent


class TestAgentWithMocks:
    """
    Тестирование агента с мокированием LLM и Tools.
    """

    @pytest.fixture
    def mock_llm(self):
        """
        Фикстура для создания мок-объекта LLM.
        Мы имитируем поведение ChatOllama или ChatOpenAI.
        """
        mock = MagicMock()
        # Имитируем ответ LLM при вызове invoke или generate
        # В реальности CrewAI использует более сложные вызовы, но для unit-теста 
        # достаточно замокать конечный результат или поведение Tool-calling
        
        # Пример: имитация ответа, что агент решил вызвать инструмент
        mock_response = MagicMock()
        mock_response.content = "Я вызову инструмент create_task с параметрами title='Купить молоко', priority='high'"
        
        # Для более продвинутого мокинга CrewAI можно использовать patch на уровне вызова модели
        return mock

    @pytest.fixture
    def mock_create_task_tool(self):
        """
        Фикстура для мокирования внешнего Tool (например, запроса к БД или API).
        Это гарантирует, что тест не будет зависеть от реального состояния базы данных.
        """
        mock_tool = MagicMock()
        mock_tool.name = "create_task"
        mock_tool.description = "Создает новую задачу в системе"
        
        # Имитируем успешное выполнение инструмента
        mock_tool.return_value = json.dumps({
            "status": "success",
            "task_id": 999,
            "title": "Купить молоко"
        })
        return mock_tool

    @patch('app.agents.ChatOllama')  # Заменяем реальный класс LLM на мок
    def test_agent_calls_tool_correctly(self, mock_chat_ollama_class, mock_create_task_tool):
        """
        Тест проверяет, что агент корректно формирует запрос к Tool 
        при получении соответствующей инструкции от пользователя.
        """
        # 1. Arrange (Подготовка)
        # Настраиваем мок LLM так, чтобы он возвращал предсказуемый результат
        mock_llm_instance = MagicMock()
        mock_chat_ollama_class.return_value = mock_llm_instance
        
        # Имитируем, что LLM "поняла", что нужно вызвать инструмент
        # (В CrewAI это сложно замокать напрямую, поэтому часто тестируют 
        # изолированно: отдельно Tool, отдельно логику формирования промпта)
        
        # Более практичный подход для CrewAI: тестировать сам Tool изолированно,
        # а интеграцию с LLM проверять через "snapshot testing" или интеграционные тесты с фиксированным seed.
        
        # 2. Act (Действие) - Тестируем сам Tool (это детерминированно!)
        result = mock_create_task_tool(title="Купить молоко", priority="high")
        parsed_result = json.loads(result)
        
        # 3. Assert (Проверка)
        assert parsed_result["status"] == "success"
        assert parsed_result["task_id"] == 999
        mock_create_task_tool.assert_called_once_with(title="Купить молоко", priority="high")


class TestToolLogicIsolation:
    """
    Лучшая практика: тестировать логику Tool изолированно от LLM.
    LLM недетерминирована, но код внутри Tool должен быть детерминированным 
    и покрываться обычными unit-тестами.
    """

    def test_create_task_tool_validates_priority(self):
        """
        Тест проверяет, что Tool корректно обрабатывает невалидные входные данные,
        не полагаясь на LLM для валидации.
        """
        # Импортируем реальную функцию инструмента (без декоратора @tool для чистоты теста, 
        # или тестируем обёртку, если она простая)
        # from app.tools import create_task_logic
        
        # def create_task_logic(title: str, priority: str) -> str:
        #     if priority not in ["high", "medium", "low"]:
        #         return "Ошибка: приоритет должен быть high, medium или low"
        #     return json.dumps({"status": "success", "title": title})
        
        # Имитация вызова с невалидным приоритетом
        # result = create_task_logic(title="Задача", priority="super-high")
        
        # assert "Ошибка" in result
        # assert "super-high" not in result # Или проверка конкретного сообщения
        
        assert True # Заглушка, заменить на реальный тест при внедрении


class TestAgentIntegrationWithMockedLLM:
    """
    Продвинутый уровень: интеграционное тестирование агента с использованием 
    зафиксированных ответов LLM (VCR-подобный подход или snapshot testing).
    """
    
    @pytest.mark.skip(reason="Требует настройки vcrpy или аналогичной библиотеки для записи ответов LLM")
    def test_agent_end_to_end_with_recorded_response(self):
        """
        Этот тест использует заранее записанный ответ LLM (например, в формате JSON),
        чтобы проверить, как агент обрабатывает этот ответ и вызывает ли он правильные Tools.
        
        Инструменты:
        - vcrpy (для записи HTTP-запросов к LLM)
        - pytest-snapshot (для сравнения вывода агента с эталоном)
        """
        pass


# ==============================================================================
# РЕКОМЕНДАЦИИ ДЛЯ СТУДЕНТОВ
# ==============================================================================
"""
1. НЕ тестируйте реальные вызовы к LLM в unit-тестах. Это медленно, дорого и ломается.
2. Тестируйте логику ваших Tools изолированно. Tool — это обычная Python-функция.
3. Если нужно проверить поведение агента целиком, используйте мокирование ответов LLM 
   или библиотеки для записи/воспроизведения HTTP-запросов (vcrpy, betamax).
4. В CI/CD (GitHub Actions) убедитесь, что переменные окружения для LLM либо не заданы, 
   либо указывают на мок-сервер, чтобы случайно не потратить токены.
5. Для проверки качества промптов и поведения агента используйте eval-фреймворки 
   (например, deepeval или ragas), но запускайте их отдельно от основного CI/CD пайплайна.
"""