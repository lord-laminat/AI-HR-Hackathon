from pydantic import BaseModel

class JobDescription(BaseModel):
    """
    Объект, содержащий текст вакансии или резюме.
    """
    title: str
    text: str
