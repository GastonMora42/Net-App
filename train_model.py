from dvc.api import read
import pandas as pd
import numpy as np
import os
from pymongo import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader

# Configuración de la conexión a MongoDB
connection_string = "mongodb+srv://gastonmora1742:jIhdEUoE9FWAcunB@jett-cluster.psm4rdx.mongodb.net/"
db_name = "index-contactos"
collection_name = "index"
index_name = "index_name"

# Inicialización del cliente de MongoDB
client = MongoClient(connection_string)
collection = client[db_name][collection_name]

# Cargar datos desde un archivo CSVs
loader = CSVLoader(file_path='dataset/new-contact.csv')
data = loader.load()

# Inicializar embeddings de OpenAI
openai_api_key = os.environ.get("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, disallowed_special=())

# Dividir documentos en fragmentos (chunks)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(data)

# Inicializar búsqueda de vectores en MongoDB
vector_search = MongoDBAtlasVectorSearch(document=docs, embedding=embeddings, collection=collection, index_name=index_name)

# Obtener el embedding del documento
embedding = embeddings.embed(docs.page_content)

# Almacenar el vector en MongoDB
vector_search.store_vector(document=docs, embedding=embedding, collection=collection)

print("Documentos y embeddings insertados exitosamente en MongoDB.")
