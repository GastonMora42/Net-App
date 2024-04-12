from fastapi import FastAPI, Query
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

# Inicialización global de objetos
embedding_openai = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)
NOMBRE_INDICE_CHROMA = "dataset-contactos"
vectorstore_chroma = Chroma(persist_directory=NOMBRE_INDICE_CHROMA, embedding_function=embedding_openai)
retriever_chroma = vectorstore_chroma.as_retriever()
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

@app.post("/generate_text")
async def generate_text(input_data: InputData, use_chroma: bool = False, feedback: bool = False):
    try:
        # Si se ha seleccionado la opción para utilizar Chroma
        if use_chroma:
            qa_chains_with_sources.retriever = retriever_chroma

        # Concatenar el input de texto con el string predeterminado
        concatenated_text = input_data.text + ""

        # Realizar una sola consulta al modelo utilizando el texto concatenado
        response = qa_chains_with_sources(concatenated_text)

        # Guardar la retroalimentación del usuario si se proporcionó
        if feedback is not None:
            # Aquí puedes realizar alguna acción con la retroalimentación, como guardarla en una base de datos o utilizarla para entrenar tu modelo
            if feedback:  # Si la retroalimentación es positiva
                print("La respuesta es buena.")
            else:  # Si la retroalimentación es negativa
                print("La respuesta no es buena.")

        return {"generated_text": response}
    except Exception as e:
        return {"error": f"Error en la generación del texto: {e}"}