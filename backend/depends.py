from repositories.cv_analysis import VacancyRepository
from services.cv_analysis import CVAnalysisService
from configs.config import config

"""
Файл внедрения зависимостей.
Реализация паттерна 'Dependency Injection'.
"""

def get_analyse_job_service() -> CVAnalysisService:
    """ Проброс зависимостей для сервиса анализа резюме/вакансий. """

    job_repository = VacancyRepository()
    model_name = config["LLM"]["model_name"]
    model_temperature = config["LLM"]["temperature"]

    return  AnalyseJobService(job_repository)
