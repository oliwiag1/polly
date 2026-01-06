"""
Konfiguracja i fixture'y dla testów.
"""

import os
import pytest

from fastapi.testclient import TestClient

# Resetowanie singletonów przed testami
os.environ["POLLY_BASE_URL"] = "http://test.local"


@pytest.fixture(autouse=True)
def reset_singletons():
    """Resetuje singletony przed każdym testem."""
    # Reset Database singleton
    from app.database import DatabaseMeta

    if hasattr(DatabaseMeta, "_instances"):
        DatabaseMeta._instances.clear()

    # Reset ConfigManager singleton
    from app.config import ConfigMeta

    if hasattr(ConfigMeta, "_instances"):
        ConfigMeta._instances.clear()

    # Reset AppLogger singleton
    from app.logger import LoggerMeta

    if hasattr(LoggerMeta, "_instances"):
        LoggerMeta._instances.clear()

    yield

    # Cleanup po teście
    DatabaseMeta._instances.clear()
    ConfigMeta._instances.clear()
    LoggerMeta._instances.clear()


@pytest.fixture
def database():
    """Fixture zwracający czystą bazę danych."""
    from app.database import get_database

    db = get_database()
    db.clear()
    return db


@pytest.fixture
def config():
    """Fixture zwracający menedżer konfiguracji."""
    from app.config import get_config

    return get_config()


@pytest.fixture
def logger():
    """Fixture zwracający logger."""
    from app.logger import get_logger

    log = get_logger()
    log.reset_stats()
    return log


@pytest.fixture
def survey_service(database, config, logger):
    """Fixture zwracający serwis ankiet."""
    from app.services import SurveyService

    return SurveyService(database=database, config=config, logger=logger)


@pytest.fixture
def client(database):
    """Fixture zwracający klienta testowego FastAPI."""
    from app.main import create_app

    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_question_text():
    """Przykładowe pytanie tekstowe."""
    from app.models import Question, QuestionType

    return Question(
        id="q1",
        text="Jak masz na imię?",
        type=QuestionType.TEXT,
        required=True,
    )


@pytest.fixture
def sample_question_single_choice():
    """Przykładowe pytanie jednokrotnego wyboru."""
    from app.models import Question, QuestionType

    return Question(
        id="q2",
        text="Jaki jest Twój ulubiony kolor?",
        type=QuestionType.SINGLE_CHOICE,
        required=True,
        options=["Czerwony", "Niebieski", "Zielony"],
    )


@pytest.fixture
def sample_question_multiple_choice():
    """Przykładowe pytanie wielokrotnego wyboru."""
    from app.models import Question, QuestionType

    return Question(
        id="q3",
        text="Jakie języki programowania znasz?",
        type=QuestionType.MULTIPLE_CHOICE,
        required=False,
        options=["Python", "JavaScript", "Java", "C++"],
    )


@pytest.fixture
def sample_question_rating():
    """Przykładowe pytanie z oceną."""
    from app.models import Question, QuestionType

    return Question(
        id="q4",
        text="Oceń naszą usługę",
        type=QuestionType.RATING,
        required=True,
        min_rating=1,
        max_rating=10,
    )


@pytest.fixture
def sample_question_yes_no():
    """Przykładowe pytanie tak/nie."""
    from app.models import Question, QuestionType

    return Question(
        id="q5",
        text="Czy polecisz nas znajomym?",
        type=QuestionType.YES_NO,
        required=True,
    )


@pytest.fixture
def sample_survey_create(
    sample_question_text,
    sample_question_single_choice,
    sample_question_rating,
    sample_question_yes_no,
):
    """Przykładowe dane do utworzenia ankiety."""
    from app.models import SurveyCreate

    return SurveyCreate(
        title="Ankieta testowa",
        description="Opis ankiety testowej",
        questions=[
            sample_question_text,
            sample_question_single_choice,
            sample_question_rating,
            sample_question_yes_no,
        ],
    )


@pytest.fixture
def sample_survey_create_all_types(
    sample_question_text,
    sample_question_single_choice,
    sample_question_multiple_choice,
    sample_question_rating,
    sample_question_yes_no,
):
    """Ankieta ze wszystkimi typami pytań."""
    from app.models import SurveyCreate

    return SurveyCreate(
        title="Pełna ankieta testowa",
        description="Ankieta zawierająca wszystkie typy pytań",
        questions=[
            sample_question_text,
            sample_question_single_choice,
            sample_question_multiple_choice,
            sample_question_rating,
            sample_question_yes_no,
        ],
    )


@pytest.fixture
def created_survey(survey_service, sample_survey_create):
    """Fixture zwracający utworzoną ankietę."""
    return survey_service.create_survey(sample_survey_create)


@pytest.fixture
def sample_answers():
    """Przykładowe odpowiedzi do ankiety."""
    from app.models import Answer

    return [
        Answer(question_id="q1", value="Jan Kowalski"),
        Answer(question_id="q2", value="Niebieski"),
        Answer(question_id="q4", value=8),
        Answer(question_id="q5", value="yes"),
    ]


@pytest.fixture
def sample_answer_submit(sample_answers):
    """Przykładowe dane do przesłania odpowiedzi."""
    from app.models import AnswerSubmit

    return AnswerSubmit(
        answers=sample_answers,
        respondent_id="respondent-123",
    )
