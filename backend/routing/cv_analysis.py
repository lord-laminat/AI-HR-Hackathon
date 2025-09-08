from typing import List
from fastapi import APIRouter, Depends

from depends import get_job_service
from schemas.cv_analysis import VacancyMatchingReport
from services.cv_analysis import CVAnalysisService

router = APIRouter(tags=["CV analysis"])


@router.post(
    "/analyse_cv",
    responses={400: {"description": "Bad request"}},
    response_model=VacancyMatchingReport,
    description="Поиск подходящих под резюме вакансий",
)
async def get_matching_vacancies(
    cv_description: str, cv_analysis_service: CVAnalysisService = Depends(get_job_service)
) -> List[VacancyMatchingReport]:
    """
    Ручка принимает резюме соискателя и возвращяет ему
    ответ от сервиса по анализу и поиску подходящих вакансий.
    """
    return cv_analysis_service.analyse(cv_description)
