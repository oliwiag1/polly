"""
Testy jednostkowe dla modeli Pydantic.
"""

import pytest
from datetime import datetime
from uuid import uuid4


class TestQuestionModel:
    """Testy dla modelu Question."""

    def test_create_text_question(self):
        """Sprawdza tworzenie pytania tekstowego."""
        from app.models import Question, QuestionType

        question = Question(
            id="q1",
            text="Jak masz na imię?",
            type=QuestionType.TEXT,
        )

        assert question.id == "q1"
        assert question.type == QuestionType.TEXT
        assert question.required is True  # domyślnie

    def test_create_choice_question_with_options(self):
        """Sprawdza tworzenie pytania z opcjami."""
        from app.models import Question, QuestionType

        question = Question(
            id="q1",
            text="Wybierz kolor",
            type=QuestionType.SINGLE_CHOICE,
            options=["Czerwony", "Niebieski"],
        )

        assert question.options == ["Czerwony", "Niebieski"]

    def test_create_rating_question(self):
        """Sprawdza tworzenie pytania z oceną."""
        from app.models import Question, QuestionType

        question = Question(
            id="q1",
            text="Oceń",
            type=QuestionType.RATING,
            min_rating=1,
            max_rating=10,
        )

        assert question.min_rating == 1
        assert question.max_rating == 10

    def test_question_text_validation_min_length(self):
        """Sprawdza walidację minimalnej długości tekstu."""
        from app.models import Question, QuestionType
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Question(
                id="q1",
                text="",  # Za krótki
                type=QuestionType.TEXT,
            )

    def test_question_text_validation_max_length(self):
        """Sprawdza walidację maksymalnej długości tekstu."""
        from app.models import Question, QuestionType
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Question(
                id="q1",
                text="x" * 501,  # Za długi
                type=QuestionType.TEXT,
            )


class TestSurveyCreateModel:
    """Testy dla modelu SurveyCreate."""

    def test_create_survey(self):
        """Sprawdza tworzenie ankiety."""
        from app.models import SurveyCreate, Question, QuestionType

        survey = SurveyCreate(
            title="Test Survey",
            description="Test Description",
            questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
        )

        assert survey.title == "Test Survey"
        assert len(survey.questions) == 1

    def test_create_survey_without_description(self):
        """Sprawdza tworzenie ankiety bez opisu."""
        from app.models import SurveyCreate, Question, QuestionType

        survey = SurveyCreate(
            title="Test",
            questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
        )

        assert survey.description is None

    def test_survey_title_validation_min_length(self):
        """Sprawdza walidację minimalnej długości tytułu."""
        from app.models import SurveyCreate, Question, QuestionType
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SurveyCreate(
                title="",  # Za krótki
                questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
            )

    def test_survey_title_validation_max_length(self):
        """Sprawdza walidację maksymalnej długości tytułu."""
        from app.models import SurveyCreate, Question, QuestionType
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SurveyCreate(
                title="x" * 201,  # Za długi
                questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
            )

    def test_survey_requires_questions(self):
        """Sprawdza czy ankieta wymaga przynajmniej jednego pytania."""
        from app.models import SurveyCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SurveyCreate(
                title="Test",
                questions=[],  # Puste
            )


class TestAnswerModel:
    """Testy dla modelu Answer."""

    def test_create_text_answer(self):
        """Sprawdza tworzenie odpowiedzi tekstowej."""
        from app.models import Answer

        answer = Answer(question_id="q1", value="Test answer")

        assert answer.question_id == "q1"
        assert answer.value == "Test answer"

    def test_create_numeric_answer(self):
        """Sprawdza tworzenie odpowiedzi numerycznej."""
        from app.models import Answer

        answer = Answer(question_id="q1", value=5)

        assert answer.value == 5

    def test_create_list_answer(self):
        """Sprawdza tworzenie odpowiedzi z listą."""
        from app.models import Answer

        answer = Answer(question_id="q1", value=["opt1", "opt2"])

        assert answer.value == ["opt1", "opt2"]

    def test_create_boolean_answer(self):
        """Sprawdza tworzenie odpowiedzi boolean."""
        from app.models import Answer

        answer = Answer(question_id="q1", value=True)

        assert answer.value is True


class TestAnswerSubmitModel:
    """Testy dla modelu AnswerSubmit."""

    def test_create_answer_submit(self):
        """Sprawdza tworzenie przesłania odpowiedzi."""
        from app.models import AnswerSubmit, Answer

        submit = AnswerSubmit(
            answers=[
                Answer(question_id="q1", value="test"),
            ],
            respondent_id="user-123",
        )

        assert len(submit.answers) == 1
        assert submit.respondent_id == "user-123"

    def test_create_anonymous_submit(self):
        """Sprawdza anonimowe przesłanie."""
        from app.models import AnswerSubmit, Answer

        submit = AnswerSubmit(
            answers=[Answer(question_id="q1", value="test")],
        )

        assert submit.respondent_id is None


class TestSurveyModel:
    """Testy dla modelu Survey."""

    def test_create_survey(self):
        """Sprawdza tworzenie pełnego modelu ankiety."""
        from app.models import Survey, Question, QuestionType, SurveyLinks

        survey_id = uuid4()
        survey = Survey(
            id=survey_id,
            title="Test Survey",
            description="Description",
            questions=[Question(id="q1", text="Test?", type=QuestionType.TEXT)],
            created_at=datetime.now(),
            links=SurveyLinks(
                survey_url="http://test/1",
                stats_url="http://test/1/stats",
            ),
        )

        assert survey.id == survey_id
        assert survey.links.survey_url == "http://test/1"


class TestSurveyResponseModel:
    """Testy dla modelu SurveyResponse."""

    def test_create_survey_response(self):
        """Sprawdza tworzenie odpowiedzi na ankietę."""
        from app.models import SurveyResponse, Answer

        response_id = uuid4()
        survey_id = uuid4()

        response = SurveyResponse(
            id=response_id,
            survey_id=survey_id,
            answers=[Answer(question_id="q1", value="test")],
            respondent_id="user-123",
            submitted_at=datetime.now(),
        )

        assert response.id == response_id
        assert response.survey_id == survey_id


class TestQuestionStatsModel:
    """Testy dla modelu QuestionStats."""

    def test_create_question_stats(self):
        """Sprawdza tworzenie statystyk pytania."""
        from app.models import QuestionStats, QuestionType

        stats = QuestionStats(
            question_id="q1",
            question_text="Test?",
            question_type=QuestionType.TEXT,
            total_responses=10,
            answer_distribution={"yes": 5, "no": 5},
            average_value=None,
        )

        assert stats.total_responses == 10

    def test_create_rating_stats_with_average(self):
        """Sprawdza statystyki z średnią."""
        from app.models import QuestionStats, QuestionType

        stats = QuestionStats(
            question_id="q1",
            question_text="Rate?",
            question_type=QuestionType.RATING,
            total_responses=5,
            answer_distribution={"4": 2, "5": 3},
            average_value=4.6,
        )

        assert stats.average_value == 4.6


class TestSurveyStatsModel:
    """Testy dla modelu SurveyStats."""

    def test_create_survey_stats(self):
        """Sprawdza tworzenie statystyk ankiety."""
        from app.models import SurveyStats, QuestionStats, QuestionType

        survey_id = uuid4()
        stats = SurveyStats(
            survey_id=survey_id,
            survey_title="Test Survey",
            total_responses=100,
            questions_stats=[
                QuestionStats(
                    question_id="q1",
                    question_text="Test?",
                    question_type=QuestionType.TEXT,
                    total_responses=100,
                )
            ],
            created_at=datetime.now(),
            last_response_at=datetime.now(),
        )

        assert stats.total_responses == 100


class TestQuestionType:
    """Testy dla enuma QuestionType."""

    def test_all_question_types(self):
        """Sprawdza wszystkie typy pytań."""
        from app.models import QuestionType

        assert QuestionType.TEXT.value == "text"
        assert QuestionType.SINGLE_CHOICE.value == "single_choice"
        assert QuestionType.MULTIPLE_CHOICE.value == "multiple_choice"
        assert QuestionType.RATING.value == "rating"
        assert QuestionType.YES_NO.value == "yes_no"
