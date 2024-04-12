from fastapi import FastAPI, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
import os

app = FastAPI(docs_url="/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    text: str

class Feedback(BaseModel):
    good: bool

# Inicialización global de objetos
embedding_openai = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

@app.post("/generate_text")
async def generate_text(
    input_data: InputData,
    use_database: bool = Query(default=False, description="Indica si se debe utilizar la base de datos")
):
    try:
        # Inicializar la base de datos si se solicita
        if use_database:
            NOMBRE_INDICE_CHROMA = "dataset-contactos"
            vectorstore_chroma = Chroma(persist_directory=NOMBRE_INDICE_CHROMA, embedding_function=embedding_openai)
            retriever_chroma = vectorstore_chroma.as_retriever()
        else:
            retriever_chroma = None

        # Inicializar el modelo
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            temperature=1,
        )

        qa_chains_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever_chroma,
        )

        # Concatenar el input de texto con el string predeterminado
        concatenated_text = input_data.text + ""

        # Realizar una sola consulta al modelo utilizando el texto concatenado
        response = qa_chains_with_sources(concatenated_text)

        # Devolver la respuesta junto con los botones de feedback
        return {
            "generated_text": response,
            "feedback_options": {
                "good": "Buena",
                "bad": "Mala"
            }
        }
    except Exception as e:
        return {"error": f"Error en la generación del texto: {e}"}

@app.post("/send_feedback")
async def send_feedback(feedback: Feedback):
    try:
        # Guardar la retroalimentación del usuario en alguna base de datos o utilizarla para entrenar tu modelo
        if feedback.good:
            print("La respuesta es buena.")
            # Aquí puedes realizar alguna acción con la retroalimentación positiva
        else:
            print("La respuesta no es buena.")
            # Aquí puedes realizar alguna acción con la retroalimentación negativa

        return {"message": "Feedback recibido correctamente."}
    except Exception as e:
        return {"error": f"Error al procesar el feedback: {e}"}
