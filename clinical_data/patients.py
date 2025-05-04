from pymongo import MongoClient
from typing import Optional, Dict


class PatientRepository:
    def __init__(self, db_client: MongoClient, db_name: str = "clinical-data"):
        self.db = db_client[db_name]
        self.collection = self.db["patients"]

    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Busca un paciente por su ID en la colección 'patients'."""
        return self.collection.find_one({"numero_identificacion": patient_id})

    def get_all_patients(self) -> list:
        """Retorna todos los pacientes de la colección."""
        return list(self.collection.find())

    def search_by_name(self, name: str) -> list:
        """Busca pacientes cuyo nombre coincida parcialmente (búsqueda insensible a mayúsculas)."""
        return list(self.collection.find({"Nombre": {"$regex": name, "$options": "i"}}))
