import os
import gradio as gr
from pymongo import MongoClient
from rag.llm import LLM
from clinical_data.patients import PatientRepository
from clinical_data.clinical_history import ClinicalHistoryRepository
from dotenv import load_dotenv

load_dotenv()

# Crear el cliente
client = MongoClient(os.environ.get("DATABASE_CONNECTION"))

# Crear el repositorio
patient_repository = PatientRepository(client)
clinical_history_repository = ClinicalHistoryRepository(client)

# Crear conexión con LLM (Ollama)
llm = LLM()

# Clinical History
clinical_history = ""

# Función para cargar paciente y reiniciar historial del chat


def cargar_paciente(identificacion):
    patient = patient_repository.get_patient_by_id(identificacion)

    clinical_history = clinical_history_repository.get_clinical_history(
        patient_id=str(patient["_id"]))

    patient = {key: patient[key] for key in [
        "nombre_completo", "fecha_nacimiento", "estado_civil", "lugar_residencia"] if key in patient}

    summary = "\n\n".join(
        f"Fecha y hora de la atencion: {c['fecha_hora']}\nResumen de la atencion medica: {c['resumen']}"
        for c in clinical_history["atenciones"]
    )

    if patient:
        panel = f"""
        <div style="background-color: #F0F8FF; padding: 1rem; border-radius: 10px;">
            <h3>🧑‍⚕️ Paciente en consulta</h3>
            <p><strong>Nombre:</strong> {patient["nombre_completo"]}</p>
            <p><strong>F. Nacimiento:</strong> {patient["fecha_nacimiento"]}</p>
            <p><strong>Estado Civil:</strong> {patient["estado_civil"]}</p>
            <p><strong>Lugar Residencia:</strong> {patient["lugar_residencia"]}</p>
        </div>
        """
        # Se activa el Textbox y el botón de envío, y se reinicia el historial del chatbot (lista vacía)
        return panel, patient, gr.update(interactive=True), gr.update(interactive=True), [], summary, str(clinical_history["_id"])

    else:
        return "<div style='color: red;'>Paciente no encontrado</div>", None, gr.update(interactive=False), gr.update(interactive=False), [], "", ""


# Función del asistente clínico

def clinical_assistant(message, history_ui, history_llm, patient, summary, clinical_history_id):

    # Agregar mensaje normal del usuario
    history_ui.append({"role": "user", "content": message})
    history_llm.append({"role": "user", "content": message})

    # Inicializa el mensaje parcial del asistente
    assistant_msg = {"role": "assistant", "content": ""}
    history_ui.append(assistant_msg)
    history_llm.append(assistant_msg)

    partial_response = ""
    for token in llm.get_streaming_response(clinical_history_id, patient, summary, history_llm[:-1]):
        partial_response += token
        if "function_calling" in partial_response:
            # Si detectas que es function calling, sólo actualizas el mensaje visible
            partial_response = "<i>Estoy investigando más a fondo para responderte...</i>\n\n"
            history_ui[-1]["content"] = partial_response
        else:
            history_llm[-1]["content"] = partial_response
            history_ui[-1]["content"] = partial_response
        yield history_ui, ""


# Interfaz
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="color: #2A6FA1;">🤖 Asistente Clínico Virtual</h1>
        <p style="font-size: 1.1rem; color: #444;">
            Herramienta de apoyo para médicos durante la consulta. Consulta información relevante del historial clínico del paciente.<br>
            <small><i>Solo para uso interno. No sustituye el juicio profesional.</i></small>
        </p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=6):
            # Se usa el nuevo formato de mensajes para el chatbot
            history_ui_state = gr.Chatbot(label="Asistente Clínico",
                                          height=420, type="messages")
            msg = gr.Textbox(placeholder="Ej: ¿Qué antecedentes tiene el paciente?",
                             label="Consulta médica", interactive=False)
            # 👈 historial técnico para enviar al LLM
            history_llm_state = gr.State([])
            with gr.Row():
                send_btn = gr.Button(
                    "Enviar consulta", variant="primary", interactive=False)
                clear_btn = gr.Button("🧹 Limpiar conversación")
        with gr.Column(scale=4):
            identificacion_input = gr.Textbox(
                label="ID del paciente", placeholder="Ej: 123")
            cargar_btn = gr.Button("🔍 Cargar paciente")
            panel_paciente = gr.HTML()
            summary_state = gr.State()
            patient_data_state = gr.State()
            clinical_history_id_state = gr.State()

    # Eventos:
    # Al cargar un paciente se actualiza el panel, se almacena el paciente en un gr.State(),
    # se habilitan el textbox y botón de envío y se limpia el chatbot (historial).
    cargar_btn.click(
        cargar_paciente,
        inputs=identificacion_input,
        outputs=[panel_paciente, patient_data_state, msg, send_btn, history_ui_state,
                 summary_state, clinical_history_id_state, history_llm_state],
        show_progress="full"
    )

    identificacion_input.submit(
        cargar_paciente,
        inputs=identificacion_input,
        outputs=[panel_paciente, patient_data_state, msg, send_btn, history_ui_state,
                 summary_state, clinical_history_id_state],
        show_progress="full"
    )

    msg.submit(
        clinical_assistant,
        inputs=[msg, history_ui_state, history_llm_state,
                patient_data_state, summary_state, clinical_history_id_state],
        outputs=[history_ui_state, msg]
    )

    send_btn.click(
        clinical_assistant,
        inputs=[msg, history_ui_state, history_llm_state,
                patient_data_state, summary_state, clinical_history_id_state],
        outputs=[history_ui_state, msg]
    )

    clear_btn.click(lambda: ([], "", []), None, [
                    history_ui_state, msg, history_llm_state])


demo.launch()
