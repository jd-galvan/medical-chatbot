from pydantic import BaseModel


class MedicalSummary(BaseModel):
    diagnostico: str
    medicamentos: str
