from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Typ pytania
class QuestionType(str, Enum):

    TEXT = "text"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    RATING = "rating"
    YES_NO = "yes_no"


# Pojedyncze pytanie z ankiety
class Question(BaseModel):

    id: str = Field(..., description="Unique identifier for the question")
    text: str = Field(..., min_length=1, max_length=500, description="Question text")
    type: QuestionType = Field(..., description="Type of the question")
    required: bool = Field(default=True, description="Whether the question is required")
    options: list[str] | None = Field(
        default=None, 
        description="Available options for choice questions"
    )
    min_rating: int | None = Field(default=1, description="Minimum rating value")
    max_rating: int | None = Field(default=5, description="Maximum rating value")

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str] | None, info) -> list[str] | None:
        return v


# Obiekt tworzący ankietę (przychodzi z frontendu)
class SurveyCreate(BaseModel):

    title: str = Field(..., min_length=1, max_length=200, description="Survey title")
    description: str | None = Field(
        default=None, 
        max_length=1000, 
        description="Survey description"
    )
    questions: list[Question] = Field(
        ..., 
        min_length=1, 
        description="List of survey questions"
    )

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v: list[Question]) -> list[Question]:
        if not v:
            raise ValueError("Survey must have at least one question")
        return v


# Klasa na linki do statystyk oraz ankiety
class SurveyLinks(BaseModel):

    survey_url: str = Field(..., description="URL to access and fill the survey")
    stats_url: str = Field(..., description="URL to view survey statistics")


# Klasa reprezentująca ankietę w bazie danych
class Survey(BaseModel):

    id: UUID = Field(..., description="Unique survey identifier")
    title: str = Field(..., description="Survey title")
    description: str | None = Field(default=None, description="Survey description")
    questions: list[Question] = Field(..., description="List of survey questions")
    created_at: datetime = Field(..., description="Survey creation timestamp")
    links: SurveyLinks = Field(..., description="Survey URLs")


# Klasa reprezentująca odpowiedz w bazie danych
class Answer(BaseModel):

    question_id: str = Field(..., description="ID of the answered question")
    value: Any = Field(..., description="Answer value")


# Klasa reprezentująca odpowiedź (przychodzi z frontendu)
class AnswerSubmit(BaseModel):

    answers: list[Answer] = Field(..., description="List of answers")
    respondent_id: str | None = Field(
        default=None, 
        description="Optional respondent identifier"
    )

# Klasa reprezentująca odpowiedzi na ankietę w bazie danych
class SurveyResponse(BaseModel):

    id: UUID = Field(..., description="Unique response identifier")
    survey_id: UUID = Field(..., description="Associated survey ID")
    answers: list[Answer] = Field(..., description="List of answers")
    respondent_id: str | None = Field(default=None, description="Respondent identifier")
    submitted_at: datetime = Field(..., description="Response submission timestamp")


# Klasa reprezentująca statystyki pytania z ankiety
class QuestionStats(BaseModel):

    question_id: str = Field(..., description="Question identifier")
    question_text: str = Field(..., description="Question text")
    question_type: QuestionType = Field(..., description="Question type")
    total_responses: int = Field(..., description="Total number of responses")

    # Rozkład odpowiedzi
    answer_distribution: dict[str, int] = Field(
        default_factory=dict, 
        description="Distribution of answers"
    )

    # Typowa odpowiedź
    average_value: float | None = Field(
        default=None, 
        description="Average value for numeric questions"
    )


# Statystyki odpowiedzi
class SurveyStats(BaseModel):

    survey_id: UUID = Field(..., description="Survey identifier")
    survey_title: str = Field(..., description="Survey title")
    total_responses: int = Field(..., description="Total number of responses")

    # Statystyki pytań
    questions_stats: list[QuestionStats] = Field(
        ..., 
        description="Statistics for each question"
    )
    created_at: datetime = Field(..., description="Survey creation timestamp")

    # Data ostatniej odpowiedzi
    last_response_at: datetime | None = Field(
        default=None, 
        description="Timestamp of last response"
    )
