from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os
from train_model import vector_search
import pymongo
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymongo import MongoClient

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

# Instantiate Atlas Vector Search as a retriever
retriever = vector_search.as_retriever(
   search_type = "similarity",
   search_kwargs = {"k": 15, "score_threshold": 0.75}
)

# Inicializar el modelo de ChatOpenAI
llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=4,
    max_tokens=1000,
)

# Define a prompt template
template = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
{context}
Question: {query}
"""
custom_rag_prompt = PromptTemplate.from_template(template)

 # Historial de la conversación
conversation_history = [],

def format_docs(docs):
   return "\n\n".join(doc.page_content for doc in docs)


@app.post("/generate_text")
async def generate_text(input_data: InputData):
    try:# Inicializar la conversación
        query = input_data.text
        rag_chain = (
        { "context": retriever | format_docs, "query": RunnablePassthrough()}
         | custom_rag_prompt
         | llm
         | StrOutputParser())
        response = rag_chain.invoke(query)
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
            print("La respuesta no es buenas.")
            # Aquí puedes realizar alguna acción con la retroalimentación negativa
            prompt_feedback = "Mala respuesta"
        return {"message": "Feedback recibido correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el feedback: {e}")
