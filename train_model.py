from dvc.api import read
import pandas as pd
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import os
import pymongo
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.document_loaders.mongodb import MongodbLoader

openai_api_key = os.environ.get("OPENAI_API_KEY")

embeddingopenai = OpenAIEmbeddings(
    openai_api_key=openai_api_key,
    model="text-embedding-3-large"
)

connection_string="mongodb+srv://netsquared:jalAcjL8zTQrDPMa@netsquared-cluster.jmzk3jk.mongodb.net/";
db_name="netsquared-db";
collection_name="contactos";
index_name="embbeding-contactos"

client = MongoClient(connection_string)
collection = client[db_name][collection_name]

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

loader = CSVLoader(file_path='dataset/new-contact.csv')
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(data)

#Cargamos nuevos datos a la database junto a su embedding

vector_search = MongoDBAtlasVectorSearch.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(disallowed_special=()),
    collection=collection,
    index_name=index_name
)