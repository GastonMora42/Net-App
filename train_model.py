import os
from pymongo import MongoClient
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configuración de la conexión a MongoDB
connection_string = "mongodb+srv://gastonmora1742:jIhdEUoE9FWAcunB@jett-cluster.psm4rdx.mongodb.net/"
db_name = "test"
collection_name = "users"
index_name = "jett-index"

# Inicialización del embedding de OpenAI
openai_api_key = os.environ.get("OPENAI_API_KEY")
embedding_openai = OpenAIEmbeddings(
    openai_api_key=openai_api_key,
    model="text-embedding-ada-002"
)

client = MongoClient(connection_string)
collection = client[db_name][collection_name]

# Leer todos los documentos de la colección
documents = list(collection.find())

# Campos relevantes para generar el texto
field_names = ['name', 'username', 'email', 'bio', 'skills', 'skills2', 'skills3']

# Función para generar embeddings y source, y actualizar el documento
def generate_and_store_embeddings(doc):
    if 'embedding' not in doc or 'source' not in doc:
        text = " ".join(filter(None, [doc.get(field, "") for field in field_names]))
        embedding = embedding_openai.embed_query(text)

        # Generar el source basado en la información del documento
        source = f"Document from collection {collection_name} with id {doc.get('_id')}"
        
        # Actualizar el documento en la base de datos con el embedding y el source
        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'embedding': embedding, 'source': source}}
        )

# Inicializar el text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

# Lista para almacenar todos los documentos divididos
all_split_docs = []

# Procesar documentos
for doc in documents:
    try:
        # Generar y almacenar embeddings y source si es un documento nuevo
        generate_and_store_embeddings(doc)

        # No es necesario dividir documentos si no se desea crear nuevos fragmentos
        # Si fuera necesario dividir y almacenar, aquí iría la lógica

    except KeyError as e:
        print(f"Error procesando el documento {doc.get('_id')}: {e}")
    except Exception as e:
        print(f"Otro error ocurrió: {e}")


    # Inicialización de la búsqueda vectorial en MongoDB usando from_documents
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=all_split_docs,
        embedding=embedding_openai,
        collection=collection,
        index_name=index_name
    )
    print("Embeddings y sources generados correctamente, documentos divididos y búsqueda vectorial inicializada.")
else:
    print("No se encontraron documentos válidos para dividir.")
