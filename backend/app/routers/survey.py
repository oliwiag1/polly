from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import Database, get_database
from app.decorators import handle_exceptions, log_execution, rate_limit
from app.models import (
    AnswerSubmit,
    Survey,
    SurveyCreate,
    SurveyResponse,
    SurveyStats,
)
from app.services import SurveyService

router = APIRouter(prefix="/surveys", tags=["surveys"])


def get_survey_service(db: Database = Depends(get_database)) -> SurveyService:
    return SurveyService(db)


# Endpoint na stworzenie ankiety
@router.post(
    "/",
    response_model=Survey,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new survey",
    description="Create a new survey with questions. Returns the survey with generated links.",
)
@handle_exceptions
@log_execution
async def create_survey(
    survey_data: SurveyCreate,
    service: SurveyService = Depends(get_survey_service)) -> Survey:
    return service.create_survey(survey_data)


# Endpoint na pobranie wszystkich ankiet
@router.get(
    "/",
    response_model=list[Survey],
    summary="Get all surveys",
    description="Retrieve a list of all surveys.",
)
@handle_exceptions
@log_execution
async def get_all_surveys(service: SurveyService = Depends(get_survey_service)) -> list[Survey]:
    return service.get_all_surveys()


# Endpoint na pobranie ankiety do wypełnienia na podstawie jej identyfikatora
@router.get(
    "/{survey_id}",
    response_model=Survey,
    summary="Get survey by ID",
    description="Retrieve a specific survey by its UUID to fill it out.",
)
@handle_exceptions
@log_execution
async def get_survey(
    survey_id: UUID,
    service: SurveyService = Depends(get_survey_service),
) -> Survey:
    try:
        return service.get_survey(survey_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Endpoint na wysyłanie odpowiedzi do ankiety
@router.post(
    "/{survey_id}/responses",
    response_model=SurveyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit survey response",
    description="Submit answers for a specific survey.",
)
@handle_exceptions
@log_execution
@rate_limit(max_calls=100, time_window=60)  # 100 submissions per minute
async def submit_response(
    survey_id: UUID,
    answer_data: AnswerSubmit,
    service: SurveyService = Depends(get_survey_service),
) -> SurveyResponse:
    try:
        return service.submit_response(survey_id, answer_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint na pobranie statystyk ankiety
@router.get(
    "/{survey_id}/stats",
    response_model=SurveyStats,
    summary="Get survey statistics",
    description="Retrieve statistics for a specific survey including response counts and distributions.",
)
@handle_exceptions
@log_execution
async def get_survey_stats(
    survey_id: UUID,
    service: SurveyService = Depends(get_survey_service),
) -> SurveyStats:
    try:
        return service.get_statistics(survey_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
