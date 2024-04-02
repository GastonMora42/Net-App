import subprocess
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import json

def configure_google_drive():
    gauth = GoogleAuth()
    
    # Obtener el JSON de las credenciales desde la variable de entorno
    credentials_json = os.getenv('MYCREDSGOOGLE')
    
    if credentials_json is None:
        raise ValueError("No se encontró el JSON de credenciales en la variable de entorno")

    # Cargar las credenciales desde el JSON
    credentials = json.loads(credentials_json)
    
    # Configurar las credenciales en gauth
    gauth.credentials = credentials

    # Verificar si el token de acceso está expirado y refrescarlo si es necesario
    if gauth.access_token_expired:
        gauth.Refresh()
    
    # Guardar las credenciales actualizadas
    gauth.SaveCredentialsFile("mycreds.txt")
    
    # Crear el objeto GoogleDrive con las credenciales configuradas
    drive = GoogleDrive(gauth)
    return drive

def download_latest_google_doc(drive, folder_id, local_file_name):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    google_doc_files = [file for file in file_list if file['mimeType'] == 'application/vnd.google-apps.document']

    if not google_doc_files:
        print("No se encontraron documentos de Google en la carpeta.")
        return

    latest_google_doc = max(google_doc_files, key=lambda x: x['modifiedDate'])

    print(f"Descargando el último documento de Google: {latest_google_doc['title']}, Fecha de modificación: {latest_google_doc['modifiedDate']}")

    latest_google_doc.GetContentFile(local_file_name, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    print(f"El último documento se ha descargado exitosamente como {local_file_name}")


def main():
    folder_id = '1T54m4fmnMr-GSznRhdT7YU3mhaCOWerB'
    local_file_name = '/dataset/ultimo_documento.docx'

    drive = configure_google_drive()
    download_latest_google_doc(drive, folder_id, local_file_name)

if __name__ == "__main__":
    main()