from dvc.api import read
from io import StringIO
import sys
import logging
from dvc import api
import re
from langchain.llms import OpenAI
import csv
import io
import os
import openai
import pandas as pd


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt='%H:%M:%S',
    stream=sys.stderr
)

#Modificamos estructura en la DB

logger = logging.getLogger(__name__)

logging.info("Fetching data.....")

ruta_dvc = api.read('dataset/output.csv', remote='model-tracker')

contacts_data = pd.read_csv(StringIO(ruta_dvc))

logging.info("Leeyendo el archivo CSV y carga su contenido en una lista de listas")

with open('dataset/Contacts-Main View.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    data = list(csvreader)

csv_string = io.StringIO()
csv_writer = csv.writer(csv_string)
csv_writer.writerows(data)
csv_content = csv_string.getvalue()

logging.info("Generando resumen de los datos a raiz de los meetings.....")

api_key = os.environ.get("OPENAI_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

llm_gpt3_5 = OpenAI(
    model_name="gpt-4-turbo",
    n=1,
    temperature=0,
    max_tokens=100,
    )

llm = OpenAI()

question = "Porfavor Generame un documento detallado y resumido del contenido de" + csv_content

answer = llm(question)

# Convertir el contenido de answer a un DataFrame de pandas
df = pd.DataFrame([answer], columns=["Resumen"])

# Guardar el DataFrame como un archivo CSV
df.to_csv('dataset/resumen-contacts.csv')

logger.info("Data preparada.....")
