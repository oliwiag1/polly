"""
Testy integracyjne - interakcje między komponentami.
"""

import pytest
from datetime import datetime
from uuid import uuid4


class TestDatabaseServiceIntegration:
    """Testy integracji Database z SurveyService."""

    def test_service_uses_database(
        self, survey_service, database, sample_survey_create
    ):
        """Sprawdza czy serwis poprawnie używa bazy danych."""
        # Tworzenie ankiety przez serwis
        survey = survey_service.create_survey(sample_survey_create)

        # Weryfikacja w bazie danych
        db_survey = database.get_survey(survey.id)

        assert db_survey == survey
        assert database.survey_exists(survey.id)

    def test_responses_persist_in_database(
        self, survey_service, database, created_survey, sample_answer_submit
    ):
        """Sprawdza trwałość odpowiedzi w bazie danych."""
        # Wysłanie odpowiedzi
        response = survey_service.submit_response(
            created_survey.id, sample_answer_submit
        )

        # Weryfikacja w bazie
        db_responses = database.get_responses(created_survey.id)

        assert len(db_responses) == 1
        assert db_responses[0].id == response.id

    def test_statistics_reflect_database_state(
        self, survey_service, database, created_survey, sample_answer_submit
    ):
        """Sprawdza czy statystyki odzwierciedlają stan bazy."""
        # Początkowe statystyki
        initial_stats = survey_service.get_statistics(created_survey.id)
        assert initial_stats.total_responses == 0

        # Dodanie odpowiedzi
        survey_service.submit_response(created_survey.id, sample_answer_submit)

        # Zaktualizowane statystyki
        updated_stats = survey_service.get_statistics(created_survey.id)
        assert updated_stats.total_responses == 1

    def test_multiple_responses_accumulate(
        self, survey_service, database, created_survey, sample_answer_submit
    ):
        """Sprawdza akumulację wielu odpowiedzi."""
        for _ in range(5):
            survey_service.submit_response(created_survey.id, sample_answer_submit)

        responses = database.get_responses(created_survey.id)
        stats = survey_service.get_statistics(created_survey.id)

        assert len(responses) == 5
        assert stats.total_responses == 5

    def test_clear_database_affects_service(
        self, survey_service, database, sample_survey_create
    ):
        """Sprawdza wpływ czyszczenia bazy na serwis."""
        # Tworzenie danych
        survey = survey_service.create_survey(sample_survey_create)

        # Czyszczenie bazy
        database.clear()

        # Serwis nie powinien znaleźć ankiety
        with pytest.raises(ValueError, match="not found"):
            survey_service.get_survey(survey.id)


class TestConfigServiceIntegration:
    """Testy integracji ConfigManager z SurveyService."""

    def test_links_use_config_base_url(
        self, survey_service, config, sample_survey_create
    ):
        """Sprawdza czy linki używają URL z konfiguracji."""
        survey = survey_service.create_survey(sample_survey_create)

        assert config.base_url in survey.links.survey_url
        assert config.base_url in survey.links.stats_url

    def test_config_change_affects_new_surveys(
        self, survey_service, config, sample_survey_create
    ):
        """Sprawdza czy zmiana konfiguracji wpływa na nowe ankiety."""
        # Pierwsza ankieta
        survey1 = survey_service.create_survey(sample_survey_create)
        _ = survey1.links.survey_url

        # Zmiana konfiguracji
        config.set("api", "base_url", "http://new-domain.com")

        # Nowa ankieta z nowym serwisem (aby pobrać zaktualizowaną konfigurację)
        from app.services import SurveyService

        new_service = SurveyService()
        survey2 = new_service.create_survey(sample_survey_create)

        assert "new-domain.com" in survey2.links.survey_url


class TestLoggerServiceIntegration:
    """Testy integracji AppLogger z innymi komponentami."""

    def test_logger_tracks_operations(self, logger):
        """Sprawdza czy logger śledzi operacje."""
        initial_stats = logger.get_stats()
        initial_total = initial_stats["total_logs"]

        # Wykonanie operacji logowania
        logger.info("Test operation 1")
        logger.info("Test operation 2")
        logger.warning("Test warning")

        updated_stats = logger.get_stats()
        assert updated_stats["total_logs"] == initial_total + 3

    def test_logger_database_operation_logging(self, logger):
        """Sprawdza logowanie operacji bazodanowych."""
        initial_info = logger.get_stats()["logs_by_level"]["INFO"]

        logger.log_database_operation("CREATE", "survey", "123")
        logger.log_database_operation("READ", "survey", "123")
        logger.log_database_operation("DELETE", "survey", "123")

        final_info = logger.get_stats()["logs_by_level"]["INFO"]
        assert final_info == initial_info + 3

    def test_logger_http_request_logging(self, logger):
        """Sprawdza logowanie żądań HTTP."""
        # Sukces
        logger.log_request("GET", "/surveys", 200, 15.0)

        # Błąd
        logger.log_request("POST", "/surveys", 400, 10.0)

        stats = logger.get_stats()
        assert stats["logs_by_level"]["INFO"] >= 1
        assert stats["logs_by_level"]["WARNING"] >= 1


class TestFullWorkflowIntegration:
    """Testy pełnego przepływu aplikacji."""

    def test_complete_survey_workflow(
        self, survey_service, database, sample_survey_create
    ):
        """Sprawdza kompletny przepływ: tworzenie -> odpowiedzi -> statystyki."""
        from app.models import AnswerSubmit, Answer

        # 1. Tworzenie ankiety
        survey = survey_service.create_survey(sample_survey_create)
        assert survey.id is not None

        # 2. Weryfikacja istnienia
        retrieved = survey_service.get_survey(survey.id)
        assert retrieved.title == survey.title

        # 3. Wysyłanie odpowiedzi
        for i in range(3):
            answers = AnswerSubmit(
                answers=[
                    Answer(question_id="q1", value=f"User {i}"),
                    Answer(question_id="q2", value="Niebieski"),
                    Answer(question_id="q4", value=5 + i),
                    Answer(question_id="q5", value="yes" if i % 2 == 0 else "no"),
                ],
                respondent_id=f"user-{i}",
            )
            survey_service.submit_response(survey.id, answers)

        # 4. Pobieranie statystyk
        stats = survey_service.get_statistics(survey.id)

        assert stats.total_responses == 3
        assert len(stats.questions_stats) == 4

        # Sprawdzenie średniej dla oceny
        rating_stats = next(q for q in stats.questions_stats if q.question_id == "q4")
        assert rating_stats.average_value == 6.0  # (5+6+7)/3

        # Sprawdzenie rozkładu tak/nie
        yes_no_stats = next(q for q in stats.questions_stats if q.question_id == "q5")
        assert yes_no_stats.answer_distribution["yes"] == 2
        assert yes_no_stats.answer_distribution["no"] == 1

    def test_multiple_surveys_isolation(self, survey_service, sample_survey_create):
        """Sprawdza izolację danych między ankietami."""
        from app.models import AnswerSubmit, Answer

        # Tworzenie dwóch ankiet
        survey1 = survey_service.create_survey(sample_survey_create)
        survey2 = survey_service.create_survey(sample_survey_create)

        # Odpowiedzi tylko dla ankiety 1
        for _ in range(3):
            answers = AnswerSubmit(
                answers=[
                    Answer(question_id="q1", value="Test"),
                    Answer(question_id="q2", value="Niebieski"),
                    Answer(question_id="q4", value=5),
                    Answer(question_id="q5", value="yes"),
                ],
            )
            survey_service.submit_response(survey1.id, answers)

        # Statystyki
        stats1 = survey_service.get_statistics(survey1.id)
        stats2 = survey_service.get_statistics(survey2.id)

        assert stats1.total_responses == 3
        assert stats2.total_responses == 0

    def test_list_all_surveys(self, survey_service, sample_survey_create):
        """Sprawdza listowanie wszystkich ankiet."""
        # Tworzenie kilku ankiet
        surveys = []
        for i in range(5):
            survey = survey_service.create_survey(sample_survey_create)
            surveys.append(survey)

        # Pobieranie wszystkich
        all_surveys = survey_service.get_all_surveys()

        assert len(all_surveys) == 5
        for survey in surveys:
            assert any(s.id == survey.id for s in all_surveys)


class TestSingletonsIntegration:
    """Testy integracji singletonów."""

    def test_all_singletons_initialized(self, database, config, logger):
        """Sprawdza czy wszystkie singletony są zainicjalizowane."""
        assert database is not None
        assert config is not None
        assert logger is not None

    def test_singletons_share_state(self, database, config, logger):
        """Sprawdza czy singletony współdzielą stan."""
        from app.database import get_database
        from app.config import get_config
        from app.logger import get_logger

        # Dodanie danych
        from app.models import Survey, Question, QuestionType, SurveyLinks

        survey = Survey(
            id=uuid4(),
            title="Test",
            description=None,
            questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
            created_at=datetime.now(),
            links=SurveyLinks(survey_url="http://x", stats_url="http://y"),
        )
        database.add_survey(survey)

        # Weryfikacja przez nowe pobranie
        db2 = get_database()
        assert db2.survey_exists(survey.id)

        # Zmiana konfiguracji
        config.set("test", "key", "value")
        config2 = get_config()
        assert config2.get("test", "key") == "value"

        # Logowanie
        logger.info("Test")
        logger2 = get_logger()
        assert logger2.get_stats()["total_logs"] >= 1

    def test_service_uses_all_singletons(
        self, survey_service, database, config, logger, sample_survey_create
    ):
        """Sprawdza czy serwis używa wszystkich singletonów."""
        # Tworzenie ankiety (używa wszystkich)
        survey = survey_service.create_survey(sample_survey_create)

        # Weryfikacja bazy
        assert database.survey_exists(survey.id)

        # Weryfikacja konfiguracji (linki)
        assert config.base_url in survey.links.survey_url
