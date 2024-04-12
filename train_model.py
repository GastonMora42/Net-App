from dvc.api import read
import pandas as pd
import numpy
import openai
import langchain
import retriever
import sentence_transformers
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma
from datetime import datetime
from io import StringIO
from langchain.chains import RetrievalQAWithSourcesChain
import random
import sys
from langchain.chat_models import ChatOpenAI
import logging
from sklearn.pipeline import Pipeline
from prepare import contacts_data
from langchain.embeddings import OpenAIEmbeddings
import os

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt='%H:%M:%S',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

logger.info("Cargando claves y secretos..")

api_key = os.environ.get("OPENAI_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

logger.info("Cargando modelo....")

model = Pipeline([
    ('embeddingopenai', OpenAIEmbeddings(
        openai_api_key="OPENAI_API_KEY",
        model_name="text-embedding-3-large"
    )),
    ('index', Chroma(
        persist_directory='NOMBRE_INDICE_CHROMA',
        embedding_function='embeddingopenai',
    )),
    ('retriever_chroma', Chroma(
        persist_directory='NOMBRE_INDICE_CHROMA',
        embedding_function='embeddingopenai',
    ).as_retriever(
        search_kwargs={"k": 4}
    )),
    ('llm', ChatOpenAI(
        openai_api_key="OPENAI_API_KEY",
        model_name="gpt-3.5-turbo",
        temperature=0.5
    )),
])

embeddingopenai = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

logger.info("Cargando data resumida...")

loader = CSVLoader(file_path='/dataset/Contacts-Main View.csv')
data = loader.load()

NOMBRE_INDICE_CHROMA = "dataset-contactos"

vectorstore_chroma = Chroma.from_documents(
    documents=data,
    embedding=embeddingopenai,
    persist_directory=NOMBRE_INDICE_CHROMA
)

vectorstore_chroma.persist()

vectorstore_chroma = Chroma(
    persist_directory=NOMBRE_INDICE_CHROMA, 
    embedding_function=embeddingopenai
)

retriever_chroma = vectorstore_chroma.as_retriever(
    search_kwargs={"k" : 4}
)

llm = ChatOpenAI (
    model_name="gpt-3.5-turbo",
    openai_api_key="OPENAI_API_KEY",
    temperature=1,
)

qa_chains_whith_sources = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever_chroma
)