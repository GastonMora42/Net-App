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

# Cargar datos desde un archivo CSV
loader = CSVLoader(file_path='dataset/new-contact.csv')
data = loader.load()

# Inicializar embeddings de OpenAI
openai_api_key = os.environ.get("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, disallowed_special=())

# Dividir documentos en fragmentos (chunks)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(data)

# Inicializar búsqueda de vectores en MongoDB
vector_search = MongoDBAtlasVectorSearch(embedding=embeddings, collection=collection, index_name=index_name)

# Iterar sobre los documentos y procesar cada uno
for doc in docs:
    # Obtener el contenido del documento de manera genérica
    content = getattr(doc, 'content', None)  # Intentar acceder al atributo 'content' del documento
    if content is None:
        # Si 'content' no está disponible, intentar otras formas de acceder al contenido
        if isinstance(doc, dict):
            content = doc.get('text', '')  # Intentar obtener 'text' de un diccionario
        elif isinstance(doc, str):
            content = doc  # Si el documento es una cadena, considerarlo como el contenido directamente

    # Verificar si el contenido es válido antes de crear un Document
    if content:
        # Crear un objeto Document con el contenido extraído
        metadata = {}  # Puedes ajustar la metadata según sea necesario
        document = Document(page_content=content, metadata=metadata)

        # Calcular el embedding para el documento
        embedding = embeddings.embed(content)

        # Insertar el documento y su embedding en MongoDB
        vector_search.insert(document=document, embedding=embedding, collection=collection, index_name=index_name)

print("Documentos y embeddings insertados exitosamente en MongoDB.")
