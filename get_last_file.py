import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import json

#Fixing

def configure_google_drive():
    gauth = GoogleAuth()

    # Obtener el token de acceso desde la variable de entorno
    access_token_json = os.getenv('REFRES_TOKEN_GOOGLE')

    if access_token_json is None:
        raise ValueError("No se encontró el token de acceso en la variable de entorno REFRES_TOKEN_GOOGLE")

    # Cargar el token de acceso desde la cadena JSON
    try:
        creds_dict = json.loads(access_token_json)
    except json.JSONDecodeError as e:
        raise ValueError("El token de acceso no está en formato JSON válido") from e

    # Configurar las credenciales con el token de acceso
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_service_account_info(creds_dict, scopes=scopes)
    gauth.credentials = creds

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
    local_file_name = '/Users/gastonmora/Desktop/Net-App/dataset/ultimo_documento.docx'

    try:
        drive = configure_google_drive()
        download_latest_google_doc(drive, folder_id, local_file_name)
    except Exception as e:
        print(f"Error al configurar Google Drive: {e}")

if __name__ == "__main__":
    main()

