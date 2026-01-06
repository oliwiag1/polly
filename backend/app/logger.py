import logging
import sys
from datetime import datetime
from threading import Lock
from typing import Any


# Metaklasa singletona dla loggera
class LoggerMeta(type):
    _instances: dict[type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


# Singleton loggera aplikacji
class AppLogger(metaclass=LoggerMeta):
    """
    Singleton zarządzający logowaniem w całej aplikacji.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._initialized_at = datetime.now()
        self._log_count = {"INFO": 0, "WARNING": 0, "ERROR": 0, "DEBUG": 0}

        # Konfiguracja głównego loggera
        self._logger = logging.getLogger("polly")
        self._logger.setLevel(logging.DEBUG)

        # Handler do konsoli
        if not self._logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Format logów
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

    # Logowanie informacji
    def info(self, message: str, module: str = "app") -> None:
        with self._lock:
            self._log_count["INFO"] += 1
        self._logger.info(f"[{module}] {message}")

    # Logowanie ostrzeżeń
    def warning(self, message: str, module: str = "app") -> None:
        with self._lock:
            self._log_count["WARNING"] += 1
        self._logger.warning(f"[{module}] {message}")

    # Logowanie błędów
    def error(self, message: str, module: str = "app") -> None:
        with self._lock:
            self._log_count["ERROR"] += 1
        self._logger.error(f"[{module}] {message}")

    # Logowanie debugowania
    def debug(self, message: str, module: str = "app") -> None:
        with self._lock:
            self._log_count["DEBUG"] += 1
        self._logger.debug(f"[{module}] {message}")

    # Logowanie żądania HTTP
    def log_request(
        self, method: str, path: str, status_code: int, duration_ms: float
    ) -> None:
        message = f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)"
        if status_code >= 400:
            self.warning(message, module="http")
        else:
            self.info(message, module="http")

    # Logowanie operacji na bazie danych
    def log_database_operation(
        self, operation: str, entity: str, entity_id: str | None = None
    ) -> None:
        if entity_id:
            message = f"{operation} {entity} (ID: {entity_id})"
        else:
            message = f"{operation} {entity}"
        self.info(message, module="database")

    # Pobranie statystyk logowania
    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "initialized_at": self._initialized_at.isoformat(),
                "total_logs": sum(self._log_count.values()),
                "logs_by_level": dict(self._log_count),
            }

    # Resetowanie liczników
    def reset_stats(self) -> None:
        with self._lock:
            self._log_count = {"INFO": 0, "WARNING": 0, "ERROR": 0, "DEBUG": 0}


# Funkcja pomocnicza do pobierania instancji loggera
def get_logger() -> AppLogger:
    return AppLogger()
