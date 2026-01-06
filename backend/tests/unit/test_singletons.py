"""
Testy jednostkowe dla singletonów (Database, ConfigManager, AppLogger).
"""

from datetime import datetime
from uuid import uuid4


class TestDatabaseSingleton:
    """Testy dla singletona Database."""

    def test_database_is_singleton(self, database):
        """Sprawdza czy Database jest singletonem."""
        from app.database import get_database

        db1 = get_database()
        db2 = get_database()

        assert db1 is db2

    def test_database_initial_state(self, database):
        """Sprawdza początkowy stan bazy danych."""
        assert len(database.surveys) == 0
        assert len(database.responses) == 0

    def test_database_add_survey(self, database):
        """Sprawdza dodawanie ankiety do bazy."""
        from app.models import Survey, Question, QuestionType, SurveyLinks

        survey = Survey(
            id=uuid4(),
            title="Test Survey",
            description="Test Description",
            questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
            created_at=datetime.now(),
            links=SurveyLinks(
                survey_url="http://test.local/surveys/123",
                stats_url="http://test.local/surveys/123/stats",
            ),
        )

        database.add_survey(survey)

        assert survey.id in database.surveys
        assert database.get_survey(survey.id) == survey

    def test_database_get_nonexistent_survey(self, database):
        """Sprawdza pobieranie nieistniejącej ankiety."""
        result = database.get_survey(uuid4())
        assert result is None

    def test_database_survey_exists(self, database):
        """Sprawdza metodę survey_exists."""
        from app.models import Survey, Question, QuestionType, SurveyLinks

        survey_id = uuid4()
        assert database.survey_exists(survey_id) is False

        survey = Survey(
            id=survey_id,
            title="Test",
            description=None,
            questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
            created_at=datetime.now(),
            links=SurveyLinks(survey_url="http://x", stats_url="http://y"),
        )
        database.add_survey(survey)

        assert database.survey_exists(survey_id) is True

    def test_database_add_response(self, database, created_survey, sample_answers):
        """Sprawdza dodawanie odpowiedzi."""
        from app.models import SurveyResponse

        response = SurveyResponse(
            id=uuid4(),
            survey_id=created_survey.id,
            answers=sample_answers,
            respondent_id="test-user",
            submitted_at=datetime.now(),
        )

        database.add_response(response)
        responses = database.get_responses(created_survey.id)

        assert len(responses) == 1
        assert responses[0] == response

    def test_database_add_response_nonexistent_survey(self, database, sample_answers):
        """Sprawdza dodawanie odpowiedzi do nieistniejącej ankiety."""
        from app.models import SurveyResponse

        fake_survey_id = uuid4()
        response = SurveyResponse(
            id=uuid4(),
            survey_id=fake_survey_id,
            answers=sample_answers,
            respondent_id="test",
            submitted_at=datetime.now(),
        )

        # Nie powinno rzucić wyjątku, po prostu nie doda
        database.add_response(response)
        assert database.get_responses(fake_survey_id) == []

    def test_database_get_stats(self, database, created_survey):
        """Sprawdza statystyki bazy danych."""
        stats = database.get_stats()

        assert "total_surveys" in stats
        assert "total_responses" in stats
        assert "initialized_at" in stats
        assert stats["total_surveys"] == 1

    def test_database_clear(self, database, created_survey):
        """Sprawdza czyszczenie bazy danych."""
        assert len(database.surveys) > 0

        database.clear()

        assert len(database.surveys) == 0
        assert len(database.responses) == 0


class TestConfigManagerSingleton:
    """Testy dla singletona ConfigManager."""

    def test_config_is_singleton(self, config):
        """Sprawdza czy ConfigManager jest singletonem."""
        from app.config import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_config_default_values(self, config):
        """Sprawdza domyślne wartości konfiguracji."""
        assert config.get("server", "host") == "0.0.0.0"
        assert config.get("server", "port") == 8000
        assert config.get("api", "version") == "1.0.0"

    def test_config_get_nonexistent(self, config):
        """Sprawdza pobieranie nieistniejącej wartości."""
        result = config.get("nonexistent", "key")
        assert result is None

        result_with_default = config.get("nonexistent", "key", "default")
        assert result_with_default == "default"

    def test_config_set_value(self, config):
        """Sprawdza ustawianie wartości."""
        config.set("test_section", "test_key", "test_value")

        assert config.get("test_section", "test_key") == "test_value"

    def test_config_set_new_section(self, config):
        """Sprawdza tworzenie nowej sekcji."""
        config.set("new_section", "key1", "value1")

        assert config.get("new_section", "key1") == "value1"

    def test_config_get_section(self, config):
        """Sprawdza pobieranie całej sekcji."""
        section = config.get_section("server")

        assert isinstance(section, dict)
        assert "host" in section
        assert "port" in section

    def test_config_get_nonexistent_section(self, config):
        """Sprawdza pobieranie nieistniejącej sekcji."""
        section = config.get_section("nonexistent")
        assert section == {}

    def test_config_base_url_property(self, config):
        """Sprawdza property base_url."""
        base_url = config.base_url
        assert isinstance(base_url, str)
        assert base_url.startswith("http")

    def test_config_server_config_property(self, config):
        """Sprawdza property server_config."""
        server_config = config.server_config

        assert isinstance(server_config, dict)
        assert "host" in server_config

    def test_config_limits_property(self, config):
        """Sprawdza property limits."""
        limits = config.limits

        assert isinstance(limits, dict)
        assert "max_questions_per_survey" in limits

    def test_config_get_stats(self, config):
        """Sprawdza statystyki konfiguracji."""
        stats = config.get_stats()

        assert "initialized_at" in stats
        assert "sections" in stats
        assert "total_settings" in stats

    def test_config_export(self, config):
        """Sprawdza eksport konfiguracji."""
        exported = config.export_config()

        assert isinstance(exported, dict)
        assert "server" in exported
        assert "api" in exported


class TestAppLoggerSingleton:
    """Testy dla singletona AppLogger."""

    def test_logger_is_singleton(self, logger):
        """Sprawdza czy AppLogger jest singletonem."""
        from app.logger import get_logger

        logger1 = get_logger()
        logger2 = get_logger()

        assert logger1 is logger2

    def test_logger_info(self, logger):
        """Sprawdza logowanie info."""
        initial_count = logger.get_stats()["logs_by_level"]["INFO"]

        logger.info("Test message")

        assert logger.get_stats()["logs_by_level"]["INFO"] == initial_count + 1

    def test_logger_warning(self, logger):
        """Sprawdza logowanie warning."""
        initial_count = logger.get_stats()["logs_by_level"]["WARNING"]

        logger.warning("Test warning")

        assert logger.get_stats()["logs_by_level"]["WARNING"] == initial_count + 1

    def test_logger_error(self, logger):
        """Sprawdza logowanie error."""
        initial_count = logger.get_stats()["logs_by_level"]["ERROR"]

        logger.error("Test error")

        assert logger.get_stats()["logs_by_level"]["ERROR"] == initial_count + 1

    def test_logger_debug(self, logger):
        """Sprawdza logowanie debug."""
        initial_count = logger.get_stats()["logs_by_level"]["DEBUG"]

        logger.debug("Test debug")

        assert logger.get_stats()["logs_by_level"]["DEBUG"] == initial_count + 1

    def test_logger_with_module(self, logger):
        """Sprawdza logowanie z modułem."""
        # Nie powinno rzucić wyjątku
        logger.info("Test message", module="test_module")
        logger.warning("Test warning", module="test_module")
        logger.error("Test error", module="test_module")

    def test_logger_log_request_success(self, logger):
        """Sprawdza logowanie żądania HTTP z sukcesem."""
        initial_info = logger.get_stats()["logs_by_level"]["INFO"]

        logger.log_request("GET", "/api/test", 200, 15.5)

        assert logger.get_stats()["logs_by_level"]["INFO"] == initial_info + 1

    def test_logger_log_request_error(self, logger):
        """Sprawdza logowanie żądania HTTP z błędem."""
        initial_warning = logger.get_stats()["logs_by_level"]["WARNING"]

        logger.log_request("POST", "/api/test", 400, 10.0)

        assert logger.get_stats()["logs_by_level"]["WARNING"] == initial_warning + 1

    def test_logger_log_database_operation(self, logger):
        """Sprawdza logowanie operacji bazodanowej."""
        initial_info = logger.get_stats()["logs_by_level"]["INFO"]

        logger.log_database_operation("CREATE", "survey", "123")

        assert logger.get_stats()["logs_by_level"]["INFO"] == initial_info + 1

    def test_logger_log_database_operation_without_id(self, logger):
        """Sprawdza logowanie operacji bez ID."""
        # Nie powinno rzucić wyjątku
        logger.log_database_operation("LIST", "surveys")

    def test_logger_get_stats(self, logger):
        """Sprawdza statystyki loggera."""
        logger.info("Test")
        logger.warning("Test")

        stats = logger.get_stats()

        assert "initialized_at" in stats
        assert "total_logs" in stats
        assert "logs_by_level" in stats
        assert stats["total_logs"] >= 2

    def test_logger_reset_stats(self, logger):
        """Sprawdza resetowanie statystyk."""
        logger.info("Test")
        logger.error("Test")

        logger.reset_stats()

        stats = logger.get_stats()
        assert stats["total_logs"] == 0
        assert all(v == 0 for v in stats["logs_by_level"].values())
