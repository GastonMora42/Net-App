import subprocess
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

def configure_google_cloud_storage():
    subprocess.run(['gcloud', 'auth', 'activate-service-account', '--key-file', 'netsquared-407819-9ddae082973b.json'])


def track_and_push():
     # Rastrear el archivo local output.csv con DVC
    subprocess.run(['dvc', 'add', '/Users/gastonmora/Desktop/Net-App/dataset/output.csv'])

    # Agregar un nuevo remoto para el rastreo en Google Cloud Storage
    subprocess.run(['dvc', 'remote', 'add', '-f', 'gs_remote', 'gs://model-dataset-netsquared-tracker/dataset'])

    # Subir el archivo rastreado a Google Cloud Storage
    subprocess.run(['dvc', 'push', '-r', 'gs_remote'])
  
    subprocess.run(['git', 'add', '.'])

    subprocess.run(['git', 'commit', '-m', 'Agrega y rastrea carpeta en DVC'])

    subprocess.run(['dvc', 'push'])

    # Copiar el archivo .dvc al directorio de Google Cloud Storage
    subprocess.run(['gsutil', 'cp', 'output.csv.dvc', 'gs://model-dataset-netsquared-tracker/dataset/output.csv.dvc'])
        

if __name__ == "__main__":
    
     # Configurar las credenciales para Google Cloud Storage
    configure_google_cloud_storage()

    # Ejecutar el rastreo y la carga
    track_and_push()