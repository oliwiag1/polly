import functools
import logging
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from fastapi import HTTPException

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


# Dekorator na logowanie danych do konsoli
def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    # Dla funkcji asynchronicznych
    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func_name = func.__name__
        # Logowanie przed wykonaniem żądania
        logger.info(f"Executing {func_name} with args={args}, kwargs={kwargs}")
        start_time = time.perf_counter()

        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time

            # Logowanie po wykonaniu żądania
            logger.info(f"{func_name} completed successfully in {elapsed:.4f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time

            # Logowanie w sytuacji gdy wystąpi jakiś błąd
            logger.error(f"{func_name} failed after {elapsed:.4f}s with error: {e}")
            raise

    # Dla zwykłych funkcji
    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func_name = func.__name__
        # Logowanie przed wykonaniem żądania
        logger.info(f"Executing {func_name} with args={args}, kwargs={kwargs}")
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            # Logowanie po wykonaniu żądania
            logger.info(f"{func_name} completed successfully in {elapsed:.4f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            # Logowanie w sytuacji gdy wystąpi jakiś błąd
            logger.error(f"{func_name} failed after {elapsed:.4f}s with error: {e}")
            raise

    # Sprawdzenie czy funkcja jest asynchroniczna czy nie
    if asyncio_iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# Funkcja sprawdzająca czy funkcja jest asynchroniczna
def asyncio_iscoroutinefunction(func: Callable) -> bool:
    import asyncio

    return asyncio.iscoroutinefunction(func)


# Dekorator do obsługi wyjątków
def handle_exceptions(func: Callable[P, R]) -> Callable[P, R]:
    # Dla funkcji asynchronicznych
    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            # Wypisanie informacji o błędach walidacyjnych
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except KeyError as e:
            # Wypisanie informacji o błędzie braku rekordu
            logger.warning(f"Not found error in {func.__name__}: {e}")
            raise HTTPException(status_code=404, detail=f"Resource not found: {e}")
        except Exception as e:
            # Wypisanie informacji o ogólnym błędzie
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    # Dla zwykłych funkcji
    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            # Wypisanie informacji o błędach walidacyjnych
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except KeyError as e:
            # Wypisanie informacji o błędzie braku rekordu
            logger.warning(f"Not found error in {func.__name__}: {e}")
            raise HTTPException(status_code=404, detail=f"Resource not found: {e}")
        except Exception as e:
            # Wypisanie informacji o ogólnym błędzie
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    # Sprawdzenie czy funkcja jest asynchroniczna czy nie
    if asyncio_iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# Dekorator na sprawdzenie czy ankieta istnieje
def validate_survey_exists(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        from uuid import UUID
        from app.database import get_database

        # Wyciągnięcie identyfikatora ankiety
        survey_id = kwargs.get("survey_id")
        if survey_id is None and len(args) > 1:
            potential_id = args[1] if hasattr(args[0], "__class__") else args[0]
            if isinstance(potential_id, UUID):
                survey_id = potential_id

        if survey_id is None:
            raise ValueError("survey_id is required")

        db = get_database()

        # Sprawdzenie czy ankieta istnieje
        if not db.survey_exists(survey_id):
            raise HTTPException(
                status_code=404, detail=f"Survey with ID {survey_id} not found"
            )

        return func(*args, **kwargs)

    return wrapper


# Dekorator na rate limit (ograniczenie na zbyt dużą ilość żądań - DDoS)
def rate_limit(max_calls: int, time_window: int):
    calls: dict[str, list[float]] = {}

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        # Dla funkcji asynchronicznych
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_time = time.time()
            func_name = func.__name__

            if func_name not in calls:
                calls[func_name] = []

            calls[func_name] = [
                call_time
                for call_time in calls[func_name]
                if current_time - call_time < time_window
            ]

            # Jeżeli liczba uruchomień funkcji w pewnym przedziale czasowym była większa niż, to przerwij żądanie
            if len(calls[func_name]) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                )

            calls[func_name].append(current_time)
            return await func(*args, **kwargs)

        # Dla zwykłych funkcji
        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_time = time.time()
            func_name = func.__name__

            if func_name not in calls:
                calls[func_name] = []

            calls[func_name] = [
                call_time
                for call_time in calls[func_name]
                if current_time - call_time < time_window
            ]

            # Jeżeli liczba uruchomień funkcji w pewnym przedziale czasowym była większa niż, to przerwij żądanie
            if len(calls[func_name]) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                )

            calls[func_name].append(current_time)
            return func(*args, **kwargs)

        # Sprawdzenie czy funkcja jest asynchroniczna
        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Dekorator ma pomiar czasu wykonania żądania
def measure_time(func: Callable[P, R]) -> Callable[P, R]:
    # Dla funkcji asynchronicznych
    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        # Wypisanie informacji ile sekund funkcja była wykonywana
        logger.debug(f"{func.__name__} executed in {elapsed:.4f} seconds")
        return result

    # Dla zwykłych funkcji
    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        # Wypisanie informacji ile sekund funkcja była wykonywana
        logger.debug(f"{func.__name__} executed in {elapsed:.4f} seconds")
        return result

    # Sprawdzenie czy funkcja jest asynchroniczna
    if asyncio_iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
