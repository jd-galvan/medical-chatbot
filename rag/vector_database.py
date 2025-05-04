import os
from chromadb import HttpClient
import chromadb.utils.embedding_functions as embedding_functions


class VectorDatabase:
    def __init__(self):
        self.client = HttpClient()

        embed_model = os.environ.get("OLLAMA_EMBEDDINGS_MODEL")
        self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
            url=os.environ.get("OLLAMA_HOST"),
            model_name=embed_model,
        )

    def query(self, clinical_history_id, datetime, query, n_results=1):
        try:
            collection = self.client.get_collection(
                name=clinical_history_id, embedding_function=self.embedding_function)

            if datetime:
                results = collection.query(
                    # query_embeddings=embeddings,
                    query_texts=[query],  # Presion arterial
                    n_results=n_results,  # 3
                    where={"fecha_hora": datetime},  # 21/06/2024 08:30
                    include=["documents"]
                )
            else:
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents"]
                )
            return results["documents"]
        except Exception as e:
            print(e)
