import os
import asyncio
import json
import re
from typing import TypedDict, Dict, Tuple, List, Any
from enum import Enum
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from schemas.cv_analysis import JobDescription
from repositories.cv_analysis import VacancyRepository, JobParameters, VacancyMatchingReport


class State(TypedDict):
    """
    Описание параметров, к которым имеет
    доступ агент во время работы.
    """
    cv_description: str
    cv_parameters: JobParameters
    vacancies_list: List[str]
    vacancies_parameters: List[JobParameters]


class CVAnalyseService:
    """
    Сервис по определению ключевых параметров
    в резюме и формированию объекта JobParameters.
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
        self.workflow = self._create_workflow()


    def _create_workflow(self) -> StateGraph:
        """ Создание графа, описывающего рабочий процесс агента. """
        workflow = StateGraph(State)

        # Узлы графа
        workflow.add_node("analyse_cv", self._analyse_cv)
        workflow.add_node("get_vacancies_list", self._get_vacancies_list)
        workflow.add_node("analyse_vacancies", self._analyse_vacancies)
        workflow.add_node("compare_cv_with_vacancies", self._compare_cv_with_vacancies)

        # Ребра графа
        workflow.set_entry_point("analyse_cv")
        workflow.add_edge("analyse_cv", "get_vacancies_list")
        workflow.add_edge("get_vacancies_list", "analyse_vacancies")
        workflow.add_edge("analyse_vacancies", "compare_cv_with_vacancies")
        workflow.add_edge("compare_cv_with_vacancies", END)

        return workflow.compile()


    def _analyse_cv(self, state: State) -> Dict[str, JobParameters]:
        """ Узел анализа резюме кандидата. """
        cv_parameters = JobParameters()

        cv_parameters.experience_years = self._get_experience(state["cv_description"])
        cv_parameters.hard_skills = self._get_hard_skills(state["cv_description"])
        cv_parameters.soft_skills = list()

        return { "cv_parameters": cv_parameters }


    def _get_experience(self, cv_description: str) -> float:
        """ Функция узла '_analyse_cv' для определения опыта  """
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Ты - HR агент. Твоя задача - оценить способности кандидата по его резюме.
            Выяви из него опыт работы кандидата и ответь одним числом - количеством лет опыта.
            (можно использовать дробное число с разделителем - '.')
            Пример ответа: 3.25

            Проанализируй следующее резюме:
            # начало описания
            {description}
            # конец описания

            Ответ: 
            """
        )

        message = HumanMessage(content=prompt.format(description=cv_description))
        response = await self.llm.ainvoke([message])

        experience = re.search(r"\d+.?\d*", response.content).group()

        return float(experience)


    def _get_hard_skills(self, cv_description: str) -> List[Tuple[str, int]]:
        """ Функция узла '_analyse_cv' для определения хард скилов в резюме кандидата. """
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Ты - HR агент. Твоя задача - оценить способности кандидата по его резюме.
            Выяви из него хард скилы и, учитывая описание опыта работы кандидата, оцени их по шкале от 1 до 3. 
            
            Проанализируй следующее резюме:
            # начало описания
            {description}
            # конец описания

            Строго соблюди формат ответа.
            Формат ответа: <skill_1>=<skill_1_grade>, <skill_2>=<skill_2_grade>, ...
            
            Обрати внимание на параметр <grade> у каждого перечисляемого скилла.
            <grade> - численная оценка (по шкале от 0 до 3 включительно).
            Определить уровень владения навыком нужно исходя из описанного соискателем опыта по следующему принципу:
            0 - уровень владения навыком не удаётся определить (например, навык упоминается в резюме, но описывается недостаточно подробно)
            1 - Junior уровень владения навыком.
            2 - Middle yровень владения навыком.
            3 - Senior уровень владения навыком.

            Ответ:
            """
        )

        message = HumanMessage(content=prompt.format(description=cv_description))
        response = await self.llm.ainvoke([message])

        hard_skills = _parse_skills(response.content)

        return hard_skills


    def _parse_skills(self, llm_response: str) -> List[Tuple[str, int]]:
        """ Вспомогательная функция для парсинга скиллов из ответа llm'ки """
        # Убираем возможные лишние символы по краям ответа нейронки
        llm_response: str = llm_response.strip().strip(',')

        # Разбиваем ответ нейронки по парам "скилл=оценка"
        skill_pairs: list = llm_response.split()

        for i in range(len(skill_pairs)):
            # Разбиваем пару <skill_name>=<skill_grade> по '='
            skill_pairs[i] = skill_pairs[i].split('=')
            
            # Приводим оценку skill_grade к типу int
            skill_pairs[i][1] = int(skill_pairs[i][1])

        return skill_pairs

