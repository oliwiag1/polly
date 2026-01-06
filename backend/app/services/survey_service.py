from collections import Counter
from datetime import datetime
from uuid import UUID, uuid4

from app.config import ConfigManager, get_config
from app.database import Database, get_database
from app.decorators import measure_time
from app.logger import AppLogger, get_logger
from app.models import (
    Answer,
    AnswerSubmit,
    Question,
    QuestionStats,
    QuestionType,
    Survey,
    SurveyCreate,
    SurveyLinks,
    SurveyResponse,
    SurveyStats,
)


class SurveyService:
    
    def __init__(
        self, 
        database: Database | None = None,
        config: ConfigManager | None = None,
        logger: AppLogger | None = None,
    ) -> None:
        self._db = database or get_database()
        self._config = config or get_config()
        self._logger = logger or get_logger()

    # Funkcja tworząca ankietę
    @measure_time
    def create_survey(self, survey_data: SurveyCreate) -> Survey:
        survey_id = uuid4()

        # Wygenerowanie linku do ankiety
        links = self._generate_links(survey_id)

        # Stworzenie rekordu ankiety do bazy danych
        survey = Survey(
            id=survey_id,
            title=survey_data.title,
            description=survey_data.description,
            questions=survey_data.questions,
            created_at=datetime.now(),
            links=links,
        )

        # Zapisanie ankiety w bazie danych
        self._db.add_survey(survey)
        return survey

    # Funkcja generująca linki do ankiety i statystyk ankiety
    def _generate_links(self, survey_id: UUID) -> SurveyLinks:
        base_url = self._config.base_url
        return SurveyLinks(
            survey_url=f"{base_url}/surveys/{survey_id}",
            stats_url=f"{base_url}/surveys/{survey_id}/stats",
        )

    # Pobranie ankiety na podstawie jej identyfikatora
    @measure_time
    def get_survey(self, survey_id: UUID) -> Survey:
        survey = self._db.get_survey(survey_id)
        if survey is None:
            raise ValueError(f"Survey with ID {survey_id} not found")
        return survey

    # Wysłanie odpowiedzi do ankiety
    @measure_time
    def submit_response(
        self, 
        survey_id: UUID, 
        answer_data: AnswerSubmit
    ) -> SurveyResponse:
        survey = self.get_survey(survey_id)

        # Sprawdzenie poprawności wypełnionych odpowiedzi
        self._validate_answers(survey, answer_data.answers)

        # Stworzenie rekordu z odpowiedzią dla bazy danych
        response = SurveyResponse(
            id=uuid4(),
            survey_id=survey_id,
            answers=answer_data.answers,
            respondent_id=answer_data.respondent_id,
            submitted_at=datetime.now(),
        )

        # Dodanie odpowiedzi do bazy danych
        self._db.add_response(response)
        return response

    # Funkcja sprawdzająca poprawność odpowiedzi
    def _validate_answers(
        self, 
        survey: Survey, 
        answers: list[Answer]
    ) -> None:
        question_map = {q.id: q for q in survey.questions}
        answered_ids = {a.question_id for a in answers}

        # Sprawdzenie czy wszystkie wymagane pytania mają odpowiedź
        for question in survey.questions:
            if question.required and question.id not in answered_ids:
                raise ValueError(
                    f"Required question '{question.text}' was not answered"
                )

        # Sprawdzenie czy odpowiedź na pytanie jest poprawna
        for answer in answers:

            # Jeżeli nie istnieje pytanie dla ankiety
            if answer.question_id not in question_map:
                raise ValueError(
                    f"Question with ID {answer.question_id} not found in survey"
                )
            
            question = question_map[answer.question_id]
            self._validate_single_answer(question, answer)

    # Funkcja sprawdzająca pojedynczą odpowiedź
    def _validate_single_answer(self, question: Question, answer: Answer) -> None:
        value = answer.value

        match question.type:
            # Jeżeli pytanie jest tekstowe -> sprawdzenie czy pole wypełniono jako string
            case QuestionType.TEXT:
                if not isinstance(value, str):
                    raise ValueError(f"Text answer expected for question {question.id}")

            # Jeżeli pytanie jest jednokrotnego wyboru -> sprawdzenie czy odpowiedź jest możliwa
            case QuestionType.SINGLE_CHOICE:
                if question.options and value not in question.options:
                    raise ValueError(
                        f"Invalid option '{value}' for question {question.id}"
                    )

            # Jeżeli pytanie wielokrotnego wyboru -> sprawdzenie czy pole jest listą oraz czy nie posiada niedozwolonych wartości
            case QuestionType.MULTIPLE_CHOICE:
                if not isinstance(value, list):
                    raise ValueError(
                        f"List of options expected for question {question.id}"
                    )
                if question.options:
                    for v in value:
                        if v not in question.options:
                            raise ValueError(
                                f"Invalid option '{v}' for question {question.id}"
                            )

            # Jeżeli pole jest oceną -> sprawdzenie czy pole jest cyfrą oraz czy mieści się w zakresie od-do
            case QuestionType.RATING:
                if not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Numeric value expected for question {question.id}"
                    )
                min_val = question.min_rating or 1
                max_val = question.max_rating or 5
                if not min_val <= value <= max_val:
                    raise ValueError(
                        f"Rating must be between {min_val} and {max_val}"
                    )

            # Jeżeli pole typu tak/nie -> sprawdzenie czy wartość pola jest 'yes', 'no', True lub False
            case QuestionType.YES_NO:
                if value not in ("yes", "no", True, False):
                    raise ValueError(
                        f"Yes/No answer expected for question {question.id}"
                    )

    # Funkcja obliczająca statystyki ankiety
    @measure_time
    def get_statistics(self, survey_id: UUID) -> SurveyStats:
        survey = self.get_survey(survey_id)
        responses = self._db.get_responses(survey_id)

        # Pobranie statystyk odpowiedzi
        questions_stats = [
            self._calculate_question_stats(question, responses)
            for question in survey.questions
        ]
        
        last_response_at = None
        if responses:
            last_response_at = max(r.submitted_at for r in responses)
        
        return SurveyStats(
            survey_id=survey_id,
            survey_title=survey.title,
            total_responses=len(responses),
            questions_stats=questions_stats,
            created_at=survey.created_at,
            last_response_at=last_response_at,
        )

    # Funkcja obliczająca statystyki dla pytania
    def _calculate_question_stats(
        self, 
        question: Question, 
        responses: list[SurveyResponse]
    ) -> QuestionStats:
        # Collect all answers for this question
        answers = []
        for response in responses:
            for answer in response.answers:
                if answer.question_id == question.id:
                    answers.append(answer.value)

        # Obliczenie rozkładu odpowiedzi
        distribution = self._calculate_distribution(question.type, answers)
        
        average = None
        # Obliczenie średniej wartości dla pytań o typie ocena
        if question.type == QuestionType.RATING and answers:
            numeric_answers = [a for a in answers if isinstance(a, (int, float))]
            if numeric_answers:
                average = sum(numeric_answers) / len(numeric_answers)

        # Zwrócenie odpowiedzi
        return QuestionStats(
            question_id=question.id,
            question_text=question.text,
            question_type=question.type,
            total_responses=len(answers),
            answer_distribution=distribution,
            average_value=average,
        )

    # Obliczenie rozkładu odpowiedzi dla pytania
    def _calculate_distribution(
        self, 
        question_type: QuestionType, 
        answers: list
    ) -> dict[str, int]:
        if not answers:
            return {}
        
        match question_type:

            # Jeżeli odpowiedzią na pytanie jest tekst -> Zliczenie częstotliwości występowania tekstu
            case QuestionType.TEXT:
                return dict(Counter(str(a) for a in answers))

            # Jeżeli wielokrotny wybór -> Zliczenie częstotliwości odpowiedzi
            case QuestionType.MULTIPLE_CHOICE:
                flat_answers = []
                for answer in answers:
                    if isinstance(answer, list):
                        flat_answers.extend(answer)
                    else:
                        flat_answers.append(answer)
                return dict(Counter(str(a) for a in flat_answers))

            # Jeżeli odpowiedź yes/no -> zliczenie odpowiedzi
            case QuestionType.YES_NO:
                normalized = []
                for a in answers:
                    if a in (True, "yes"):
                        normalized.append("yes")
                    else:
                        normalized.append("no")
                return dict(Counter(normalized))
            
            case _:
                return dict(Counter(str(a) for a in answers))

    # Funkcja pobierająca wszystkie ankiety
    def get_all_surveys(self) -> list[Survey]:
        return list(self._db.surveys.values())
