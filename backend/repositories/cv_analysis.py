from schemas.cv_analysis import JobDescription
from configs.config import config


class VacancyRepository:
    """ Класс, описывающий хранение объектов JobDescription. """

    def get_vacancies_list(self) -> List[str]:
        """ Возвращает список файлов, лежащих в директории для вакансий. """
        directory_path = config["Paths"]["vacancies_dir_path"]
        files = list()

        # итерация по всем именам в директории (файлы и папки)
        for entry in os.listdir(directory_path):
            full_path = os.path.join(directory_path, entry)
            
            # убеждаемся, что выбранное имя - файл
            if os.path.isfile(full_path):
                files.append(entry)

        return files


    def get_vacancy_description(self, file_title: str) -> JobDescription:
        """ Достаёт объект JobDescription из хранилища. """
        
        job_description: JobDescription

        try: 
            with open(f"{config["Paths"]["vacancies_dir_path"]}/{file_title}", "r") as file {
                job_description.text = file.read()
                job_description.title = file_title
            }
        except FileNotFoundError as ex:
            ...
            # TODO: добавить логирование ошибки

        return job_description


    def create_vacancy_description(self, JobDescription) -> None:
        """ Создаёт объект JobDescription в хранилище. """
        raise NotImplementedError("Is not implemented yet.")


    def delete_vacancy_description(self, JobDescription) -> None:
        """ Удаляет объект JobDescription из хранилища. """
        raise NotImplementedError("Is not implemented yet.")


    def update_vacancy_description(self, JobDescription) -> None:
        """ Изменяет объект JobDescription в хранилище. """
        raise NotImplementedError("Is not implemented yet.")
