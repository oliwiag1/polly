import os
from datetime import datetime
from threading import Lock
from typing import Any


# Metaklasa singletona dla konfiguracji
class ConfigMeta(type):
    _instances: dict[type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


# Singleton menedżera konfiguracji aplikacji
class ConfigManager(metaclass=ConfigMeta):
    """
    Singleton zarządzający konfiguracją całej aplikacji.
    Centralizuje wszystkie ustawienia i zmienne środowiskowe.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._initialized_at = datetime.now()
        self._config: dict[str, Any] = {}

        # Załadowanie domyślnej konfiguracji
        self._load_defaults()
        # Nadpisanie wartościami ze zmiennych środowiskowych
        self._load_from_environment()

    # Załadowanie domyślnych ustawień
    def _load_defaults(self) -> None:
        self._config = {
            # Ustawienia serwera
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False,
                "reload": True,
            },
            # Ustawienia API
            "api": {
                "base_url": "http://localhost:8000",
                "title": "Polly - Survey API",
                "version": "1.0.0",
                "docs_url": "/docs",
                "redoc_url": "/redoc",
            },
            # Ustawienia CORS
            "cors": {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
            # Limity aplikacji
            "limits": {
                "max_questions_per_survey": 50,
                "max_options_per_question": 20,
                "max_title_length": 200,
                "max_description_length": 1000,
            },
            # Ustawienia ankiet
            "survey": {
                "default_required": False,
                "allow_anonymous": True,
            },
            # Azure Application Insights
            "azure": {
                "appinsights_connection_string": None,
            },
        }

    # Załadowanie konfiguracji ze zmiennych środowiskowych
    def _load_from_environment(self) -> None:
        env_mappings = {
            "POLLY_HOST": ("server", "host"),
            "POLLY_PORT": ("server", "port", int),
            "POLLY_DEBUG": ("server", "debug", lambda x: x.lower() == "true"),
            "POLLY_BASE_URL": ("api", "base_url"),
            "POLLY_MAX_QUESTIONS": ("limits", "max_questions_per_survey", int),
            "APPLICATIONINSIGHTS_CONNECTION_STRING": (
                "azure",
                "appinsights_connection_string",
            ),
        }

        for env_var, mapping in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                section, key = mapping[0], mapping[1]
                # Konwersja typu jeśli podana
                if len(mapping) > 2:
                    converter = mapping[2]
                    value = converter(value)
                self._config[section][key] = value

    # Pobranie wartości konfiguracji
    def get(self, section: str, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._config.get(section, {}).get(key, default)

    # Ustawienie wartości konfiguracji
    def set(self, section: str, key: str, value: Any) -> None:
        with self._lock:
            if section not in self._config:
                self._config[section] = {}
            self._config[section][key] = value

    # Pobranie całej sekcji konfiguracji
    def get_section(self, section: str) -> dict[str, Any]:
        with self._lock:
            return dict(self._config.get(section, {}))

    # Pobranie URL bazowego API
    @property
    def base_url(self) -> str:
        return self.get("api", "base_url", "http://localhost:8000")

    # Pobranie ustawień serwera
    @property
    def server_config(self) -> dict[str, Any]:
        return self.get_section("server")

    # Pobranie limitów
    @property
    def limits(self) -> dict[str, int]:
        return self.get_section("limits")

    # Pobranie statystyk konfiguracji
    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "initialized_at": self._initialized_at.isoformat(),
                "sections": list(self._config.keys()),
                "total_settings": sum(len(v) for v in self._config.values()),
            }

    # Eksport całej konfiguracji (bez wrażliwych danych)
    def export_config(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._config)


# Funkcja pomocnicza do pobierania instancji konfiguracji
def get_config() -> ConfigManager:
    return ConfigManager()
