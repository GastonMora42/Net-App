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
import subprocess


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
    max_tokens=250,
    )

llm = OpenAI()

question = "Porfavor Generame un resumen detallado conservando a modo de variables las siguientes variables de datos (Nombre:,Apellido:,Empresa:,Pais:,Email:,Interacciones:,Especialidad:,Twitter:,Teléfono:,Ultima fecha de contacto:,Deck(pdf):,Sitio Web:,LinkedIn:,Comentarios relevantes:,Resumen por GPT de la reunion:) del contenido de" + csv_content

answer = llm(question)

# Convertir el contenido de answer a un DataFrame de pandas
df = pd.DataFrame([answer], columns=["Resumen"])

# Guardar el DataFrame como un archivo CSV
df.to_csv('dataset/resumen-contacts.csv')

# Obtener la clave SSH desde el secreto de GitHub
ssh_private_key = os.environ.get("PUSH_DB")

#Probamos

# Guardar la clave SSH en un archivo temporal
with open('/tmp/id_rsa', 'w') as f:
    f.write(ssh_private_key)

# Dar permisos adecuados al archivo
subprocess.run(['chmod', '600', '/tmp/id_rsa'])

# Copiar la clave SSH al directorio .ssh
subprocess.run(['cp', '/tmp/id_rsa', '~/.ssh/id_rsa'])

# Configurar nombre de usuario y correo electrónico
subprocess.run(["git", "config", "user.email", "gaston-mora@hotmail.com"])
subprocess.run(["git", "config", "user.name", "GastonMora42"])

# Agregar el archivo generado al área de preparación
subprocess.run(["git", "add", "dataset/resumen-contacts.csv"])

# Hacer un commit con un mensaje descriptivo
subprocess.run(["git", "commit", "-m", "Add resumen generado a raiz de los scripts"])

# Pushear los cambios al repositorio remoto si es necesario
subprocess.run(["git", "push"])

logger.info("Data preparada.....")
