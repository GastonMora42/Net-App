from dvc.api import read
import pandas as pd
import numpy
import openai
import langchain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma
from datetime import datetime
from io import StringIO
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
import random
import sys
from langchain.chat_models import ChatOpenAI
import logging
from sklearn.pipeline import Pipeline
from langchain.embeddings import OpenAIEmbeddings
import os
from pymongo import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch

api_key = os.environ.get("OPENAI_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

embeddingopenai = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

connection_string = "mongodb+srv://gastonmora1742:jIhdEUoE9FWAcunB@jett-cluster.psm4rdx.mongodb.net/"
db_name = "index-contactos"
collection_name = "index"
index_name = "index_name"

client = MongoClient(connection_string)
collection = client[db_name][collection_name]

# Load CSV data
loader = CSVLoader(file_path='dataset/new-contact.csv')
data = loader.load()

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(data)

# Insert documents and embeddings into MongoDB using MongoDBAtlasVectorSearch
vector_search = MongoDBAtlasVectorSearch(embedding=embeddings, collection=collection, index_name=index_name)

for doc in docs:
    # Convert document to langchain Document object
    document = Document(content=doc.content, metadata=doc.metadata)

    # Calculate embedding for the document
    embedding = embeddings.embed(doc.content)

    # Insert document and its embedding into MongoDB
    vector_search.insert(document=document, embedding=embedding)

print("Documents and embeddings inserted successfully into MongoDB.")
