from typing import List
from fastapi import APIRouter, Depends

from depends import get_job_service
from schemas.cv_analysis import VacancyMatchingReport
from services.cv_analysis import AnalyseJobService

router = APIRouter(tags=["CV analysis"])


@router.post(
    "analyse_cv",
    responses={400: {"description": "Bad request"}},
    response_model=VacancyMatchingReport,
    description="Поиск подходящих под резюме вакансий",
)
async def get_all_books(
    book_service: BookService = Depends(get_job_service),
) -> List[VacancyMatchingReport]:
    """
    Ручка принимает резюме соискателя и возвращяет ему
    ответ от сервиса по анализу и поиску подходящих вакансий.
    """
    ...
    # TODO: реализовать ручку для поиска вакансий по резюме
