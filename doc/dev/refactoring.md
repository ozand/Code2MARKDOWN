Отлично, код получен. Я внимательно изучил структуру и логику вашего приложения Code2MARKDOWN.

Приступаю к Фазе 1: Архитектурный анализ и рекомендации.

---

## 1. Executive Summary

Проект **Code2MARKDOWN** представляет собой функциональное Streamlit-приложение, решающее конкретную задачу: генерация документации из исходного кода на основе шаблонов. Приложение уже обладает ценными функциями, такими как интерактивный выбор файлов, система фильтрации и история запросов.

Текущая архитектура, однако, представляет собой **единый процедурный скрипт** (`app.py`), где смешаны логика отображения (UI), бизнес-логика и доступ к данным. Такой подход эффективен для быстрого прототипирования, но с ростом функциональности он создает сложности в поддержке, тестировании и дальнейшем развитии.

Данный анализ предлагает стратегию перехода к **многоуровневой архитектуре с фокусом на Предметно-Ориентированном Проектировании (Domain-Driven Design)**. Основная цель — выделить ключевые концепции вашего приложения (такие как "Запрос на генерацию", "Настройки фильтра") в явные, независимые и самодостаточные объекты домена. Это сделает код более чистым, модульным, понятным и готовым к будущим изменениям.

## 2. Current State ("As-Is") Architectural Analysis

Приложение построено вокруг одного основного файла `app.py`, который содержит более 1000 строк кода. Это классический пример архитектурного стиля "Script Transaction", где вся работа выполняется в одном большом потоке.

Я выделяю три ключевые архитектурные проблемы, которые стоит решить для обеспечения долгосрочного здоровья проекта:

* **Анемичная модель предметной области (Anemic Domain Model)**: Основные концепции приложения — "Запрос", "Фильтр", "Проект" — не представлены в виде полноценных классов с поведением. Вместо этого их данные разбросаны по примитивным типам (строки, словари, списки), а логика, которая должна принадлежать им, находится в глобальных функциях. Например, логика сохранения запроса в базу данных (`save_to_db`) оперирует набором простых параметров (`project_path`, `template_name`, `markdown_content`), а не единым объектом `GenerationRequest`.

* **Одержимость примитивами (Primitive Obsession)**: Фундаментальные понятия в коде представлены базовыми типами данных вместо того, чтобы быть обернутыми в специализированные классы.
    * `project_path` — это просто `string`.
    * `filter_settings` — это `dict`, который затем сериализуется в JSON `string` для записи в БД.
    * `max_file_size` — это `int`.
    Это приводит к тому, что валидация и связанное с этими понятиями поведение дублируются и размазываются по всему коду. Например, проверка корректности пути к проекту может потребоваться в нескольких местах.

* **Отсутствие инкапсуляции и смешение ответственности (Lack of Encapsulation / Low Cohesion)**: Файл `app.py` стал своего рода "божественным объектом", отвечающим за всё:
    * **UI-логика**: Вызовы `st.checkbox`, `st.button`, `st.expander`.
    * **Бизнес-логика**: Фильтрация файлов, построение дерева, применение шаблонов.
    * **Доступ к данным**: Прямые SQL-запросы к `sqlite3`.
    Такое смешение делает невозможным независимое изменение или тестирование одной части системы, не затрагивая остальные. Функции с большим количеством аргументов (например, `get_file_tree_structure` или `generate_markdown`) являются ярким симптомом этой проблемы.

## 3. Target Architecture ("To-Be") Vision

Я предлагаю эволюционно перейти к простой, но эффективной многоуровневой архитектуре. Это не потребует полной переписки, а скорее, реструктуризации существующего кода.


1.  **Presentation Layer (Уровень Представления)**
    * **Что это?** Ваш файл `app.py`.
    * **Ответственность:** Исключительно отрисовка UI и обработка действий пользователя. Он не должен содержать сложной бизнес-логики или прямых запросов к БД. Он будет вызывать сервисы из следующего уровня.
    * **Преимущество:** UI становится "тонким" и легко заменяемым. Логика отображения отделена от бизнес-правил.

2.  **Application Layer (Прикладной Уровень)**
    * **Что это?** Новый модуль, например `application/services.py`.
    * **Ответственность:** Оркестрация. Этот уровень будет содержать сервисы (например, `GenerationService`), которые принимают простые запросы от UI, используют объекты Домена для выполнения работы и возвращают результат. Например, `service.generate_documentation(path, template, filters)`.
    * **Преимущество:** Четко определяет варианты использования (use cases) вашего приложения.

3.  **Domain Layer (Уровень Предметной Области)**
    * **Что это?** Сердце вашего приложения. Новые модули, например `domain/request.py`, `domain/filters.py`.
    * **Ответственность:** Содержать бизнес-логику и состояние. Здесь будут жить классы, которые представляют ключевые концепции:
        * **Value Objects (Объекты-Значения):** Небольшие, неизменяемые объекты для представления простых понятий. Например, `FilePath`, `FileSize`, `Template`. Они инкапсулируют логику валидации (например, `FilePath` может проверить, существует ли путь).
        * **Entities (Сущности):** Объекты с уникальным идентификатором и жизненным циклом. Главный кандидат — `GenerationRequest`, у которого есть `id`.
        * **Aggregates (Агрегаты):** Кластеры из связанных объектов, которые рассматриваются как единое целое. `GenerationRequest` мог бы стать корнем агрегата, содержащего `FilterSettings`.
    * **Преимущество:** Бизнес-логика становится централизованной, явной и легко тестируемой. Код начинает "говорить" на языке предметной области.

4.  **Infrastructure Layer (Инфраструктурный Уровень)**
    * **Что это?** Новый модуль, например `infrastructure/database.py`.
    * **Ответственность:** Технические детали: работа с базой данных, файловой системой, внешними API. Этот уровень реализует интерфейсы, определенные на Прикладном или Доменном уровне. Например, класс `SqliteHistoryRepository` будет реализовывать интерфейс `IHistoryRepository` и содержать весь SQL-код.
    * **Преимущество:** Полное отделение бизнес-правил от технических деталей. Вы сможете легко заменить SQLite на другую БД, не меняя ни строчки в Доменном уровне.

## 4. Key Problems and Proposed Solutions

| Проблема | Пример в коде (`app.py`) | Предлагаемое DDD-решение | Преимущество |
| :--- | :--- | :--- | :--- |
| **Одержимость примитивами** | `project_path: str`, `filter_settings: dict`, `max_file_size: int` | Создать `Value Objects`: `class FilePath(str)`, `class FilterSettings`, `class FileSize`. | Самовалидирующиеся, переиспользуемые и выразительные типы. Устранение дублирования проверок. |
| **Анемичная модель** | Функция `save_to_db` принимает множество отдельных аргументов. | Создать `Entity` `class GenerationRequest`, который инкапсулирует все данные о запросе. | Логика и данные находятся вместе. Объект всегда находится в корректном состоянии. |
| **Смешение ответственности** | Функция `generate_markdown` одновременно читает файлы, применяет шаблон и сохраняет в БД. | Разделить логику: 1) UI вызывает `ApplicationService`. 2) Сервис использует `GenerationRequest` для создания контента. 3) Сервис использует `HistoryRepository` для сохранения. | Каждый компонент имеет одну причину для изменения. Упрощается тестирование и понимание. |
| **Разбросанная логика фильтрации** | Логика исключения файлов размазана по `get_file_tree_structure`. | Создать `Value Object` `class Filter` (или `FilterSpecification`), который содержит все правила и имеет один метод: `is_excluded(file_path: FilePath) -> bool`. | Централизация всех правил фильтрации в одном месте. Легко добавлять новые правила. |
| **Прямые SQL-запросы в UI-коде** | `sqlite3.connect(...)` и `cursor.execute(...)` вызываются прямо в `app.py`. | Создать интерфейс `IHistoryRepository` на прикладном уровне и его реализацию `SqliteHistoryRepository` на инфраструктурном. | Приложение зависит от абстракции, а не от конкретной реализации БД. |

## 5. Architectural Roadmap

Вот пошаговый, итеративный план по улучшению архитектуры. Каждый шаг приносит немедленную пользу и является основой для следующего.

1.  **Шаг 1: Внедрение Объектов-Значений (Value Objects).**
    * **Задача:** Начать с самого простого. Создайте класс `FilterSettings`, который заменит словарь `st.session_state.filter_settings`. Этот класс будет содержать все поля (`include_patterns`, `exclude_patterns`, `max_file_size`) и, возможно, методы для их валидации.
    * **Цель:** Сделать первый шаг к инкапсуляции. Уменьшить количество параметров, передаваемых в функции, объединив их в один объект.

2.  **Шаг 2: Создание первой Сущности (Entity) и Репозитория.**
    * **Задача:** Создайте класс `GenerationRequest`. Перенесите в него все поля, относящиеся к одному сеансу генерации (путь, шаблон, фильтры, контент, дата). Создайте в `infrastructure` модуль `history_repository.py` с классом `SqliteHistoryRepository`, который будет отвечать за сохранение и загрузку объектов `GenerationRequest`.
    * **Цель:** Отделить логику сохранения от бизнес-логики. Ваш основной код больше не будет "знать" о существовании SQLite.

3.  **Шаг 3: Выделение Прикладного Сервиса.**
    * **Задача:** Создайте `application/services.py` с классом `GenerationService`. Этот сервис в конструкторе будет принимать `history_repository`. Создайте в нем метод `generate_and_save_documentation(...)`, который будет содержать логику, ранее находившуюся в кнопке "Generate Markdown".
    * **Цель:** Сделать `app.py` тоньше. Логика обработки клика сведется к вызову одного метода сервиса.

4.  **Шаг 4: Рефакторинг логики обхода файлов.**
    * **Задача:** Реорганизовать сложную логику из `get_file_tree_structure` и `get_filtered_files_interactive`. Создайте Доменные объекты, такие как `ProjectTree`, `FileNode`, `DirectoryNode`. Логика определения, исключен ли файл, должна стать методом самого `FileNode`, который принимает объект `FilterSettings`.
    * **Цель:** Сделать сложную логику более объектно-ориентированной, понятной и тестируемой.

---

Отлично, приступаем к Фазе 2.

Здесь я возьму ключевые проблемы, которые мы определили, и продемонстрирую, как их можно решить на практике с помощью рефакторинга. Я покажу код в формате "До" и "После", чтобы наглядно проиллюстрировать преимущества предложенных изменений.

-----

### Проблема 1: Одержимость примитивами и разбросанные данные

**Проблема:** Настройки фильтров хранятся в словаре `st.session_state` и передаются в функции в виде отдельных, несвязанных переменных. Это затрудняет понимание и увеличивает риск ошибок при добавлении новых фильтров.

#### Код "До":

В `app.py` мы видим инициализацию словаря и вызов функции `generate_markdown` с россыпью аргументов.

```python
# app.py

# ... в районе строки 930
if 'filter_settings' not in st.session_state:
    st.session_state.filter_settings = {
        'include_patterns': ['.py', '.js', '.ts', '.jsx', '.tsx', '.md', '.txt', '.json', '.yml', '.yaml'],
        'exclude_patterns': ['node_modules', '__pycache__', '.git', 'venv', '.venv'],
        'max_file_size': 50,  # KB
        'selected_files': set(),
        'show_excluded': False
    }
    
# ... в районе строки 1115 (внутри кнопки "Generate Markdown")
if st.button("Generate Markdown", ...):
    # ...
    include_patterns = st.session_state.filter_settings['include_patterns']
    exclude_patterns = st.session_state.filter_settings['exclude_patterns']
    max_file_size = st.session_state.filter_settings['max_file_size']
    
    st.session_state.markdown_content = generate_markdown(
        project_path, 
        selected_template, 
        reference_url,
        selected_files=selected_files,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        max_file_size=max_file_size
    )
```

#### Код "После":

Мы создаем новый, самодостаточный класс `FilterSettings`, который инкапсулирует все данные и логику, связанную с фильтрацией.

**1. Создаем новый файл `domain/filters.py`:**

```python
# domain/filters.py
from dataclasses import dataclass, field
from typing import List, Set

@dataclass(frozen=True)
class FileSize:
    """ Value Object для размера файла в килобайтах. """
    kb: int

    def __post_init__(self):
        if self.kb <= 0:
            raise ValueError("Размер файла должен быть положительным числом.")

    @property
    def bytes(self) -> int:
        return self.kb * 1024

@dataclass(frozen=True)
class FilterSettings:
    """ Value Object, инкапсулирующий все настройки фильтрации. """
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size: FileSize = field(default_factory=lambda: FileSize(kb=50))
    show_excluded: bool = False
```

**2. Обновляем `app.py`:**

```python
# app.py

# Импортируем наши новые доменные объекты
from domain.filters import FilterSettings, FileSize

# ...

# Инициализация становится чище
if 'filter_settings' not in st.session_state:
    st.session_state.filter_settings = FilterSettings(
        include_patterns=['.py', '.js', '.ts', '.jsx', '.tsx', '.md', '.txt', '.json', '.yml', '.yaml'],
        exclude_patterns=['node_modules', '__pycache__', '.git', 'venv', '.venv'],
        max_file_size=FileSize(kb=50)
    )

# ...

# Сигнатура функции generate_markdown упрощается
def generate_markdown(project_path: str, template_name: str, reference_url: str, selected_files: set, filter_settings: FilterSettings):
    # ... (тело функции теперь использует filter_settings.include_patterns и т.д.)
    pass

# ...

# Вызов внутри кнопки "Generate Markdown" становится гораздо чище и безопаснее
if st.button("Generate Markdown", ...):
    # ...
    # Просто передаем один объект вместо набора переменных
    current_filters = st.session_state.filter_settings
    
    st.session_state.markdown_content = generate_markdown(
        project_path, 
        selected_template, 
        reference_url,
        selected_files=selected_files,
        filter_settings=current_filters  # <--- Передаем единый объект
    )
```

#### Объяснение изменений:

Мы создали два **Объекта-Значения (Value Objects)**: `FileSize` и `FilterSettings`.

1.  **Инкапсуляция:** Вся информация о фильтрах теперь сгруппирована в одном месте. Если в будущем появится новый параметр фильтра, нам нужно будет изменить только класс `FilterSettings`.
2.  **Выразительность и Безопасность:** Вместо `int` для размера файла мы используем `FileSize`. Этот класс не только делает код понятнее (`max_file_size.bytes`), но и содержит логику валидации (размер не может быть отрицательным). Это предотвращает появление некорректных данных в системе.
3.  **Упрощение API:** Сигнатура функции `generate_markdown` стала значительно короче и понятнее. Она ясно говорит: "Я принимаю настройки фильтра", а не "Я принимаю список для включения, список для исключения и максимальный размер".

-----

### Проблема 2: Анемичная модель и смешение ответственности (работа с БД)

**Проблема:** Функция `save_to_db` содержит "сырые" SQL-запросы и работает с набором примитивных типов. Логика сохранения данных тесно переплетена с основным кодом приложения, что затрудняет тестирование и смену СУБД в будущем.

#### Код "До":

```python
# app.py, в районе строки 60
def save_to_db(project_path, template_name, markdown_content, reference_url=None, file_count=0, filter_settings=None):
    conn = sqlite3.connect('code2markdown.db')
    cursor = conn.cursor()
    
    project_name = os.path.basename(os.path.abspath(project_path)) if project_path else "Unknown"
    filter_settings_json = json.dumps(filter_settings) if filter_settings else None
    
    cursor.execute('''
        INSERT INTO requests (project_path, template_name, markdown_content, reference_url, processed_at, file_count, filter_settings, project_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_path, template_name, markdown_content, reference_url, datetime.now(), file_count, filter_settings_json, project_name))
    conn.commit()
    conn.close()

# ... и вызов внутри generate_markdown
# app.py, в районе строки 277
def generate_markdown(...):
    # ... (логика генерации) ...
    
    save_to_db(project_path, template_name, markdown_content, reference_url, file_count, filter_settings_info)
    return markdown_content
```

#### Код "После":

Мы разделим эту логику на три части: **Сущность** (Entity), **Интерфейс Репозитория** (Repository Interface) и его **Реализацию** (Implementation).

**1. Создаем Сущность `GenerationRequest` в `domain/request.py`:**

```python
# domain/request.py
from datetime import datetime
from dataclasses import dataclass
from domain.filters import FilterSettings # Используем наш Value Object

@dataclass
class GenerationRequest:
    """ Entity, представляющая один запрос на генерацию документации. """
    id: int | None # У сущности есть ID
    project_path: str
    project_name: str
    template_name: str
    markdown_content: str
    filter_settings: FilterSettings
    file_count: int
    processed_at: datetime
    reference_url: str | None = None
```

**2. Создаем "контракт" (интерфейс) в `application/repository.py`:**

```python
# application/repository.py
from abc import ABC, abstractmethod
from typing import List
from domain.request import GenerationRequest

class IHistoryRepository(ABC):
    """ Абстрактный репозиторий для работы с историей запросов. """

    @abstractmethod
    def save(self, request: GenerationRequest) -> None:
        ...

    @abstractmethod
    def get_all(self) -> List[GenerationRequest]:
        ...
    
    @abstractmethod
    def delete(self, request_id: int) -> None:
        ...
```

**3. Создаем конкретную реализацию для SQLite в `infrastructure/database.py`:**

```python
# infrastructure/database.py
import sqlite3
import json
from application.repository import IHistoryRepository
from domain.request import GenerationRequest

class SqliteHistoryRepository(IHistoryRepository):
    """ Реализация репозитория для SQLite. """
    
    def __init__(self, db_path: str):
        self._db_path = db_path
        # Можно здесь же вызывать init_db()
        
    def save(self, request: GenerationRequest) -> None:
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        # Логика сериализации теперь внутри репозитория
        filter_settings_json = json.dumps(request.filter_settings.__dict__)
        
        cursor.execute('''
            INSERT INTO requests (...) VALUES (?, ?, ...)
        ''', (request.project_path, ..., filter_settings_json))
        
        conn.commit()
        conn.close()

    def get_all(self) -> List[GenerationRequest]:
        # ... здесь будет логика извлечения и преобразования данных в объекты GenerationRequest
        pass
    
    def delete(self, request_id: int) -> None:
        # ... логика удаления
        pass
```

**4. Обновляем код, который использует эту логику (например, Прикладной Сервис):**

```python
# application/services.py (новый файл)

from domain.request import GenerationRequest
from domain.filters import FilterSettings
from application.repository import IHistoryRepository

class GenerationService:
    def __init__(self, history_repo: IHistoryRepository):
        self._history_repo = history_repo

    def generate_and_save_documentation(self, project_path: str, template_name: str, filters: FilterSettings) -> str:
        # 1. Основная логика генерации markdown...
        markdown_content = "..." 
        file_count = 10 
        
        # 2. Создаем полноценный объект Сущности
        request_to_save = GenerationRequest(
            id=None, # БД присвоит ID
            project_path=project_path,
            project_name=os.path.basename(project_path),
            template_name=template_name,
            markdown_content=markdown_content,
            filter_settings=filters,
            file_count=file_count,
            processed_at=datetime.now()
        )
        
        # 3. Сохраняем через репозиторий, не зная о деталях БД
        self._history_repo.save(request_to_save)
        
        return markdown_content
```

#### Объяснение изменений:

1.  **Разделение Ответственности (Separation of Concerns):** Мы четко разделили код на уровни. `GenerationService` (прикладной уровень) ничего не знает про SQL. `SqliteHistoryRepository` (инфраструктурный уровень) ничего не знает о бизнес-логике. `GenerationRequest` (доменный уровень) ничего не знает ни о том, ни о другом.
2.  **Принцип Инверсии Зависимостей (Dependency Inversion):** Наш сервис зависит не от конкретной реализации `SqliteHistoryRepository`, а от абстракции `IHistoryRepository`. Это значит, что завтра мы можем написать `PostgresHistoryRepository`, передать его в сервис, и всё продолжит работать без изменения единой строки в `GenerationService`.
3.  **Тестируемость:** Теперь мы можем легко протестировать `GenerationService`, передав ему "фейковый" репозиторий (mock), который не будет обращаться к реальной базе данных. Это делает юнит-тесты быстрыми и надежными.
4.  **Богатая Модель:** Мы избавились от анемичной функции `save_to_db` и создали богатую сущность `GenerationRequest`, которая представляет собой полноценную концепцию в нашей системе.