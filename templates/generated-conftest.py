"""Настройка pytest для тестов из generated/: приложение бэкенда импортируется без правки бэкенда.

Каркас практики 4. Копируется в репозиторий помощника:

    cp <клон курса>/templates/generated-conftest.py generated/conftest.py

Запуск сгенерированных тестов — человек, из корня помощника, с активированным
окружением помощника (одинаково в Git Bash и PowerShell):

    python -m pytest generated -q

pytest загружает этот файл раньше, чем собирает тесты каталога generated/. Поэтому
всё ниже выполняется до строки «from main import app» в модуле теста:

1. Корень бэкенда (AI_REPO_ROOT из .env помощника) — в начало sys.path: тест
   импортирует main или app.main так же, как из корня бэкенда.
2. DATABASE_URL — недоступный адрес, если переменная не задана в окружении. С недели 8
   «Конфигурирования» бэкенд проверяет настройки при импорте и без DATABASE_URL
   не импортируется. База не поднимается: тест не выбирает поведение, которому
   нужна работающая база. Переменная окружения важнее значения из .env бэкенда
   (и у pydantic-settings, и у load_dotenv()), поэтому адрес из .env не подставится.
   Требует бэкенд при импорте и другие переменные, которых нет в его .env, —
   допишите рядом такую же строку: os.environ.setdefault("<ИМЯ>", "test").
3. Текущий каталог — корень бэкенда, как при его обычном запуске: настройки бэкенда
   читают .env бэкенда, а не .env помощника (иначе класс настроек без extra="ignore"
   падает на чужих ключах AI_REPO_ROOT, LLM_PROVIDER, …).

Набор тестов помощника (tests/) этот файл не затрагивает: в pytest.ini помощника
testpaths = tests, и python -m pytest -q каталог generated/ не собирает.
"""

import os
import sys
from pathlib import Path

from ai.config import settings

BACKEND_ROOT = Path(settings.ai_repo_root).resolve()

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Порт 1 на своей машине: соединение сразу отклоняется, тест не ждёт сеть.
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@127.0.0.1:1/db")
# Другие обязательные переменные бэкенда, которых нет в его .env, — здесь же, например:
# os.environ.setdefault("SECRET_KEY", "test")

os.chdir(BACKEND_ROOT)  # .env бэкенда, а не помощника: как при запуске из корня бэкенда
