"""
Moduł telemetrii Azure Application Insights.
Konfiguruje śledzenie żądań, logów i wyjątków.
"""
import logging
from threading import Lock
from typing import Any

from app.config import get_config


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
        connection_string = config.get("azure", "appinsights_connection_string")
        
        if not connection_string:
            logging.info("Application Insights disabled - no connection string provided")
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
                exporter=self._exporter,
                sampler=ProbabilitySampler(1.0)
            )
            
            # Konfiguracja handlera logów
            azure_handler = AzureLogHandler(connection_string=connection_string)
            
            # Dodanie handlera do root loggera
            root_logger = logging.getLogger()
            root_logger.addHandler(azure_handler)
            root_logger.setLevel(logging.INFO)
            
            self._enabled = True
            logging.info("Application Insights initialized successfully")
            
        except ImportError as e:
            logging.warning(f"Application Insights packages not available: {e}")
        except Exception as e:
            logging.error(f"Failed to initialize Application Insights: {e}")
    
    @property
    def enabled(self) -> bool:
        """Czy telemetria jest włączona."""
        return self._enabled
    
    @property
    def tracer(self):
        """Zwraca tracer do śledzenia requestów."""
        return self._tracer
    
    def track_event(self, name: str, properties: dict[str, Any] | None = None) -> None:
        """Śledzi zdarzenie niestandardowe."""
        if not self._enabled:
            return
            
        try:
            from opencensus.ext.azure import metrics_exporter
            # Logowanie jako event przez standardowy logger
            logging.info(f"CustomEvent: {name}", extra={"custom_dimensions": properties or {}})
        except Exception as e:
            logging.debug(f"Failed to track event: {e}")
    
    def track_exception(self, exception: Exception) -> None:
        """Śledzi wyjątek."""
        if not self._enabled:
            return
            
        logging.exception(f"Exception tracked: {exception}")
    
    def get_stats(self) -> dict[str, Any]:
        """Zwraca statystyki telemetrii."""
        return {
            "enabled": self._enabled,
            "tracer_active": self._tracer is not None,
        }


def get_telemetry() -> TelemetryManager:
    """Funkcja pomocnicza do pobierania instancji TelemetryManager."""
    return TelemetryManager()
