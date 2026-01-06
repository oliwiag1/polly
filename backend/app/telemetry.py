"""
Moduł telemetrii Azure Application Insights.
Konfiguruje śledzenie żądań, logów i wyjątków.
"""

import logging
from threading import Lock
from typing import Any

from app.config import get_config
from app.logger import get_logger


class TelemetryManager:
    """
    Singleton zarządzający telemetrią Application Insights.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._enabled = False
        self._tracer = None
        self._exporter = None

        self._setup()

    def _setup(self) -> None:
        """Konfiguruje Application Insights jeśli connection string jest dostępny."""
        config = get_config()
        app_logger = get_logger()
        connection_string = config.get("azure", "appinsights_connection_string")

        if not connection_string:
            app_logger.info(
                "Application Insights disabled - no connection string provided",
                module="telemetry",
            )
            return

        try:
            from opencensus.ext.azure.trace_exporter import AzureExporter
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            from opencensus.trace.samplers import ProbabilitySampler
            from opencensus.trace.tracer import Tracer

            # Konfiguracja eksportera trace'ów
            self._exporter = AzureExporter(connection_string=connection_string)

            # Konfiguracja tracera z próbkowaniem 100%
            self._tracer = Tracer(
                exporter=self._exporter, sampler=ProbabilitySampler(1.0)
            )

            # Konfiguracja handlera logów
            azure_handler = AzureLogHandler(connection_string=connection_string)

            # Dodanie handlera do root loggera
            polly_logger = logging.getLogger("polly")
            polly_logger.addHandler(azure_handler)
            polly_logger.setLevel(logging.INFO)

            self._enabled = True
            app_logger.info(
                "Application Insights initialized successfully", module="telemetry"
            )

        except ImportError as e:
            app_logger.warning(
                f"Application Insights packages not available: {e}", module="telemetry"
            )
        except Exception as e:
            app_logger.exception(
                f"Failed to initialize Application Insights: {e}", module="telemetry"
            )

    @property
    def enabled(self) -> bool:
        """Czy telemetria jest włączona."""
        return self._enabled

    @property
    def tracer(self):
        """Zwraca tracer do śledzenia requestów."""
        return self._tracer

    @property
    def exporter(self):
        """Zwraca eksportera do middleware OpenCensus/ASGI."""
        return self._exporter

    def track_event(self, name: str, properties: dict[str, Any] | None = None) -> None:
        """Śledzi zdarzenie niestandardowe."""
        if not self._enabled:
            return

        try:
            # Logowanie jako event przez standardowy logger
            get_logger().info(
                f"CustomEvent: {name} props={properties or {}}", module="telemetry"
            )
        except Exception as e:
            get_logger().debug(f"Failed to track event: {e}", module="telemetry")

    def track_exception(self, exception: Exception) -> None:
        """Śledzi wyjątek."""
        if not self._enabled:
            return

        get_logger().exception(f"Exception tracked: {exception}", module="telemetry")

    def get_stats(self) -> dict[str, Any]:
        """Zwraca statystyki telemetrii."""
        return {
            "enabled": self._enabled,
            "tracer_active": self._tracer is not None,
            "exporter_active": self._exporter is not None,
        }


def get_telemetry() -> TelemetryManager:
    """Funkcja pomocnicza do pobierania instancji TelemetryManager."""
    return TelemetryManager()
