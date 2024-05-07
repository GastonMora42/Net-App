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

from langchain_community.document_loaders.mongodb import MongodbLoader

openai_api_key = os.environ.get("OPENAI_API_KEY")

embeddingopenai = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

connection_string="mongodb+srv://netsquared-db:L0PFljJA6c9bJNbV@netsquared-cluster.jmzk3jk.mongodb.net/";
db_name="netsquared-db";
collection_name="contactos";
index_name="embbeding-contactos"

client = MongoClient(connection_string)
collection = client[db_name][collection_name]

loader = CSVLoader(file_path='dataset/Contacts-Main View.csv')
data = loader.load()

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(data)

vector_search = MongoDBAtlasVectorSearch.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(disallowed_special=()),
    collection=collection,
    index_name=index_name,
)