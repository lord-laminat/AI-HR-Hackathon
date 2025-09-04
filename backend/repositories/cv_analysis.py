from schemas.cv_analysis import JobDescription

class JobRepository:
    """
    Класс, описывающий хранение объектов JobDescription.
    """

    def get_job_description(self, file_title: str) -> JobDescription:
        """
        Достаёт объект JobDescription из хранилища.
        """
        job_description: JobDescription

        try: 
            with open(f"../../vacancies/{file_title}", "r") as file {
                job_description.text = file.read()
                job_description.title = file_title
            }
        except FileNotFoundError as ex:
            ...
            # TODO: добавить логирование ошибки

        return job_description


    def create_job_description(self, JobDescription) -> None:
        """
        Создаёт объект JobDescription в хранилище.
        """
        raise NotImplementedError("Is not implemented yet.")


    def delete_job_description(self, JobDescription) -> None:
        """
        Удаляет объект JobDescription из хранилища.
        """
        raise NotImplementedError("Is not implemented yet.")


    def update_job_description(self, JobDescription) -> None:
        """
        Изменяет объект JobDescription в хранилище.
        """
        raise NotImplementedError("Is not implemented yet.")
