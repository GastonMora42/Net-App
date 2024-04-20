from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
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

# Inicializar la base de datos Chroma
NOMBRE_INDICE_CHROMA = "dataset-contactos"
vectorstore_chroma = Chroma(persist_directory=NOMBRE_INDICE_CHROMA, embedding_function=embedding_openai)

# Inicializar el modelo de ChatOpenAI
llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=0.2,
    max_tokens=1000,
)

# Inicializar la conversación
conversation = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=vectorstore_chroma.as_retriever(), verbose=True
)

# Historial de la conversación
conversation_history = []

@app.post("/generate_text")
async def generate_text(input_data: InputData):
    try:
        query = input_data.text
        response = process_query(query)
        # Actualizar el historial de la conversación
        conversation_history.append((query, response))
        return {"generated_text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la generación del texto: {e}")

@app.post("/send_feedback")
async def send_feedback(feedback: Feedback):
    try:
        if feedback.good:
            print("La respuesta es buena.")
            # Aquí puedes realizar alguna acción con la retroalimentación positiva
            prompt_feedback = "Buena respuesta"
        else:
            print("La respuesta no es buena.")
            # Aquí puedes realizar alguna acción con la retroalimentación negativa
            prompt_feedback = "Mala respuesta"
        return {"message": "Feedback recibido correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el feedback: {e}")

def process_query(query):
    global conversation_history
    print("[La IA está pensando...]")
    result = conversation({"question": query, "chat_history": conversation_history})
    return result["answer"]
