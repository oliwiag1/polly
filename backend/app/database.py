from datetime import datetime
from threading import Lock
from typing import Any
from uuid import UUID

from app.models.survey import Survey, SurveyResponse


# Metaklasa niezbędna aby stworzyć singletona
class DatabaseMeta(type):
    _instances: dict[type, Any] = {}

    # Blokada aby singleton był bezpieczny wątkowo (tylko jeden wątek może coś robić)
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


# Baza danych w pamięci jako singleton (tylko jeden obiekt w całym programie)
class Database(metaclass=DatabaseMeta):
    # Konstruktor
    def __init__(self) -> None:
        self._surveys: dict[UUID, Survey] = {}
        self._responses: dict[UUID, list[SurveyResponse]] = {}
        self._lock = Lock()
        self._initialized_at = datetime.now()

    # Pobranie wszystkich ankiet
    @property
    def surveys(self) -> dict[UUID, Survey]:
        return self._surveys

    # Pobranie wszystkich odpowiedzi
    @property
    def responses(self) -> dict[UUID, list[SurveyResponse]]:
        return self._responses

    # Stworzenie ankiety
    def add_survey(self, survey: Survey) -> None:
        with self._lock:
            self._surveys[survey.id] = survey
            self._responses[survey.id] = []

    # Pobranie formularza ankiety
    def get_survey(self, survey_id: UUID) -> Survey | None:
        return self._surveys.get(survey_id)

    # Dodanie odpowiedzi do ankiety
    def add_response(self, response: SurveyResponse) -> None:
        with self._lock:
            if response.survey_id in self._responses:
                self._responses[response.survey_id].append(response)

    # Pobranie odpowiedzi do danej ankiety
    def get_responses(self, survey_id: UUID) -> list[SurveyResponse]:
        return self._responses.get(survey_id, [])

    # Sprawdzenie czy ankieta istnieje
    def survey_exists(self, survey_id: UUID) -> bool:
        return survey_id in self._surveys

    # Pobranie ogólnych statystyk ankiet
    def get_stats(self) -> dict[str, Any]:
        return {
            "total_surveys": len(self._surveys),
            "total_responses": sum(len(r) for r in self._responses.values()),
            "initialized_at": self._initialized_at.isoformat(),
        }

    # Wyczyszczenie bazy danych
    def clear(self) -> None:
        with self._lock:
            self._surveys.clear()
            self._responses.clear()


# Pobranie obiektu bazy danych
def get_database() -> Database:
    return Database()
