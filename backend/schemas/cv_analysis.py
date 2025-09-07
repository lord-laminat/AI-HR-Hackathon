from pydantic import BaseModel
from typing import List


class VacancyMatchingReport(BaseModel):
    """
    Объект, содержащий название конкретной вакансии и
    долю соответствия присланному ранее резюме.
    """
    vacancy_title: str
    matching: float


class JobParameters(BaseModel):
    """ 
    Объект, описывающий параметры, по которым
    определяется соответствие кандидата вакансии.
    """
    experience_years: float
    hard_skills: List[Tuple[str, int]]
    soft_skills: List[Tuple[str, int]]


class JobDescription(BaseModel):
    """
    Объект, содержащий текст вакансии или резюме.
    """
    title: str
    text: str
