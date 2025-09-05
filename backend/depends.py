from repositories.cv_analysis import JobRepository
from services.cv_analysis import AnalyseJobService
from configs.config import config

"""
Файл внедрения зависимостей.
Реализация паттерна 'Dependency Injection'.
"""

def get_analyse_job_service() -> AnalyseJobService:
    """ Проброс зависимостей для сервиса анализа резюме/вакансий. """

    job_repository = JobRepository()
    model_name = config["LLM"]["model_name"]
    model_temperature = config["LLM"]["temperature"]

    return  AnalyseJobService(job_repository)
