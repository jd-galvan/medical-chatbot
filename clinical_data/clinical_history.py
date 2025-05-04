from pymongo import MongoClient
from typing import Optional, Dict


class ClinicalHistoryRepository:
    def __init__(self, db_client: MongoClient, db_name: str = "clinical-data"):
        self.db = db_client[db_name]
        self.collection = self.db["clinical-history"]

    def get_clinical_history(self, patient_id: str) -> Optional[Dict]:
        """Busca un paciente por su ID en la colección 'patients'."""
        return self.collection.find_one({"id_paciente": patient_id})
