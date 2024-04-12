from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
import random
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

# Definir una clase de dependencia para inicializar los objetos globales una vez
class InitializeChain:
    def __init__(self):
        # Inicializar los objetos globales aquí
        embedding_openai = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        nombre_indice_chroma = "dataset-contactos"
        vectorstore_chroma = Chroma(persist_directory=nombre_indice_chroma, embedding_function=embedding_openai)
        retriever_chroma = vectorstore_chroma.as_retriever(search_kwargs={"k": 1})
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            temperature=1,
        )
        self.qa_chains_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever_chroma
        )

    def get_chain(self):
        return self.qa_chains_with_sources

initialize_chain = InitializeChain()

@app.post("/generate_text")
async def generate_text(input_data: InputData, chain=Depends(initialize_chain.get_chain)):
    try:
        # Realizar consultas al modelo con un rango aleatorio
        num_queries = random.randint(1, 5)
        responses = [chain(input_data.text) for _ in range(num_queries)]
        # Seleccionar aleatoriamente una respuesta de las generadas
        random_response = random.choice(responses)
        return {"generated_text": random_response}
    except Exception as e:
        return {"error": f"Error en la generación del texto: {e}"}

