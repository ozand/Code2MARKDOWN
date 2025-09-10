"""
Полные рабочие примеры реализации различных методов авторизации
для AI агентов с обходом защиты от ботов Google.
"""

import asyncio
import hashlib
import json
import logging
import random
import secrets
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet
from playwright.async_api import BrowserContext, Page, async_playwright

# ========================================
# 1. COMPLETE SESSION PERSISTENCE EXAMPLE
# ========================================


@dataclass
class SessionMetadata:
    """Метаданные сессии для валидации"""

    timestamp: str
    user_agent: str
    ip_address: str
    fingerprint_hash: str
    service: str
    expires_at: str


class AdvancedSessionManager:
    """Продвинутый менеджер сессий с шифрованием и валидацией"""

    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/session_manager.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    async def save_session(
        self, context: BrowserContext, service: str, user_id: str
    ) -> str:
        """Сохранение сессии с полными метаданными"""
        try:
            # Получение storage state
            storage_state = await context.storage_state()

            # Сбор метаданных
            page = await context.new_page()
            user_agent = await page.evaluate("navigator.userAgent")
            fingerprint = await self._collect_fingerprint(page)
            ip_address = await self._get_external_ip(page)
            await page.close()

            # Создание метаданных
            metadata = SessionMetadata(
                timestamp=datetime.now().isoformat(),
                user_agent=user_agent,
                ip_address=ip_address,
                fingerprint_hash=hashlib.sha256(
                    json.dumps(fingerprint).encode()
                ).hexdigest(),
                service=service,
                expires_at=(datetime.now() + timedelta(hours=24)).isoformat(),
            )

            # Подготовка данных для шифрования
            session_data = {
                "storage_state": storage_state,
                "metadata": asdict(metadata),
                "fingerprint": fingerprint,
            }

            # Шифрование и сохранение
            encrypted_data = self.cipher.encrypt(json.dumps(session_data).encode())
            session_id = f"{service}_{user_id}_{int(time.time())}"
            session_file = self.sessions_dir / f"{session_id}.enc"

            session_file.write_bytes(encrypted_data)

            self.logger.info(f"Session saved: {session_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            raise

    async def restore_session(self, session_id: str, context: BrowserContext) -> bool:
        """Восстановление и валидация сессии"""
        try:
            session_file = self.sessions_dir / f"{session_id}.enc"

            if not session_file.exists():
                self.logger.warning(f"Session file not found: {session_id}")
                return False

            # Расшифровка данных
            encrypted_data = session_file.read_bytes()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = json.loads(decrypted_data.decode())

            # Проверка срока действия
            metadata = SessionMetadata(**session_data["metadata"])
            if datetime.fromisoformat(metadata.expires_at) < datetime.now():
                self.logger.warning(f"Session expired: {session_id}")
                session_file.unlink()  # Удаляем просроченную сессию
                return False

            # Восстановление storage state
            await context.add_cookies(session_data["storage_state"]["cookies"])

            # Применение fingerprint
            await self._apply_fingerprint(context, session_data["fingerprint"])

            # Валидация сессии
            validation_result = await self._validate_session(context, metadata.service)

            if validation_result:
                self.logger.info(f"Session restored successfully: {session_id}")
                return True
            else:
                self.logger.warning(f"Session validation failed: {session_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to restore session {session_id}: {e}")
            return False

    async def _collect_fingerprint(self, page: Page) -> dict:
        """Сбор fingerprint данных"""
        fingerprint = await page.evaluate("""
        () => {
            return {
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth
                },
                navigator: {
                    platform: navigator.platform,
                    language: navigator.language,
                    languages: navigator.languages,
                    cookieEnabled: navigator.cookieEnabled,
                    doNotTrack: navigator.doNotTrack
                },
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                canvas: (() => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.textBaseline = 'top';
                    ctx.font = '14px Arial';
                    ctx.fillText('Fingerprint test', 2, 2);
                    return canvas.toDataURL();
                })(),
                webgl: (() => {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    return {
                        vendor: gl.getParameter(gl.VENDOR),
                        renderer: gl.getParameter(gl.RENDERER)
                    };
                })()
            };
        }
        """)
        return fingerprint

    async def _apply_fingerprint(self, context: BrowserContext, fingerprint: dict):
        """Применение fingerprint к контексту"""
        script = f"""
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fingerprint["navigator"]["platform"]}'
        }});
        
        Object.defineProperty(navigator, 'language', {{
            get: () => '{fingerprint["navigator"]["language"]}'
        }});
        
        Object.defineProperty(screen, 'width', {{
            get: () => {fingerprint["screen"]["width"]}
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: () => {fingerprint["screen"]["height"]}
        }});
        """

        await context.add_init_script(script)

    async def _get_external_ip(self, page: Page) -> str:
        """Получение внешнего IP адреса"""
        try:
            await page.goto("https://httpbin.org/ip", timeout=10000)
            content = await page.content()
            ip_data = json.loads(await page.locator("pre").inner_text())
            return ip_data.get("origin", "unknown")
        except:
            return "unknown"

    async def _validate_session(self, context: BrowserContext, service: str) -> bool:
        """Валидация сессии на целевом сервисе"""
        validation_urls = {
            "notebooklm": "https://notebooklm.google.com/",
            "gmail": "https://mail.google.com/",
            "drive": "https://drive.google.com/",
        }

        url = validation_urls.get(service)
        if not url:
            return False

        try:
            page = await context.new_page()
            await page.goto(url, timeout=30000)

            # Проверка успешной авторизации (специфично для каждого сервиса)
            if service == "notebooklm":
                await page.wait_for_selector('img[alt="NotebookLM Logo"]', timeout=10000)
            elif service == "gmail":
                await page.wait_for_selector('[data-testid="compose"]', timeout=10000)
            elif service == "drive":
                await page.wait_for_selector(
                    '[data-testid="create-button"]', timeout=10000
                )

            await page.close()
            return True

        except Exception as e:
            self.logger.warning(f"Session validation failed for {service}: {e}")
            return False


# ========================================
# 2. HUMAN BEHAVIOR SIMULATION EXAMPLE
# ========================================


class HumanBehaviorSimulator:
    """Продвинутая симуляция человеческого поведения"""

    def __init__(self):
        self.typing_profiles = self._load_typing_profiles()
        self.mouse_profiles = self._load_mouse_profiles()
        self.reading_profiles = self._load_reading_profiles()
        self.current_session_profile = self._generate_session_profile()

    def _load_typing_profiles(self) -> list[dict]:
        """Загрузка профилей печати"""
        return [
            {
                "name": "fast_typist",
                "wpm": 75,
                "error_rate": 0.01,
                "correction_speed": 0.8,
                "think_pause_probability": 0.05,
            },
            {
                "name": "average_typist",
                "wpm": 45,
                "error_rate": 0.03,
                "correction_speed": 0.6,
                "think_pause_probability": 0.12,
            },
            {
                "name": "slow_typist",
                "wpm": 25,
                "error_rate": 0.05,
                "correction_speed": 0.4,
                "think_pause_probability": 0.20,
            },
        ]

    def _load_mouse_profiles(self) -> list[dict]:
        """Загрузка профилей движения мыши"""
        return [
            {
                "name": "precise",
                "speed_factor": 1.2,
                "jitter_amount": 0.1,
                "pause_probability": 0.08,
            },
            {
                "name": "casual",
                "speed_factor": 0.8,
                "jitter_amount": 0.3,
                "pause_probability": 0.15,
            },
            {
                "name": "erratic",
                "speed_factor": 1.0,
                "jitter_amount": 0.5,
                "pause_probability": 0.25,
            },
        ]

    def _load_reading_profiles(self) -> list[dict]:
        """Загрузка профилей чтения"""
        return [
            {
                "name": "speed_reader",
                "wpm": 300,
                "comprehension_pause_factor": 0.5,
                "scroll_frequency": 0.3,
            },
            {
                "name": "average_reader",
                "wpm": 200,
                "comprehension_pause_factor": 1.0,
                "scroll_frequency": 0.6,
            },
            {
                "name": "careful_reader",
                "wpm": 150,
                "comprehension_pause_factor": 1.5,
                "scroll_frequency": 0.8,
            },
        ]

    def _generate_session_profile(self) -> dict:
        """Генерация профиля для текущей сессии"""
        return {
            "typing": random.choice(self.typing_profiles),
            "mouse": random.choice(self.mouse_profiles),
            "reading": random.choice(self.reading_profiles),
            "session_start": time.time(),
            "fatigue_factor": 0.0,  # Увеличивается со временем
            "distraction_probability": random.uniform(0.05, 0.15),
        }

    async def human_type(self, page: Page, selector: str, text: str):
        """Человекоподобная печать с учетом профиля"""
        element = await page.wait_for_selector(selector)
        await element.click()

        profile = self.current_session_profile["typing"]
        base_delay = 60 / (profile["wpm"] * 5)  # 5 символов в среднем на слово

        for i, char in enumerate(text):
            # Добавление усталости со временем
            fatigue_factor = self._calculate_fatigue()
            char_delay = base_delay * (1 + fatigue_factor)

            # Случайные вариации в скорости
            char_delay *= random.uniform(0.5, 1.8)

            # Специальная обработка для разных типов символов
            if char.isupper():
                char_delay *= 1.2  # Медленнее для заглавных
            elif char in ".,!?;:":
                char_delay *= 1.5  # Пауза после пунктуации
            elif char == " ":
                char_delay *= 0.8  # Быстрее для пробелов

            # Ошибки и исправления
            if random.random() < profile["error_rate"]:
                # Печатаем неправильный символ
                wrong_char = chr(ord(char) + random.randint(-2, 2))
                await element.type(wrong_char)
                await asyncio.sleep(char_delay)

                # Пауза на "осознание" ошибки
                await asyncio.sleep(random.uniform(0.2, 0.8))

                # Исправление (backspace + правильный символ)
                await page.keyboard.press("Backspace")
                await asyncio.sleep(char_delay * profile["correction_speed"])

            # Паузы на размышление
            if random.random() < profile["think_pause_probability"]:
                await asyncio.sleep(random.uniform(0.5, 2.0))

            await element.type(char)
            await asyncio.sleep(char_delay)

    async def human_mouse_move(self, page: Page, target_x: int, target_y: int):
        """Человекоподобное движение мыши"""
        current_pos = await page.evaluate(
            "() => ({x: window.mouseX || 0, y: window.mouseY || 0})"
        )
        start_x, start_y = current_pos.get("x", 0), current_pos.get("y", 0)

        profile = self.current_session_profile["mouse"]

        # Генерация промежуточных точек по кривой Безье
        points = self._generate_mouse_path(
            (start_x, start_y), (target_x, target_y), profile["jitter_amount"]
        )

        for i, (x, y) in enumerate(points):
            # Переменная скорость движения
            speed_factor = profile["speed_factor"]
            if i < len(points) * 0.2:  # Ускорение в начале
                speed_factor *= 0.5
            elif i > len(points) * 0.8:  # Замедление в конце
                speed_factor *= 0.7

            await page.mouse.move(x, y)

            # Случайные микропаузы
            if random.random() < profile["pause_probability"]:
                await asyncio.sleep(random.uniform(0.01, 0.05))
            else:
                await asyncio.sleep(random.uniform(0.005, 0.02) / speed_factor)

    def _generate_mouse_path(
        self, start: tuple[int, int], end: tuple[int, int], jitter: float
    ) -> list[tuple[int, int]]:
        """Генерация естественной траектории движения мыши"""
        start_x, start_y = start
        end_x, end_y = end

        # Расчет контрольных точек для кривой Безье
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        steps = max(10, int(distance / 10))

        # Добавление промежуточных контрольных точек для более естественной кривой
        mid_x = (start_x + end_x) / 2 + random.uniform(
            -distance * jitter, distance * jitter
        )
        mid_y = (start_y + end_y) / 2 + random.uniform(
            -distance * jitter, distance * jitter
        )

        points = []
        for i in range(steps):
            t = i / (steps - 1)

            # Квадратичная кривая Безье
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * mid_x + t**2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * mid_y + t**2 * end_y

            # Добавление небольшого шума
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)

            points.append((int(x), int(y)))

        return points

    async def simulate_reading(self, page: Page, content_selector: str):
        """Симуляция чтения контента"""
        content_element = await page.wait_for_selector(content_selector)
        content_text = await content_element.inner_text()

        profile = self.current_session_profile["reading"]
        word_count = len(content_text.split())

        # Расчет времени чтения
        reading_time = (word_count / profile["wpm"]) * 60  # в секундах
        reading_time *= profile["comprehension_pause_factor"]

        # Симуляция движений глаз через движения мыши
        viewport = await page.viewport_size()
        content_box = await content_element.bounding_box()

        if content_box:
            read_segments = max(3, int(reading_time / 10))  # Сегменты по 10 секунд

            for segment in range(read_segments):
                # Случайная точка в области контента
                x = content_box["x"] + random.randint(0, int(content_box["width"]))
                y = content_box["y"] + random.randint(0, int(content_box["height"]))

                await self.human_mouse_move(page, x, y)

                # Пауза на "чтение"
                segment_time = reading_time / read_segments
                await asyncio.sleep(segment_time * random.uniform(0.8, 1.2))

                # Случайные прокрутки
                if random.random() < profile["scroll_frequency"]:
                    scroll_amount = random.randint(100, 300)
                    await page.mouse.wheel(0, scroll_amount)
                    await asyncio.sleep(random.uniform(0.5, 1.0))

    def _calculate_fatigue(self) -> float:
        """Расчет фактора усталости на основе времени сессии"""
        session_duration = time.time() - self.current_session_profile["session_start"]
        # Усталость увеличивается нелинейно со временем
        return min(0.5, (session_duration / 3600) ** 1.5)  # Максимум 50% замедления


# ========================================
# 3. IDENTITY ROTATION EXAMPLE
# ========================================


class IdentityRotationManager:
    """Менеджер ротации идентичности с консистентными профилями"""

    def __init__(self):
        self.identity_pool = []
        self.active_identities = {}
        self.cooldown_identities = {}
        self.geo_consistency_db = self._load_geo_consistency_db()
        self.hardware_profiles = self._load_hardware_profiles()

    def _load_geo_consistency_db(self) -> dict:
        """База данных для обеспечения геоконсистентности"""
        return {
            "US": {
                "timezones": [
                    "America/New_York",
                    "America/Chicago",
                    "America/Denver",
                    "America/Los_Angeles",
                ],
                "languages": ["en-US"],
                "currencies": ["USD"],
                "typical_resolutions": [(1920, 1080), (1366, 768), (2560, 1440)],
                "common_browsers": ["Chrome", "Safari", "Firefox", "Edge"],
            },
            "GB": {
                "timezones": ["Europe/London"],
                "languages": ["en-GB"],
                "currencies": ["GBP"],
                "typical_resolutions": [(1920, 1080), (1366, 768), (1440, 900)],
                "common_browsers": ["Chrome", "Safari", "Firefox"],
            },
            "DE": {
                "timezones": ["Europe/Berlin"],
                "languages": ["de-DE"],
                "currencies": ["EUR"],
                "typical_resolutions": [(1920, 1080), (1680, 1050), (2560, 1440)],
                "common_browsers": ["Chrome", "Firefox", "Edge"],
            },
        }

    def _load_hardware_profiles(self) -> list[dict]:
        """Загрузка профилей аппаратного обеспечения"""
        return [
            {
                "category": "high_end_desktop",
                "cpu_cores": 8,
                "memory_gb": 16,
                "gpu_vendor": "NVIDIA",
                "gpu_model": "RTX 3070",
                "typical_resolutions": [(2560, 1440), (3840, 2160)],
                "performance_factor": 1.2,
            },
            {
                "category": "mid_range_desktop",
                "cpu_cores": 6,
                "memory_gb": 8,
                "gpu_vendor": "AMD",
                "gpu_model": "RX 6600",
                "typical_resolutions": [(1920, 1080), (2560, 1440)],
                "performance_factor": 1.0,
            },
            {
                "category": "laptop",
                "cpu_cores": 4,
                "memory_gb": 8,
                "gpu_vendor": "Intel",
                "gpu_model": "Iris Xe",
                "typical_resolutions": [(1366, 768), (1920, 1080)],
                "performance_factor": 0.8,
            },
        ]

    async def generate_identity(self, geo_region: str = None) -> dict:
        """Генерация консистентной идентичности"""
        if not geo_region:
            geo_region = random.choice(list(self.geo_consistency_db.keys()))

        geo_data = self.geo_consistency_db[geo_region]
        hardware = random.choice(self.hardware_profiles)

        # Базовые характеристики
        identity = {
            "id": secrets.token_hex(8),
            "geo_region": geo_region,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "last_used": None,
        }

        # Географическая консистентность
        identity.update(
            {
                "timezone": random.choice(geo_data["timezones"]),
                "language": random.choice(geo_data["languages"]),
                "currency": random.choice(geo_data["currencies"]),
            }
        )

        # Аппаратные характеристики
        resolution = random.choice(hardware["typical_resolutions"])
        identity.update(
            {
                "hardware_category": hardware["category"],
                "screen_width": resolution[0],
                "screen_height": resolution[1],
                "color_depth": random.choice([24, 32]),
                "cpu_cores": hardware["cpu_cores"],
                "memory_gb": hardware["memory_gb"],
            }
        )

        # Браузерные характеристики
        browser = random.choice(geo_data["common_browsers"])
        identity.update(
            {
                "browser": browser,
                "browser_version": self._generate_browser_version(browser),
                "user_agent": self._generate_user_agent(browser, geo_region, hardware),
                "platform": self._generate_platform(hardware),
            }
        )

        # WebGL и Canvas fingerprints
        identity.update(
            {
                "webgl_vendor": hardware["gpu_vendor"],
                "webgl_renderer": hardware["gpu_model"],
                "canvas_fingerprint": self._generate_canvas_fingerprint(identity),
                "audio_fingerprint": self._generate_audio_fingerprint(hardware),
            }
        )

        return identity

    def _generate_browser_version(self, browser: str) -> str:
        """Генерация реалистичной версии браузера"""
        versions = {
            "Chrome": ["108.0.5359.125", "109.0.5414.74", "110.0.5481.77"],
            "Firefox": ["108.0", "109.0", "110.0"],
            "Safari": ["16.2", "16.3", "16.4"],
            "Edge": ["108.0.1462.54", "109.0.1518.52", "110.0.1587.41"],
        }
        return random.choice(versions.get(browser, ["100.0"]))

    def _generate_user_agent(self, browser: str, geo_region: str, hardware: dict) -> str:
        """Генерация консистентного User-Agent"""
        platform_map = {
            "high_end_desktop": "Windows NT 10.0; Win64; x64",
            "mid_range_desktop": "Windows NT 10.0; Win64; x64",
            "laptop": "Windows NT 10.0; Win64; x64",
        }

        platform = platform_map[hardware["category"]]

        if browser == "Chrome":
            version = self._generate_browser_version(browser)
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        elif browser == "Firefox":
            version = self._generate_browser_version(browser)
            return (
                f"Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}"
            )
        elif browser == "Safari":
            return f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15"
        else:
            return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

    def _generate_platform(self, hardware: dict) -> str:
        """Генерация платформы на основе аппаратного профиля"""
        if hardware["category"] == "laptop":
            return random.choice(["Win32", "MacIntel"])
        else:
            return "Win32"

    def _generate_canvas_fingerprint(self, identity: dict) -> str:
        """Генерация Canvas fingerprint на основе характеристик"""
        base_string = (
            f"{identity['browser']}{identity['screen_width']}{identity['color_depth']}"
        )
        hash_object = hashlib.md5(base_string.encode())
        return hash_object.hexdigest()[:16]

    def _generate_audio_fingerprint(self, hardware: dict) -> str:
        """Генерация Audio fingerprint на основе аппаратуры"""
        base_string = (
            f"{hardware['gpu_model']}{hardware['cpu_cores']}{hardware['memory_gb']}"
        )
        hash_object = hashlib.sha256(base_string.encode())
        return hash_object.hexdigest()[:24]

    async def apply_identity_to_context(self, context: BrowserContext, identity: dict):
        """Применение идентичности к контексту браузера"""

        # Основной скрипт модификации fingerprint
        fingerprint_script = f"""
        // Переопределение Navigator свойств
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{identity["platform"]}'
        }});
        
        Object.defineProperty(navigator, 'language', {{
            get: () => '{identity["language"]}'
        }});
        
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{identity["language"]}']
        }});
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {identity["cpu_cores"]}
        }});
        
        // Переопределение Screen свойств
        Object.defineProperty(screen, 'width', {{
            get: () => {identity["screen_width"]}
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: () => {identity["screen_height"]}
        }});
        
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {identity["color_depth"]}
        }});
        
        // WebGL модификации
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{ // UNMASKED_VENDOR_WEBGL
                return '{identity["webgl_vendor"]}';
            }}
            if (parameter === 37446) {{ // UNMASKED_RENDERER_WEBGL
                return '{identity["webgl_renderer"]}';
            }}
            return getParameter.call(this, parameter);
        }};
        
        // Canvas модификация
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {{
            const original = toDataURL.apply(this, arguments);
            // Добавляем незначительный шум на основе fingerprint
            const noise = '{identity["canvas_fingerprint"]}';
            return original.slice(0, -4) + noise.slice(-4);
        }};
        
        // Timezone
        const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            const options = originalResolvedOptions.call(this);
            options.timeZone = '{identity["timezone"]}';
            return options;
        }};
        
        // Audio Context модификация
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {{
            const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
            AudioContext.prototype.createAnalyser = function() {{
                const analyser = originalCreateAnalyser.call(this);
                const originalGetFrequencyData = analyser.getFloatFrequencyData;
                analyser.getFloatFrequencyData = function(array) {{
                    originalGetFrequencyData.call(this, array);
                    // Добавляем шум на основе hardware fingerprint
                    const noiseBase = parseFloat('0.{identity["audio_fingerprint"][:8]}');
                    for (let i = 0; i < array.length; i++) {{
                        array[i] += (Math.random() - 0.5) * noiseBase * 0.001;
                    }}
                }};
                return analyser;
            }};
        }}
        """

        await context.add_init_script(fingerprint_script)

        # Обновление статистики использования
        identity["usage_count"] += 1
        identity["last_used"] = datetime.now().isoformat()

    async def rotate_identity(self, current_identity_id: str) -> dict:
        """Ротация текущей идентичности"""
        # Помещаем текущую идентичность в cooldown
        if current_identity_id in self.active_identities:
            identity = self.active_identities.pop(current_identity_id)
            self.cooldown_identities[current_identity_id] = {
                "identity": identity,
                "cooldown_until": datetime.now() + timedelta(hours=2),
            }

        # Выбираем новую идентичность
        available_identities = [
            identity
            for identity in self.identity_pool
            if identity["id"] not in self.active_identities
            and identity["id"] not in self.cooldown_identities
        ]

        if not available_identities:
            # Генерируем новую идентичность если пул исчерпан
            new_identity = await self.generate_identity()
            self.identity_pool.append(new_identity)
            return new_identity

        # Выбираем наименее использованную идентичность
        selected_identity = min(available_identities, key=lambda x: x["usage_count"])
        self.active_identities[selected_identity["id"]] = selected_identity

        return selected_identity

    async def cleanup_expired_cooldowns(self):
        """Очистка истекших cooldown идентичностей"""
        now = datetime.now()
        expired_ids = [
            identity_id
            for identity_id, data in self.cooldown_identities.items()
            if datetime.fromisoformat(data["cooldown_until"].isoformat()) < now
        ]

        for identity_id in expired_ids:
            del self.cooldown_identities[identity_id]


# ========================================
# 4. USAGE EXAMPLE
# ========================================


async def complete_authentication_example():
    """Полный пример использования всех компонентов"""

    # Инициализация компонентов
    session_manager = AdvancedSessionManager()
    behavior_simulator = HumanBehaviorSimulator()
    identity_manager = IdentityRotationManager()

    print("🚀 Starting complete authentication example...")

    async with async_playwright() as p:
        # Генерация новой идентичности
        identity = await identity_manager.generate_identity("US")
        print(f"✅ Generated identity: {identity['id']} ({identity['geo_region']})")

        # Запуск браузера с прокси
        browser = await p.chromium.launch(
            headless=False,  # Для демонстрации
            proxy={
                "server": "http://proxy-server:8080",
                # "username": "proxy_user",
                # "password": "proxy_pass"
            },
        )

        # Создание контекста с идентичностью
        context = await browser.new_context(
            user_agent=identity["user_agent"],
            viewport={
                "width": identity["screen_width"],
                "height": identity["screen_height"],
            },
            locale=identity["language"],
            timezone_id=identity["timezone"],
        )

        # Применение fingerprint модификаций
        await identity_manager.apply_identity_to_context(context, identity)
        print("✅ Applied identity fingerprint")

        # Попытка восстановления существующей сессии
        existing_sessions = list(session_manager.sessions_dir.glob("notebooklm_*.enc"))
        if existing_sessions:
            latest_session = max(existing_sessions, key=lambda x: x.stat().st_mtime)
            session_id = latest_session.stem

            if await session_manager.restore_session(session_id, context):
                print(f"✅ Restored existing session: {session_id}")
            else:
                print("⚠️ Failed to restore session, proceeding with new authentication")

        # Переход на NotebookLM
        page = await context.new_page()
        print("🌐 Navigating to NotebookLM...")

        await page.goto("https://notebooklm.google.com/")

        # Проверка, требуется ли авторизация
        try:
            await page.wait_for_selector('img[alt="NotebookLM Logo"]', timeout=5000)
            print("✅ Already authenticated!")
        except:
            print("🔐 Authentication required, starting human-like login...")

            # Поиск кнопки входа
            login_button = await page.wait_for_selector(
                'button:has-text("Sign in")', timeout=10000
            )

            # Человекоподобный клик
            await behavior_simulator.human_mouse_move(
                page, *await login_button.bounding_box().values()[:2]
            )
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await login_button.click()

            # Ожидание формы входа Google
            email_input = await page.wait_for_selector(
                'input[type="email"]', timeout=30000
            )

            # Человекоподобный ввод email
            test_email = "your.test.email@gmail.com"  # Замените на реальный
            await behavior_simulator.human_type(page, 'input[type="email"]', test_email)

            # Клик Next
            next_button = await page.wait_for_selector("#identifierNext")
            await behavior_simulator.human_mouse_move(
                page, *await next_button.bounding_box().values()[:2]
            )
            await asyncio.sleep(random.uniform(1, 2))
            await next_button.click()

            # Ввод пароля (в реальном приложении используйте безопасное хранение)
            password_input = await page.wait_for_selector(
                'input[type="password"]', timeout=30000
            )
            test_password = "your_secure_password"  # Замените на реальный
            await behavior_simulator.human_type(
                page, 'input[type="password"]', test_password
            )

            # Подтверждение пароля
            password_next = await page.wait_for_selector("#passwordNext")
            await behavior_simulator.human_mouse_move(
                page, *await password_next.bounding_box().values()[:2]
            )
            await asyncio.sleep(random.uniform(1, 2))
            await password_next.click()

            # Ожидание завершения авторизации
            try:
                await page.wait_for_selector('img[alt="NotebookLM Logo"]', timeout=60000)
                print("✅ Authentication successful!")

                # Сохранение сессии
                session_id = await session_manager.save_session(
                    context, "notebooklm", "test_user"
                )
                print(f"✅ Session saved: {session_id}")

            except:
                print("❌ Authentication failed or timed out")

        # Симуляция использования NotebookLM
        print("📚 Simulating NotebookLM usage...")

        # Поиск области контента для "чтения"
        try:
            content_area = await page.wait_for_selector("main", timeout=10000)
            await behavior_simulator.simulate_reading(page, "main")
            print("✅ Simulated reading behavior")
        except:
            print("⚠️ Could not find content area for reading simulation")

        # Случайные человекоподобные действия
        for _ in range(3):
            # Случайное движение мыши
            viewport = await page.viewport_size()
            random_x = random.randint(100, viewport["width"] - 100)
            random_y = random.randint(100, viewport["height"] - 100)

            await behavior_simulator.human_mouse_move(page, random_x, random_y)
            await asyncio.sleep(random.uniform(2, 5))

        print("✅ Completed human behavior simulation")

        # Ротация идентичности для следующего использования
        new_identity = await identity_manager.rotate_identity(identity["id"])
        print(f"🔄 Rotated to new identity: {new_identity['id']}")

        await browser.close()
        print("🎉 Authentication example completed successfully!")


if __name__ == "__main__":
    asyncio.run(complete_authentication_example())
