from langchain_community.document_loaders.mongodb import MongodbLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo import MongoClient
import os

# Configuración de conexiones y credenciales
api_key = os.environ.get("OPENAI_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")
connection_string = "mongodb+srv://gastonmora1742:jIhdEUoE9FWAcunB@jett-cluster.psm4rdx.mongodb.net/"
db_name = "index-contactos"
collection_name = "index"
index_name = "index_name"

# Conexión a MongoDB
client = MongoClient(connection_string)
db = client[db_name]
collection = db[collection_name]

# Cargar datos desde CSV
loader = CSVLoader(file_path='dataset/new-contact.csv')
new_data = loader.load()

# Crear instancias necesarias para procesamiento de datos
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

# Dividir los documentos del CSV en fragmentos
docs = text_splitter.split_documents(new_data)

# Crear un vectorizador de búsqueda en MongoDB Atlas
vector_search = MongoDBAtlasVectorSearch.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(disallowed_special=()),
    collection=collection,
    index_name=index_name,
)

# Cargar nuevos documentos en MongoDB
for doc in docs:
    collection.insert_one(doc.to_dict())  # Insertar cada documento como un diccionario en la colección
