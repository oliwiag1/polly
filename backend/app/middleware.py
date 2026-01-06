"""
Middleware do śledzenia żądań w Application Insights.
"""
import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.telemetry import get_telemetry


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware do śledzenia żądań HTTP w Application Insights.
    Mierzy czas odpowiedzi i loguje informacje o żądaniach.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        telemetry = get_telemetry()
        
        start_time = time.perf_counter()
        
        # Przygotowanie informacji o żądaniu
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }
        
        response = None
        exception_occurred = None
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            exception_occurred = e
            telemetry.track_exception(e)
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
            
            # Logowanie z odpowiednim poziomem
            if status_code >= 500:
                logging.error(f"Request failed: {log_data}")
            elif status_code >= 400:
                logging.warning(f"Request client error: {log_data}")
            else:
                logging.info(f"Request completed: {log_data}")
