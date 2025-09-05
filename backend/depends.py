from repositories.cv_analysis import JobRepository
from services.cv_analysis import AnalyseJobService

"""
Файл внедрения зависимостей.
Реализация паттерна 'Dependency Injection'.
"""

def get_job_service() -> AnalyseJobService:
    """
    Проброс зависимостей для сервиса анализа резюме/вакансий.
    """
    job_repository = JobRepository()
    analyse_job_service = AnalyseJobService(job_repository)

    return analyse_job_service
