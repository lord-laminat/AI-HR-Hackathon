import os

from schemas.cv_analysis import JobDescription
from repositories.cv_analysis import JobRepository, JobParameters, VacancyMatchingReport


class AnalyseJobService:
    """
    Сервис по определению ключевых параметров
    в вакансии/резюме и формированию ответа пользователю.
    """

    def __init__(
            self,
            repository: JobRepository,
            model_name: str,
            temperature: float
    ) -> None:
        self.repository = repository
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature
        )


    def _get_job_parameters(self, job: JobDescription) -> JobParameters:
        """
        Вызов ИИ-агента для формирования
        описания вакансии/резюме.
        """
        ...
        # TODO: Реализовать ИИ-агента, способного анализировать вакансии и резюме.
    

    def _compare_resume_with_vacancy(
            self,
            resume: JobParameters,
            vacancy: JobParameters
    ) -> VacancyMatchingReport:
        """
        Сравнение параметров соискателя с параметрами вакансии.
        """
        # TODO: Реализовать ИИ-агента, способного сравнивать параметры вакансии и резюме.
        ...
