## Основы. Что такое ИИ-агент?

*Цель: Понять разницу между генерацией текста и агентным действием, изучить паттерн ReAct.*

**На русском:**

1. [Что такое AI-агент и из каких основных частей он состоит](https://habr.com/ru/articles/951428/) — *Четкая, структурированная статья без воды. Разбирает 5 компонентов: LLM, инструменты, промпты, память, планирование.* 
2. [Базовый минимум. Часть 4: ИИ-агенты](https://habr.com/ru/articles/1013540/) — *Краткий обзор того, как агент анализирует задачу, формирует план и выбирает инструменты для достижения результата.* 

**На английском:**

3. [What is an AI Agent?](https://www.ibm.com/topics/ai-agents) (IBM) — *Классическое определение с разбором компонентов (Perception, Memory, Planning, Action).*
4. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Оригинальная статья, читать только введение) — *Фундаментальная работа, введшая паттерн "Рассуждай и действуй".*
5. [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) (Lilian Weng, OpenAI) — *Читать только раздел "LLM as the Agent’s Brain". Это фундаментальная работа, на которую ссылаются все современные фреймворки.*

---

## Инструменты и Function Calling или Как агент "трогает" мир

*Цель: Понять механику, с помощью которой агент выполняет код или обращается к API.*

**На русском:**

1. [Вызов функций с помощью LLM (Function Calling)](https://habr.com/ru/companies/mts_ai/articles/831220/) — *Статья от МТС AI, которая простым языком объясняет, как именно LLM получает "руки" для взаимодействия с внешним миром.* 

**На английском:**

2. [Function Calling with LLMs](https://www.promptingguide.ai/applications/function_calling) (Prompting Guide) — *Лучшее пошаговое визуальное объяснение того, как работает handshake между LLM и кодом.*
3. [Tool Calling, Explained](https://towardsdatascience.com/tool-calling-explained-how-ai-agents-decide-what-to-do-next/) (Towards Data Science) — *Отличная метафора: если инструменты — это "приложения", то function calling — это "рукопожатие" операционной системы.*

---

## Бесплатные курсы

*Цель: Возможность "потыкать" агент до очной пары.*

**Stepik (Русский язык):**

1. [Введение в разработку ИИ-агентов](https://stepik.org/course/272932/promo) — *Бесплатный. Идеален для нуля: от первого API-запроса до Structured Output. Именно то, что нужно перед воркшопом.*

**Coursera / DeepLearning.AI (Английский, режим Audit):**

2. [Agentic AI](https://www.deeplearning.ai/courses/agentic-ai) (DeepLearning.AI) — *Короткий, бесплатный курс, который фокусируется именно на концепциях, а не на хардкорном коде. Идеально для первого знакомства.*
3. [LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) — *Пройти только первый модуль "Model, Prompts, and Parsers", чтобы понять, как структурировать вывод.*
