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
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from bson import ObjectId  # Importa ObjectId desde bson

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

# Conexión a la base de datos de MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["my_database"]
collection = db["my_collection"]

# Instantiate Atlas Vector Search as a retriever
retriever = vector_search.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 20, "score_threshold": 0.75}
)

# Inicializar el modelo de ChatOpenAI
llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=1,
    max_tokens=800,
)

# Define a prompt template
template = """
Si te preguntan tu nombre, responde que es Pepe.
{context}
Question: {query}
"""
custom_rag_prompt = PromptTemplate.from_template(template)

contextualize_q_system_prompt = "hola"

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

chat_history = []

qa_system_prompt = """
Eres un asistente virtual.
{context}
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@app.post("/generate_text")
async def generate_text(input_data: InputData):
    try:
        global chat_history

        query = input_data.text

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        response = rag_chain.invoke({"input": query, "chat_history": chat_history})

        # Extiende el historial de la conversación con la pregunta y respuesta actual
        chat_history.append(HumanMessage(content=query))
        chat_history.append(response["answer"])

        return {"generated_text": response["answer"]}
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
