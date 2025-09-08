from repositories.cv_analysis import VacancyRepository
from services.cv_analysis import CVAnalysisService
from configparser import ConfigParser
"""
Файл внедрения зависимостей.
Реализация паттерна 'Dependency Injection'.
"""

config = ConfigParser()
config.read("./configs/config.ini")

def get_analyse_job_service() -> CVAnalysisService:
    """ Проброс зависимостей для сервиса анализа резюме/вакансий. """

    job_repository = VacancyRepository()
    model_name = config["llm"]["model_name"]
    model_temperature = config["llm"]["temperature"]

    return  CVAnalysisService(job_repository, model_name, model_temperature)
