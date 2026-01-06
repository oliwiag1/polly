"""
Testy jednostkowe dla dekoratorów.
"""

import pytest
import time
from fastapi import HTTPException


class TestLogExecutionDecorator:
    """Testy dla dekoratora log_execution."""

    def test_log_execution_sync_function(self):
        """Sprawdza logowanie dla funkcji synchronicznej."""
        from app.decorators import log_execution

        @log_execution
        def sample_function(x, y):
            return x + y

        result = sample_function(2, 3)

        assert result == 5

    @pytest.mark.asyncio
    async def test_log_execution_async_function(self):
        """Sprawdza logowanie dla funkcji asynchronicznej."""
        from app.decorators import log_execution

        @log_execution
        async def async_sample(x):
            return x * 2

        result = await async_sample(5)

        assert result == 10

    def test_log_execution_with_exception(self):
        """Sprawdza logowanie przy wyjątku."""
        from app.decorators import log_execution

        @log_execution
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    @pytest.mark.asyncio
    async def test_log_execution_async_with_exception(self):
        """Sprawdza logowanie asynchroniczne przy wyjątku."""
        from app.decorators import log_execution

        @log_execution
        async def async_failing():
            raise ValueError("Async error")

        with pytest.raises(ValueError):
            await async_failing()


class TestHandleExceptionsDecorator:
    """Testy dla dekoratora handle_exceptions."""

    @pytest.mark.asyncio
    async def test_handle_exceptions_success(self):
        """Sprawdza sukces bez wyjątku."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        async def success_func():
            return "success"

        result = await success_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_handle_exceptions_value_error(self):
        """Sprawdza obsługę ValueError."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        async def validation_error():
            raise ValueError("Validation failed")

        with pytest.raises(HTTPException) as exc:
            await validation_error()

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_handle_exceptions_key_error(self):
        """Sprawdza obsługę KeyError."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        async def not_found_error():
            raise KeyError("item")

        with pytest.raises(HTTPException) as exc:
            await not_found_error()

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_handle_exceptions_generic_error(self):
        """Sprawdza obsługę ogólnego błędu."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        async def internal_error():
            raise RuntimeError("Unexpected error")

        with pytest.raises(HTTPException) as exc:
            await internal_error()

        assert exc.value.status_code == 500

    @pytest.mark.asyncio
    async def test_handle_exceptions_http_exception_passthrough(self):
        """Sprawdza przepuszczenie HTTPException."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        async def http_error():
            raise HTTPException(status_code=403, detail="Forbidden")

        with pytest.raises(HTTPException) as exc:
            await http_error()

        assert exc.value.status_code == 403

    def test_handle_exceptions_sync_success(self):
        """Sprawdza synchroniczną wersję przy sukcesie."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        def sync_success():
            return "ok"

        result = sync_success()
        assert result == "ok"

    def test_handle_exceptions_sync_value_error(self):
        """Sprawdza synchroniczną obsługę ValueError."""
        from app.decorators import handle_exceptions

        @handle_exceptions
        def sync_validation():
            raise ValueError("Bad value")

        with pytest.raises(HTTPException) as exc:
            sync_validation()

        assert exc.value.status_code == 400


class TestMeasureTimeDecorator:
    """Testy dla dekoratora measure_time."""

    def test_measure_time_sync(self):
        """Sprawdza pomiar czasu dla funkcji synchronicznej."""
        from app.decorators import measure_time

        @measure_time
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()

        assert result == "done"

    @pytest.mark.asyncio
    async def test_measure_time_async(self):
        """Sprawdza pomiar czasu dla funkcji asynchronicznej."""
        from app.decorators import measure_time
        import asyncio

        @measure_time
        async def async_slow():
            await asyncio.sleep(0.01)
            return "async done"

        result = await async_slow()

        assert result == "async done"


class TestRateLimitDecorator:
    """Testy dla dekoratora rate_limit."""

    @pytest.mark.asyncio
    async def test_rate_limit_allows_under_limit(self):
        """Sprawdza przepuszczenie poniżej limitu."""
        from app.decorators import rate_limit

        @rate_limit(max_calls=5, time_window=60)
        async def limited_func():
            return "ok"

        # Powinno przejść
        for _ in range(3):
            result = await limited_func()
            assert result == "ok"

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_over_limit(self):
        """Sprawdza blokowanie powyżej limitu."""
        from app.decorators import rate_limit

        @rate_limit(max_calls=2, time_window=60)
        async def very_limited():
            return "ok"

        # Pierwsze 2 powinny przejść
        await very_limited()
        await very_limited()

        # Trzecie powinno być zablokowane
        with pytest.raises(HTTPException) as exc:
            await very_limited()

        assert exc.value.status_code == 429

    def test_rate_limit_sync_allows_under_limit(self):
        """Sprawdza synchroniczną wersję poniżej limitu."""
        from app.decorators import rate_limit

        @rate_limit(max_calls=5, time_window=60)
        def sync_limited():
            return "sync ok"

        for _ in range(3):
            result = sync_limited()
            assert result == "sync ok"

    def test_rate_limit_sync_blocks_over_limit(self):
        """Sprawdza synchroniczną blokadę powyżej limitu."""
        from app.decorators import rate_limit

        @rate_limit(max_calls=2, time_window=60)
        def sync_very_limited():
            return "ok"

        sync_very_limited()
        sync_very_limited()

        with pytest.raises(HTTPException) as exc:
            sync_very_limited()

        assert exc.value.status_code == 429


class TestValidateSurveyExistsDecorator:
    """Testy dla dekoratora validate_survey_exists."""

    def test_validate_survey_exists_valid(self, database, created_survey):
        """Sprawdza walidację istniejącej ankiety."""
        from app.decorators import validate_survey_exists

        @validate_survey_exists
        def get_something(survey_id):
            return f"Survey {survey_id}"

        result = get_something(survey_id=created_survey.id)
        assert "Survey" in result

    def test_validate_survey_exists_not_found(self, database):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        from app.decorators import validate_survey_exists
        from uuid import uuid4

        @validate_survey_exists
        def get_something(survey_id):
            return f"Survey {survey_id}"

        with pytest.raises(HTTPException) as exc:
            get_something(survey_id=uuid4())

        assert exc.value.status_code == 404

    def test_validate_survey_exists_no_id(self, database):
        """Sprawdza błąd przy braku survey_id."""
        from app.decorators import validate_survey_exists

        @validate_survey_exists
        def no_id_func():
            return "no id"

        with pytest.raises(ValueError, match="survey_id is required"):
            no_id_func()


class TestAsyncioIscoroutinefunction:
    """Testy dla funkcji pomocniczej asyncio_iscoroutinefunction."""

    def test_detects_async_function(self):
        """Sprawdza wykrywanie funkcji asynchronicznej."""
        from app.decorators import asyncio_iscoroutinefunction

        async def async_func():
            pass

        assert asyncio_iscoroutinefunction(async_func) is True

    def test_detects_sync_function(self):
        """Sprawdza wykrywanie funkcji synchronicznej."""
        from app.decorators import asyncio_iscoroutinefunction

        def sync_func():
            pass

        assert asyncio_iscoroutinefunction(sync_func) is False
