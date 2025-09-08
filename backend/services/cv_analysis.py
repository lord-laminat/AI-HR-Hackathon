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

from schemas.cv_analysis import JobDescription, JobParameters, VacancyMatchingReport
from repositories.cv_analysis import VacancyRepository


class State(TypedDict):
    """
    Описание параметров, к которым имеет
    доступ агент во время работы.
    """
    cv_description: str
    cv_parameters: JobParameters
    vacancies_parameters: List[JobParameters]
    matching_reports: List[VacancyMatchingReport]


class CVAnalysisService:
    """
    Сервис по определению ключевых параметров
    в резюме и формированию объекта JobParameters.
    """

    def __init__(
            self,
            repository: VacancyRepository,
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
        workflow.add_node("analyse_vacancies", self._analyse_vacancies)
        workflow.add_node("compare_cv_with_vacancies", self._compare_cv_with_vacancies)

        # Ребра графа
        workflow.set_entry_point("analyse_cv")
        workflow.add_edge("analyse_cv", "analyse_vacancies")
        workflow.add_edge("analyse_vacancies", "compare_cv_with_vacancies")
        workflow.add_edge("compare_cv_with_vacancies", END)

        return workflow.compile()


    async def _analyse_cv(self, state: State) -> Dict[str, JobParameters]:
        """ Узел анализа резюме кандидата. """
        cv_parameters = JobParameters()

        cv_parameters.experience_years = await self._get_cv_experience(state["cv_description"])
        cv_parameters.hard_skills = await self._get_cv_hard_skills(state["cv_description"])
        cv_parameters.soft_skills = list()
        vacancy_parameters.title = ""

        return { "cv_parameters": cv_parameters }


    async def _get_cv_experience(self, cv_description: str) -> float:
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


    async def _get_cv_hard_skills(self, cv_description: str) -> List[Tuple[str, int]]:
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


    async def _analyse_vacancies(self, state: State) -> Dict[str, JobParameters]:
        """
        Узел, описывающий формирование из всех вакансий в хранилище
        объекты JobParameters для дальнейшего сравнения с резюме.
        """
        vacancies_filenames: List[str] = self.repository.get_vacancies_list()
        analysed_vacansies: List[JobParameters]

        for vacancy_filename in vacancies_filenames:
            description: str = self.repository.get_vacancy_description().text
            
            vacancy_parameters = JobParameters()
            vacancy_parameters.experience_years = await self._get_vacancy_experience(description)
            vacancy_parameters.hard_skills = await self._get_vacancy_hard_skills(description)
            vacancy_parameters.soft_skills = list()
            vacancy_parameters.title = await self._get_vacancy_name(description)

            analysed_vacansies.append(vacancy_parameters)

        return { "vacancies_parameters": analysed_vacansies }


    async def _get_vacancy_experience(self, description: str) -> float:
        """
        Функция узла 'analyse_vacancies' для определения
        минимального опыта работы, требуемого в вакансии.
        """
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Ты - HR агент. Твоя задача - проанализировать представленное описание вакансии.
            Выяви из него минимальный требуемый опыт работы.

            Проанализируй следующее описание вакансии:
            # начало описания
            {description}
            # конец описания

            Строго соблюди формат ответа.
            Формат ответа: одно число - требуемое от кандидата количество лет опыта.
            
            Ответ:
            """
        )

        message = HumanMessage(content=prompt.format(description=cv_description))
        response = await self.llm.ainvoke([message])

        experience = re.search(r"\d+\.?\d*", response.content).group()

        return float(experience)


    async def _get_vacancy_hard_skills(self, description: str) -> List[Tuple[str, int]]:
        """
        Функция узла 'analyse_vacancies' для определения
        хард скиллов, требуемых в вакансии.
        """
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Ты - HR агент. Твоя задача - проанализировать представленное описание вакансии.
            Выяви из него требуемые хард скилы и их уровень. Требуемый уровень оцени по шкале от 1 до 3. 
            
            Проанализируй следующее описание вакансии:
            # начало описания
            {description}
            # конец описания

            Строго соблюди формат ответа.
            Формат ответа: <skill_1>=<skill_1_grade>, <skill_2>=<skill_2_grade>, ...
            
            Обрати внимание на параметр <grade> у каждого перечисляемого скилла.
            <grade> - численная оценка (по шкале от 0 до 3 включительно).
            Определить требуемый уровень навыка нужно исходя из описанных обязанностей и требований к кандидату по следующему принципу:
            0 - навык указан как необязательный.
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


    async def _compare_cv_with_vacancies(self, state: State) -> Dict[str, List[VacancyMatchingReport]]:
        """
        Узел, возвращающий результаты сравнений представленного
        кандидатом резюме с имеющимися вакансиями.
        """
        cv_parameters: JobParameters = state["cv_parameters"]
        vacancies_parameters_list: List[JobParameters] = state["vacancies_parameters"]

        report_list = list()

        for vacancy in vacancies_parameters_list:
            report_list.append(self._compare_by_llm(cv_parameters, vacancy))

        return { "matching_reports": report_list }


    async def _compare_by_llm(self, cv: JobParameters, vacancy: JobParameters) -> VacancyMatchingReport:
        """
        Функция узла 'compare_cv_with_vacancies', производящее
        одиночное сравнение резюме с вакансией, используя LLM.
        """
        prompt = PromptTemplate(
            input_variables=["cv_hard_skills", "vacancy_hard_skills", "cv_experience", "vacancy_experience"],
            template="""
            Ты - HR агент. Тебе представлены краткие описания вакансии и резюме кондидата.
            Твоя задача - оценить степень соответствия кандидата рассматриваемой вакансии.
            Тебе нужно проанализировать опыт соискателя и сопоставить имеющиеся у него навыки с теми, что требуются в вакансии.

            Скиллы, требуемые в вакансии с оценкой их уровня:
            {vacancy_hard_skills}

            Скиллы, описанные в резюме кандидата с оценкой их уровня:
            {cv_hard_skills}

            Требуемый опыт/опыт кандидата: {cv_experience}/{vacancy_experience}

            Ответь строго в формате <процент_соответствия>%
            Ответ:
            """
        )

        message = HumanMessage(content=prompt.format(
            cv_hard_skills=", ".join(cv.hard_skills),
            vacancy_hard_skills=", ".join(vacancy.hard_skills),
            cv_experience=str(cv.experience_years),
            vacancy_experience=str(vacancy.experience_years)
        ))
        response = await self.llm.ainvoke([message])

        match_result: float = float(re.search(r"\d+\.?\d*\%", response.content).group().strip('%'))

        report = VacancyMatchingReport()
        report.vacancy_title = vacancy.title
        report.matching = match_result

        return report


    async def _get_vacancy_name(self, vacancy_filename: str) -> str:
        """
        Функция узла 'compare_cv_with_vacancies', выявляющая
        название вакансии из её описания.
        """
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
            Ты - HR агент. Ты анализируешь представленное описание вакансии.
            Твоя задача - просто определить название вакансии из описания.
            
            # начало описания
            {description}
            # конец описания

            Строго соблюди формат ответа.
            Формат ответа: <название_вакансии>
            
            Ответ:
            """
        )

        message = HumanMessage(content=prompt.format(description=cv_description))
        response = await self.llm.ainvoke([message])

        return response.content.strip()


    async def analyse(self, cv_description: str) -> Dict[str, List[VacancyMatchingReport]]:
        """ Основной метод для анализа резюме. """
        initial_state = {
            "cv_description": cv_description,
            "cv_parameters": JobParameters(),
            "vacancies_parameters": list(),
            "matching_reports": list()
        }

        result = await self.workflow.ainvoke(initial_state)

        analysis_result = {
            "analysis_results": result["matching_reports"]
        }

        return analysis_result
