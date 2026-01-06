"""
Testy jednostkowe dla SurveyService.
"""

import pytest
from datetime import datetime
from uuid import uuid4


class TestSurveyServiceCreate:
    """Testy tworzenia ankiet."""

    def test_create_survey(self, survey_service, sample_survey_create):
        """Sprawdza tworzenie ankiety."""
        survey = survey_service.create_survey(sample_survey_create)

        assert survey.id is not None
        assert survey.title == sample_survey_create.title
        assert survey.description == sample_survey_create.description
        assert len(survey.questions) == len(sample_survey_create.questions)

    def test_create_survey_generates_links(
        self, survey_service, sample_survey_create, config
    ):
        """Sprawdza generowanie linków."""
        survey = survey_service.create_survey(sample_survey_create)

        assert survey.links is not None
        assert str(survey.id) in survey.links.survey_url
        assert str(survey.id) in survey.links.stats_url

    def test_create_survey_sets_created_at(self, survey_service, sample_survey_create):
        """Sprawdza ustawienie daty utworzenia."""
        before = datetime.now()
        survey = survey_service.create_survey(sample_survey_create)
        after = datetime.now()

        assert before <= survey.created_at <= after

    def test_create_survey_saves_to_database(
        self, survey_service, sample_survey_create, database
    ):
        """Sprawdza zapis do bazy danych."""
        survey = survey_service.create_survey(sample_survey_create)

        assert database.survey_exists(survey.id)
        assert database.get_survey(survey.id) == survey


class TestSurveyServiceGet:
    """Testy pobierania ankiet."""

    def test_get_survey(self, survey_service, created_survey):
        """Sprawdza pobieranie ankiety."""
        survey = survey_service.get_survey(created_survey.id)

        assert survey == created_survey

    def test_get_survey_not_found(self, survey_service):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        with pytest.raises(ValueError, match="not found"):
            survey_service.get_survey(uuid4())

    def test_get_all_surveys(self, survey_service, sample_survey_create):
        """Sprawdza pobieranie wszystkich ankiet."""
        survey1 = survey_service.create_survey(sample_survey_create)
        survey2 = survey_service.create_survey(sample_survey_create)

        all_surveys = survey_service.get_all_surveys()

        assert len(all_surveys) == 2
        survey_ids = [s.id for s in all_surveys]
        assert survey1.id in survey_ids
        assert survey2.id in survey_ids

    def test_get_all_surveys_empty(self, survey_service):
        """Sprawdza pustą listę ankiet."""
        all_surveys = survey_service.get_all_surveys()

        assert all_surveys == []


class TestSurveyServiceSubmitResponse:
    """Testy wysyłania odpowiedzi."""

    def test_submit_response(
        self, survey_service, created_survey, sample_answer_submit
    ):
        """Sprawdza wysyłanie odpowiedzi."""
        response = survey_service.submit_response(
            created_survey.id, sample_answer_submit
        )

        assert response.id is not None
        assert response.survey_id == created_survey.id
        assert response.respondent_id == sample_answer_submit.respondent_id

    def test_submit_response_saves_answers(
        self, survey_service, created_survey, sample_answer_submit
    ):
        """Sprawdza zapis odpowiedzi."""
        response = survey_service.submit_response(
            created_survey.id, sample_answer_submit
        )

        assert len(response.answers) == len(sample_answer_submit.answers)

    def test_submit_response_sets_timestamp(
        self, survey_service, created_survey, sample_answer_submit
    ):
        """Sprawdza ustawienie timestampu."""
        before = datetime.now()
        response = survey_service.submit_response(
            created_survey.id, sample_answer_submit
        )
        after = datetime.now()

        assert before <= response.submitted_at <= after

    def test_submit_response_survey_not_found(
        self, survey_service, sample_answer_submit
    ):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        with pytest.raises(ValueError, match="not found"):
            survey_service.submit_response(uuid4(), sample_answer_submit)

    def test_submit_response_missing_required(self, survey_service, created_survey):
        """Sprawdza błąd dla brakującej wymaganej odpowiedzi."""
        from app.models import AnswerSubmit, Answer

        # Tylko jedna odpowiedź, brakuje wymaganych
        incomplete = AnswerSubmit(
            answers=[Answer(question_id="q1", value="Test")],
        )

        with pytest.raises(ValueError, match="Required question"):
            survey_service.submit_response(created_survey.id, incomplete)

    def test_submit_response_unknown_question(self, survey_service, created_survey):
        """Sprawdza błąd dla nieznanego pytania."""
        from app.models import AnswerSubmit, Answer

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="unknown", value="Test"),
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q4", value=5),
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="not found in survey"):
            survey_service.submit_response(created_survey.id, invalid)


class TestSurveyServiceValidation:
    """Testy walidacji odpowiedzi."""

    def test_validate_text_answer_invalid_type(self, survey_service, created_survey):
        """Sprawdza walidację odpowiedzi tekstowej z błędnym typem."""
        from app.models import AnswerSubmit, Answer

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value=123),  # Powinno być string
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q4", value=5),
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="Text answer expected"):
            survey_service.submit_response(created_survey.id, invalid)

    def test_validate_single_choice_invalid_option(
        self, survey_service, created_survey
    ):
        """Sprawdza walidację opcji jednokrotnego wyboru."""
        from app.models import AnswerSubmit, Answer

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Żółty"),  # Nie ma takiej opcji
                Answer(question_id="q4", value=5),
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="Invalid option"):
            survey_service.submit_response(created_survey.id, invalid)

    def test_validate_rating_out_of_range(self, survey_service, created_survey):
        """Sprawdza walidację oceny poza zakresem."""
        from app.models import AnswerSubmit, Answer

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q4", value=15),  # Poza zakresem 1-10
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="Rating must be between"):
            survey_service.submit_response(created_survey.id, invalid)

    def test_validate_rating_invalid_type(self, survey_service, created_survey):
        """Sprawdza walidację typu oceny."""
        from app.models import AnswerSubmit, Answer

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q4", value="five"),  # Powinno być numeric
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="Numeric value expected"):
            survey_service.submit_response(created_survey.id, invalid)

    def test_validate_yes_no_invalid_value(self, survey_service, created_survey):
        """Sprawdza walidację odpowiedzi tak/nie."""
        from app.models import AnswerSubmit, Answer

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q4", value=5),
                Answer(question_id="q5", value="maybe"),  # Powinno być yes/no
            ],
        )

        with pytest.raises(ValueError, match="Yes/No answer expected"):
            survey_service.submit_response(created_survey.id, invalid)

    def test_validate_multiple_choice_not_list(
        self, survey_service, sample_survey_create_all_types
    ):
        """Sprawdza walidację wielokrotnego wyboru - nie lista."""
        from app.models import AnswerSubmit, Answer

        survey = survey_service.create_survey(sample_survey_create_all_types)

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q3", value="Python"),  # Powinno być listą
                Answer(question_id="q4", value=5),
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="List of options expected"):
            survey_service.submit_response(survey.id, invalid)

    def test_validate_multiple_choice_invalid_option(
        self, survey_service, sample_survey_create_all_types
    ):
        """Sprawdza walidację wielokrotnego wyboru - nieprawidłowa opcja."""
        from app.models import AnswerSubmit, Answer

        survey = survey_service.create_survey(sample_survey_create_all_types)

        invalid = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="Test"),
                Answer(question_id="q2", value="Niebieski"),
                Answer(question_id="q3", value=["Python", "Ruby"]),  # Ruby nie istnieje
                Answer(question_id="q4", value=5),
                Answer(question_id="q5", value="yes"),
            ],
        )

        with pytest.raises(ValueError, match="Invalid option"):
            survey_service.submit_response(survey.id, invalid)


class TestSurveyServiceStatistics:
    """Testy statystyk ankiet."""

    def test_get_statistics_empty(self, survey_service, created_survey):
        """Sprawdza statystyki bez odpowiedzi."""
        stats = survey_service.get_statistics(created_survey.id)

        assert stats.survey_id == created_survey.id
        assert stats.total_responses == 0
        assert len(stats.questions_stats) == len(created_survey.questions)

    def test_get_statistics_with_responses(
        self, survey_service, created_survey, sample_answer_submit
    ):
        """Sprawdza statystyki z odpowiedziami."""
        # Dodaj kilka odpowiedzi
        survey_service.submit_response(created_survey.id, sample_answer_submit)
        survey_service.submit_response(created_survey.id, sample_answer_submit)

        stats = survey_service.get_statistics(created_survey.id)

        assert stats.total_responses == 2
        assert stats.last_response_at is not None

    def test_get_statistics_rating_average(self, survey_service, created_survey):
        """Sprawdza średnią dla pytań z oceną."""
        from app.models import AnswerSubmit, Answer

        # Odpowiedzi z różnymi ocenami
        for rating in [3, 5, 7, 9]:
            submit = AnswerSubmit(
                answers=[
                    Answer(question_id="q1", value="Test"),
                    Answer(question_id="q2", value="Niebieski"),
                    Answer(question_id="q4", value=rating),
                    Answer(question_id="q5", value="yes"),
                ],
            )
            survey_service.submit_response(created_survey.id, submit)

        stats = survey_service.get_statistics(created_survey.id)

        # Znajdź statystyki dla pytania q4 (rating)
        rating_stats = next(q for q in stats.questions_stats if q.question_id == "q4")

        assert rating_stats.average_value == 6.0  # (3+5+7+9) / 4

    def test_get_statistics_survey_not_found(self, survey_service):
        """Sprawdza błąd dla nieistniejącej ankiety."""
        with pytest.raises(ValueError, match="not found"):
            survey_service.get_statistics(uuid4())

    def test_get_statistics_distribution_text(self, survey_service, created_survey):
        """Sprawdza rozkład odpowiedzi tekstowych."""
        from app.models import AnswerSubmit, Answer

        for name in ["Anna", "Anna", "Jan"]:
            submit = AnswerSubmit(
                answers=[
                    Answer(question_id="q1", value=name),
                    Answer(question_id="q2", value="Niebieski"),
                    Answer(question_id="q4", value=5),
                    Answer(question_id="q5", value="yes"),
                ],
            )
            survey_service.submit_response(created_survey.id, submit)

        stats = survey_service.get_statistics(created_survey.id)

        text_stats = next(q for q in stats.questions_stats if q.question_id == "q1")

        assert text_stats.answer_distribution["Anna"] == 2
        assert text_stats.answer_distribution["Jan"] == 1

    def test_get_statistics_distribution_yes_no(self, survey_service, created_survey):
        """Sprawdza rozkład odpowiedzi tak/nie."""
        from app.models import AnswerSubmit, Answer

        for answer in ["yes", True, "no", False]:
            submit = AnswerSubmit(
                answers=[
                    Answer(question_id="q1", value="Test"),
                    Answer(question_id="q2", value="Niebieski"),
                    Answer(question_id="q4", value=5),
                    Answer(question_id="q5", value=answer),
                ],
            )
            survey_service.submit_response(created_survey.id, submit)

        stats = survey_service.get_statistics(created_survey.id)

        yes_no_stats = next(q for q in stats.questions_stats if q.question_id == "q5")

        assert yes_no_stats.answer_distribution["yes"] == 2
        assert yes_no_stats.answer_distribution["no"] == 2

    def test_get_statistics_distribution_multiple_choice(
        self, survey_service, sample_survey_create_all_types
    ):
        """Sprawdza rozkład odpowiedzi wielokrotnego wyboru."""
        from app.models import AnswerSubmit, Answer

        survey = survey_service.create_survey(sample_survey_create_all_types)

        for choices in [["Python"], ["Python", "JavaScript"], ["Java"]]:
            submit = AnswerSubmit(
                answers=[
                    Answer(question_id="q1", value="Test"),
                    Answer(question_id="q2", value="Niebieski"),
                    Answer(question_id="q3", value=choices),
                    Answer(question_id="q4", value=5),
                    Answer(question_id="q5", value="yes"),
                ],
            )
            survey_service.submit_response(survey.id, submit)

        stats = survey_service.get_statistics(survey.id)

        mc_stats = next(q for q in stats.questions_stats if q.question_id == "q3")

        assert mc_stats.answer_distribution["Python"] == 2
        assert mc_stats.answer_distribution["JavaScript"] == 1
        assert mc_stats.answer_distribution["Java"] == 1


class TestSurveyServiceGenerateLinks:
    """Testy generowania linków."""

    def test_generate_links_uses_config_base_url(self, survey_service, config):
        """Sprawdza czy linki używają URL z konfiguracji."""
        from uuid import uuid4

        survey_id = uuid4()
        links = survey_service._generate_links(survey_id)

        assert config.base_url in links.survey_url
        assert config.base_url in links.stats_url
