import os
import json
from ollama import Client
from .vector_database import VectorDatabase


class LLM:
    def __init__(self):
        self.client = Client(
            host=os.environ.get("OLLAMA_HOST"),
        )

        self.vdb_client = VectorDatabase()

    def __get_system_prompt(self, patient, summary, enable_function_calling: bool, include_summaries: bool = True):
        system_message = f"Eres un asistente medico que debe responder sobre informacion de historial clinico del siguiente paciente: \n #CONTEXTO: \n PACIENTE: \n {patient}"

        if include_summaries:
            system_message += f"\n\n ATENCIONES MEDICAS: \n {summary} \n\n Tus respuestas deben ser breves y concisas."

        if enable_function_calling:
            system_message += """
            \n\n
            Si no tienes información para responder en los resumenes, no respondas diciendo que no tienes informacion, en cambio, invoca proactivamente la siguiente funcion usando el siguiente formato (incluire ejemplo de los parametros a enviar):
            {"name": "get_more_detail_of_clinical_history", "parameters": {
                "datetime": "20/05/2023 12:05", "query": "dosis de paracetamol"}}
            En el que fecha_hora es la fecha y hora de la atencion medica (puede ser mas de una) y query es el contenido que deseas buscar.
            NO DEBES incluir ningún otro texto en la respuesta si decides llamar a una función.
            """

        return system_message

    def get_streaming_response(self, clinical_history_id: str, patient: dict, summary: str, history: list):
        print("HISTORY")
        print(history)
        messages = [{
            "role": "system",
            "content": self.__get_system_prompt(patient=patient, summary=summary, enable_function_calling=True)
        }]

        messages.extend(history)

        partial_response = ""
        for chunk in self.client.chat(
            model=os.environ.get("OLLAMA_LLM_MODEL"),
            messages=messages,
            stream=True,
            options={
                "temperature": 0.0,
                "num_ctx": 8192
            }
        ):
            # print(chunk)
            partial_response += chunk["message"]["content"]
            if "get_more_detail_of_clinical_history" in partial_response and chunk["done"]:
                yield "function_calling"

                start_index = partial_response.find('{')
                function_args = {}
                if start_index != -1:
                    # Tomamos desde la primer llave
                    json_str = partial_response[start_index:]
                    function_args = json.loads(json_str)["parameters"]
                    print("Argumentos para function calling")
                    print(function_args)

                context = self.vdb_client.query(
                    clinical_history_id=str(clinical_history_id), datetime=function_args["datetime"], query=function_args["query"], n_results=3)

                print("CONTEXTO RECUPERADO:")
                print(context[0])

                messages[0] = {
                    "role": "system",
                    "content": self.__get_system_prompt(patient=patient, summary=summary, enable_function_calling=False)
                }

                messages[len(
                    messages)-1]["content"] = f"Context: {"\n\n".join(context[0])}\n\nQuestion: {messages[len(messages)-1]["content"]}\nAnswer:"

                # print("MESSAGES")
                # print(messages)

                for new_chunk in self.client.chat(
                    model=os.environ.get("OLLAMA_LLM_MODEL"),
                    messages=messages,
                    stream=True,
                    options={
                        "temperature": 0.0,
                        "num_ctx": 8192
                    }
                ):
                    yield new_chunk["message"]["content"]
            else:
                yield chunk["message"]["content"]

    def get_response_contextual_rag(self, clinical_history_id: str, patient: dict, summary: str, history: list, model: str):
        messages = [{
            "role": "system",
            "content": self.__get_system_prompt(patient=patient, summary=summary, enable_function_calling=True, include_summaries=True)
        }]

        messages.extend(history)

        response = self.client.chat(
            model=model,
            messages=messages,
            stream=False,
            options={
                "temperature": 0.0,
                "num_ctx": 8192
            }
        )

        message_response = response.message.content

        if "get_more_detail_of_clinical_history" in message_response:
            start_index = message_response.find('{')
            function_args = {}
            if start_index != -1:
                # Tomamos desde la primer llave
                json_str = message_response[start_index:]
                function_args = json.loads(json_str)["parameters"]
                print("Argumentos para function calling")
                print(function_args)

            context = self.vdb_client.query(
                clinical_history_id=str(clinical_history_id), datetime=function_args["datetime"], query=function_args["query"], n_results=3)

            print("CONTEXTO RECUPERADO:")
            print(context[0])

            messages[0] = {
                "role": "system",
                "content": self.__get_system_prompt(patient=patient, summary=summary, enable_function_calling=False, include_summaries=True)
            }

            messages[len(
                messages)-1]["content"] = f"Context: {"\n\n".join(context[0])}\n\nQuestion: {messages[len(messages)-1]["content"]}\nAnswer:"

            new_response = self.client.chat(
                model=model,
                messages=messages,
                stream=False,
                options={
                    "temperature": 0.0,
                    "num_ctx": 8192
                }
            )

            return new_response.message.content
        else:
            return message_response

    def get_response_simple_rag(self, clinical_history_id: str, patient: dict, summary: str, history: list, model: str):
        messages = [{
            "role": "system",
            "content": self.__get_system_prompt(patient=patient, summary=summary, enable_function_calling=False, include_summaries=False)
        }]

        messages.extend(history)

        user_prompt = history[-1]["content"]

        context = self.vdb_client.query(
            clinical_history_id=str(clinical_history_id), datetime=None, query=user_prompt, n_results=3)

        print("CONTEXTO RECUPERADO:")
        print(context[0])

        messages[len(
            messages)-1]["content"] = f"Context: {"\n\n".join(context[0])}\n\nQuestion: {messages[len(messages)-1]["content"]}\nAnswer:"

        new_response = self.client.chat(
            model=model,
            messages=messages,
            stream=False,
            options={
                "temperature": 0.0,
                "num_ctx": 8192
            }
        )

        return new_response.message.content
