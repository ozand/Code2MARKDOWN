"""
Утилиты и вспомогательные классы для авторизации AI агентов
"""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# ========================================
# PROXY MANAGEMENT UTILITIES
# ========================================


@dataclass
class ProxyInfo:
    """Информация о прокси сервере"""

    url: str
    username: str | None = None
    password: str | None = None
    geo_location: str | None = None
    last_used: datetime | None = None
    success_rate: float = 1.0
    response_time_ms: float = 0.0
    failure_count: int = 0
    max_failures: int = 3
    is_active: bool = True


class ProxyManager:
    """Менеджер прокси серверов с ротацией и мониторингом"""

    def __init__(self, proxy_list_file: str = "config/proxies.json"):
        self.proxy_list_file = Path(proxy_list_file)
        self.proxies: list[ProxyInfo] = []
        self.current_proxy_index = 0
        self.load_proxies()

    def load_proxies(self):
        """Загрузка списка прокси из файла"""
        if self.proxy_list_file.exists():
            with open(self.proxy_list_file) as f:
                proxy_data = json.load(f)

            for proxy in proxy_data:
                self.proxies.append(ProxyInfo(**proxy))
        else:
            # Создание примера файла прокси
            example_proxies = [
                {
                    "url": "http://proxy1.example.com:8080",
                    "username": "user1",
                    "password": "pass1",
                    "geo_location": "US",
                },
                {
                    "url": "socks5://proxy2.example.com:1080",
                    "username": "user2",
                    "password": "pass2",
                    "geo_location": "EU",
                },
            ]

            self.proxy_list_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.proxy_list_file, "w") as f:
                json.dump(example_proxies, f, indent=2)

    def get_next_proxy(self, geo_preference: str = None) -> ProxyInfo | None:
        """Получение следующего доступного прокси"""
        active_proxies = [p for p in self.proxies if p.is_active]

        if not active_proxies:
            return None

        # Фильтрация по географии если указано
        if geo_preference:
            geo_proxies = [p for p in active_proxies if p.geo_location == geo_preference]
            if geo_proxies:
                active_proxies = geo_proxies

        # Выбор прокси с наилучшим success_rate
        best_proxy = max(active_proxies, key=lambda p: p.success_rate)

        return best_proxy

    def mark_proxy_failed(self, proxy: ProxyInfo):
        """Отметка прокси как неудачный"""
        proxy.failure_count += 1
        proxy.success_rate = max(0.1, proxy.success_rate - 0.1)

        if proxy.failure_count >= proxy.max_failures:
            proxy.is_active = False
            logging.warning(f"Proxy {proxy.url} marked as inactive due to failures")

    def mark_proxy_success(self, proxy: ProxyInfo, response_time_ms: float):
        """Отметка успешного использования прокси"""
        proxy.last_used = datetime.now()
        proxy.response_time_ms = response_time_ms
        proxy.success_rate = min(1.0, proxy.success_rate + 0.05)
        proxy.failure_count = max(0, proxy.failure_count - 1)

    async def test_proxy(self, proxy: ProxyInfo) -> bool:
        """Тестирование прокси"""
        try:
            import aiohttp

            proxy_url = proxy.url
            if proxy.username and proxy.password:
                # Добавление аутентификации в URL
                protocol = proxy_url.split("://")[0]
                host_port = proxy_url.split("://")[1]
                proxy_url = f"{protocol}://{proxy.username}:{proxy.password}@{host_port}"

            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        response_time = (time.time() - start_time) * 1000
                        self.mark_proxy_success(proxy, response_time)
                        return True
                    else:
                        self.mark_proxy_failed(proxy)
                        return False

        except Exception as e:
            logging.error(f"Proxy test failed for {proxy.url}: {e}")
            self.mark_proxy_failed(proxy)
            return False


# ========================================
# CAPTCHA SOLVING UTILITIES
# ========================================


class CaptchaSolver:
    """Базовый класс для решения CAPTCHA"""

    def __init__(self):
        self.success_rate = 0.0
        self.average_solve_time = 0.0

    async def solve(self, captcha_image: bytes, captcha_type: str) -> str | None:
        """Решение CAPTCHA (базовая реализация)"""
        raise NotImplementedError("Subclasses must implement solve method")


class MockCaptchaSolver(CaptchaSolver):
    """Mock solver для тестирования"""

    async def solve(self, captcha_image: bytes, captcha_type: str) -> str | None:
        """Имитация решения CAPTCHA"""
        await asyncio.sleep(random.uniform(2, 8))  # Имитация времени решения

        # Имитируем разный success rate для разных типов
        success_rates = {
            "text": 0.95,
            "image_selection": 0.85,
            "recaptcha_v2": 0.75,
            "audio": 0.60,
        }

        success_rate = success_rates.get(captcha_type, 0.7)

        if random.random() < success_rate:
            return f"solved_{captcha_type}_{random.randint(1000, 9999)}"
        else:
            return None


# ========================================
# RATE LIMITING UTILITIES
# ========================================


class TokenBucket:
    """Реализация алгоритма Token Bucket для rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Попытка потребить токены"""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Пополнение токенов"""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def time_until_token(self) -> float:
        """Время до появления следующего токена"""
        if self.tokens >= 1:
            return 0.0
        return (1 - self.tokens) / self.refill_rate


class RateLimiter:
    """Продвинутый rate limiter с поддержкой разных эндпоинтов"""

    def __init__(self):
        self.buckets: dict[str, TokenBucket] = {}
        self.global_bucket = TokenBucket(capacity=100, refill_rate=1.0)

    def add_endpoint(self, endpoint: str, capacity: int, refill_rate: float):
        """Добавление эндпоинта с индивидуальными лимитами"""
        self.buckets[endpoint] = TokenBucket(capacity, refill_rate)

    async def acquire(self, endpoint: str, tokens: int = 1) -> bool:
        """Получение разрешения на выполнение запроса"""
        # Проверка глобального лимита
        if not self.global_bucket.consume(tokens):
            wait_time = self.global_bucket.time_until_token()
            await asyncio.sleep(wait_time)

        # Проверка лимита эндпоинта
        if endpoint in self.buckets:
            bucket = self.buckets[endpoint]
            if not bucket.consume(tokens):
                wait_time = bucket.time_until_token()
                await asyncio.sleep(wait_time)
                return await self.acquire(endpoint, tokens)

        return True


# ========================================
# MONITORING AND METRICS UTILITIES
# ========================================


@dataclass
class AuthMetrics:
    """Метрики авторизации"""

    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    average_response_time_ms: float = 0.0
    last_success_time: datetime | None = None
    last_failure_time: datetime | None = None
    success_rate_1h: float = 0.0
    success_rate_24h: float = 0.0


class MetricsCollector:
    """Сборщик метрик для мониторинга"""

    def __init__(self):
        self.metrics: dict[str, AuthMetrics] = {}
        self.raw_events: list[dict] = []
        self.max_events = 10000

    def record_auth_attempt(
        self, service: str, success: bool, response_time_ms: float, error: str = None
    ):
        """Запись попытки авторизации"""
        if service not in self.metrics:
            self.metrics[service] = AuthMetrics()

        metrics = self.metrics[service]
        metrics.total_attempts += 1

        if success:
            metrics.successful_attempts += 1
            metrics.last_success_time = datetime.now()
        else:
            metrics.failed_attempts += 1
            metrics.last_failure_time = datetime.now()

        # Обновление среднего времени ответа
        metrics.average_response_time_ms = (
            metrics.average_response_time_ms * (metrics.total_attempts - 1)
            + response_time_ms
        ) / metrics.total_attempts

        # Запись события
        event = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "success": success,
            "response_time_ms": response_time_ms,
            "error": error,
        }

        self.raw_events.append(event)

        # Ограничение размера буфера событий
        if len(self.raw_events) > self.max_events:
            self.raw_events = self.raw_events[-self.max_events :]

        # Обновление скользящих метрик
        self._update_sliding_metrics(service)

    def _update_sliding_metrics(self, service: str):
        """Обновление скользящих метрик"""
        now = datetime.now()

        # Фильтрация событий за последний час
        hour_ago = now - timedelta(hours=1)
        hour_events = [
            e
            for e in self.raw_events
            if e["service"] == service
            and datetime.fromisoformat(e["timestamp"]) > hour_ago
        ]

        if hour_events:
            success_count = sum(1 for e in hour_events if e["success"])
            self.metrics[service].success_rate_1h = success_count / len(hour_events)

        # Фильтрация событий за последние 24 часа
        day_ago = now - timedelta(hours=24)
        day_events = [
            e
            for e in self.raw_events
            if e["service"] == service
            and datetime.fromisoformat(e["timestamp"]) > day_ago
        ]

        if day_events:
            success_count = sum(1 for e in day_events if e["success"])
            self.metrics[service].success_rate_24h = success_count / len(day_events)

    def get_metrics(self, service: str = None) -> dict[str, AuthMetrics]:
        """Получение метрик"""
        if service:
            return {service: self.metrics.get(service, AuthMetrics())}
        return self.metrics.copy()

    def export_metrics_prometheus(self) -> str:
        """Экспорт метрик в формате Prometheus"""
        lines = []

        for service, metrics in self.metrics.items():
            service_label = f'service="{service}"'

            lines.append(
                f"auth_total_attempts{{{service_label}}} {metrics.total_attempts}"
            )
            lines.append(
                f"auth_successful_attempts{{{service_label}}} {metrics.successful_attempts}"
            )
            lines.append(
                f"auth_failed_attempts{{{service_label}}} {metrics.failed_attempts}"
            )
            lines.append(
                f"auth_success_rate_1h{{{service_label}}} {metrics.success_rate_1h}"
            )
            lines.append(
                f"auth_success_rate_24h{{{service_label}}} {metrics.success_rate_24h}"
            )
            lines.append(
                f"auth_avg_response_time_ms{{{service_label}}} {metrics.average_response_time_ms}"
            )

        return "\\n".join(lines)


# ========================================
# CONFIGURATION MANAGEMENT UTILITIES
# ========================================


class ConfigManager:
    """Менеджер конфигурации с поддержкой reload"""

    def __init__(self, config_file: str = "config/auth_config.json"):
        self.config_file = Path(config_file)
        self.config: dict[str, Any] = {}
        self.last_modified = 0
        self.watchers: list[callable] = []
        self.load_config()

    def load_config(self):
        """Загрузка конфигурации"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
            self.last_modified = self.config_file.stat().st_mtime
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Создание конфигурации по умолчанию"""
        default_config = {
            "session_management": {
                "session_timeout_hours": 24,
                "max_sessions_per_service": 5,
                "session_validation_interval_minutes": 30,
            },
            "behavior_simulation": {
                "typing_speed_wpm": 60,
                "mouse_movement_speed": 1.0,
                "thinking_pause_probability": 0.1,
                "error_correction_probability": 0.02,
            },
            "identity_rotation": {
                "rotation_interval_hours": 6,
                "max_identity_reuse": 5,
                "geo_consistency_required": True,
            },
            "rate_limiting": {
                "global_requests_per_minute": 60,
                "service_requests_per_minute": 10,
                "burst_size": 5,
            },
            "monitoring": {
                "metrics_retention_hours": 168,  # 7 days
                "alert_thresholds": {
                    "success_rate_warning": 0.85,
                    "success_rate_critical": 0.7,
                    "response_time_warning_ms": 5000,
                    "response_time_critical_ms": 10000,
                },
            },
        }

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        self.config = default_config

    def get(self, key_path: str, default=None):
        """Получение значения конфигурации по пути"""
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """Установка значения конфигурации"""
        keys = key_path.split(".")
        config = self.config

        # Навигация до родительского ключа
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Установка значения
        config[keys[-1]] = value

        # Сохранение конфигурации
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

        # Уведомление наблюдателей
        for watcher in self.watchers:
            try:
                watcher(key_path, value)
            except Exception as e:
                logging.error(f"Config watcher error: {e}")

    def add_watcher(self, callback: callable):
        """Добавление наблюдателя за изменениями конфигурации"""
        self.watchers.append(callback)

    async def watch_for_changes(self):
        """Отслеживание изменений файла конфигурации"""
        while True:
            try:
                if self.config_file.exists():
                    current_modified = self.config_file.stat().st_mtime
                    if current_modified > self.last_modified:
                        logging.info("Config file changed, reloading...")
                        self.load_config()

                        # Уведомление всех наблюдателей о reload
                        for watcher in self.watchers:
                            try:
                                watcher("__reload__", self.config)
                            except Exception as e:
                                logging.error(f"Config reload watcher error: {e}")

                await asyncio.sleep(5)  # Проверка каждые 5 секунд

            except Exception as e:
                logging.error(f"Config watching error: {e}")
                await asyncio.sleep(10)


# ========================================
# UTILITY FUNCTIONS
# ========================================


def generate_realistic_user_agent(
    browser: str = "chrome", platform: str = "windows"
) -> str:
    """Генерация реалистичного User-Agent"""
    versions = {
        "chrome": ["108.0.5359.125", "109.0.5414.74", "110.0.5481.77", "111.0.5563.64"],
        "firefox": ["108.0", "109.0", "110.0", "111.0"],
        "safari": ["16.2", "16.3", "16.4", "16.5"],
        "edge": ["108.0.1462.54", "109.0.1518.52", "110.0.1587.41", "111.0.1661.41"],
    }

    platforms = {
        "windows": "Windows NT 10.0; Win64; x64",
        "macos": "Macintosh; Intel Mac OS X 10_15_7",
        "linux": "X11; Linux x86_64",
    }

    version = random.choice(versions.get(browser, versions["chrome"]))
    platform_string = platforms.get(platform, platforms["windows"])

    if browser == "chrome":
        return f"Mozilla/5.0 ({platform_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    elif browser == "firefox":
        return f"Mozilla/5.0 ({platform_string}; rv:{version}) Gecko/20100101 Firefox/{version}"
    elif browser == "safari":
        return f"Mozilla/5.0 ({platform_string}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
    elif browser == "edge":
        return f"Mozilla/5.0 ({platform_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}"

    return f"Mozilla/5.0 ({platform_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"


def calculate_text_reading_time(text: str, wpm: int = 200) -> float:
    """Расчет времени чтения текста"""
    word_count = len(text.split())
    return (word_count / wpm) * 60  # в секундах


def generate_human_delays(base_delay: float, variation_factor: float = 0.3) -> float:
    """Генерация человекоподобных задержек"""
    variation = base_delay * variation_factor
    return base_delay + random.uniform(-variation, variation)


def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Маскировка чувствительных данных для логирования"""
    patterns = {
        "email": r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
        "password": r'password["\']?\\s*[:=]\\s*["\']?([^"\'\\s]+)',
        "token": r'token["\']?\\s*[:=]\\s*["\']?([^"\'\\s]+)',
        "key": r'key["\']?\\s*[:=]\\s*["\']?([^"\'\\s]+)',
    }

    masked_data = data
    for pattern_name, pattern in patterns.items():
        masked_data = re.sub(
            pattern, f"{pattern_name}={mask_char * 8}", masked_data, flags=re.IGNORECASE
        )

    return masked_data


def validate_proxy_url(proxy_url: str) -> bool:
    """Валидация URL прокси"""
    proxy_pattern = r"^(http|https|socks4|socks5)://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)$"
    return bool(re.match(proxy_pattern, proxy_url))


def extract_domain_from_url(url: str) -> str:
    """Извлечение домена из URL"""
    pattern = r"https?://(?:www\.)?([^/]+)"
    match = re.search(pattern, url)
    return match.group(1) if match else url


def generate_session_id(prefix: str = "") -> str:
    """Генерация уникального ID сессии"""
    timestamp = int(time.time())
    random_part = random.randint(10000, 99999)
    hash_part = hashlib.md5(f"{timestamp}{random_part}".encode()).hexdigest()[:8]

    if prefix:
        return f"{prefix}_{timestamp}_{hash_part}"
    return f"{timestamp}_{hash_part}"


async def safe_sleep(duration: float, max_jitter: float = 0.1):
    """Безопасный sleep с добавлением jitter"""
    jitter = random.uniform(-max_jitter, max_jitter) * duration
    actual_duration = max(0, duration + jitter)
    await asyncio.sleep(actual_duration)


def create_backup_file(file_path: Path, max_backups: int = 5):
    """Создание резервной копии файла"""
    if not file_path.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".{timestamp}{file_path.suffix}.backup")

    # Копирование файла
    backup_path.write_bytes(file_path.read_bytes())

    # Очистка старых backup'ов
    backup_pattern = f"{file_path.stem}.*.backup"
    backup_files = list(file_path.parent.glob(backup_pattern))

    if len(backup_files) > max_backups:
        # Сортировка по времени модификации и удаление старых
        backup_files.sort(key=lambda x: x.stat().st_mtime)
        for old_backup in backup_files[:-max_backups]:
            old_backup.unlink()


# ========================================
# EXAMPLE USAGE
# ========================================


async def example_usage():
    """Пример использования утилит"""

    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    # Инициализация компонентов
    config = ConfigManager()
    metrics = MetricsCollector()
    rate_limiter = RateLimiter()
    proxy_manager = ProxyManager()

    # Настройка rate limiting
    rate_limiter.add_endpoint("google_auth", capacity=10, refill_rate=0.1)

    # Симуляция использования
    for i in range(5):
        # Получение прокси
        proxy = proxy_manager.get_next_proxy("US")
        if proxy:
            print(f"Using proxy: {proxy.url}")

        # Ожидание rate limit
        await rate_limiter.acquire("google_auth")

        # Симуляция запроса
        start_time = time.time()
        await safe_sleep(random.uniform(1, 3))
        response_time = (time.time() - start_time) * 1000

        # Запись метрик
        success = random.random() > 0.2  # 80% success rate
        metrics.record_auth_attempt("notebooklm", success, response_time)

        if proxy:
            if success:
                proxy_manager.mark_proxy_success(proxy, response_time)
            else:
                proxy_manager.mark_proxy_failed(proxy)

        print(
            f"Request {i+1}: {'SUCCESS' if success else 'FAILED'} ({response_time:.1f}ms)"
        )

    # Вывод метрик
    service_metrics = metrics.get_metrics("notebooklm")["notebooklm"]
    print("\\nMetrics:")
    print(f"Total attempts: {service_metrics.total_attempts}")
    print(f"Success rate (1h): {service_metrics.success_rate_1h:.2%}")
    print(f"Average response time: {service_metrics.average_response_time_ms:.1f}ms")

    # Экспорт в Prometheus формат
    prometheus_metrics = metrics.export_metrics_prometheus()
    print(f"\\nPrometheus metrics:\\n{prometheus_metrics}")


if __name__ == "__main__":
    asyncio.run(example_usage())
