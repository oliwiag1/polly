"""
Middleware do śledzenia żądań w Application Insights.
"""

import time
from contextlib import nullcontext
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import get_logger
from app.telemetry import get_telemetry


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware do śledzenia żądań HTTP w Application Insights.
    Mierzy czas odpowiedzi i loguje informacje o żądaniach.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        telemetry = get_telemetry()
        app_logger = get_logger()

        start_time = time.perf_counter()

        # Przygotowanie informacji o żądaniu
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }

        response = None

        span_ctx = nullcontext()
        span = None
        if telemetry.enabled and telemetry.tracer is not None:
            # Span per request; trafi do Application Insights przez AzureExporter
            span_ctx = telemetry.tracer.span(
                name=f"{request.method} {request.url.path}"
            )

        try:
            with span_ctx as span:
                if span is not None:
                    span.add_attribute("http.method", request.method)
                    span.add_attribute("http.path", request.url.path)
                    span.add_attribute("http.url", str(request.url))
                    span.add_attribute(
                        "http.client_ip",
                        request.client.host if request.client else "unknown",
                    )

                response = await call_next(request)
                if span is not None:
                    span.add_attribute("http.status_code", response.status_code)
                return response

        except Exception as e:
            telemetry.track_exception(e)
            if span is not None:
                span.add_attribute("error", True)
            raise

        finally:
            # Obliczenie czasu odpowiedzi
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Logowanie informacji o żądaniu
            status_code = response.status_code if response else 500

            log_data = {
                **request_info,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
            }

            if span is not None:
                span.add_attribute("duration_ms", round(duration_ms, 2))

            # Logowanie z odpowiednim poziomem
            if status_code >= 500:
                app_logger.error(f"Request failed: {log_data}", module="http")
            elif status_code >= 400:
                app_logger.warning(f"Request client error: {log_data}", module="http")
            else:
                app_logger.info(f"Request completed: {log_data}", module="http")
