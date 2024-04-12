import os
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.client import OAuth2Credentials
from datetime import datetime

def configure_google_drive():
    gauth = GoogleAuth()

    # Obtener las credenciales desde las variables de entorno
    credentials_json = os.getenv('MYCREDSGOOGLE')
    credentials_dict = json.loads(credentials_json)

    # Crear un objeto OAuth2Credentials desde el JSON
    credentials = OAuth2Credentials(
        credentials_dict['access_token'],
        credentials_dict['client_id'],
        credentials_dict['client_secret'],
        credentials_dict['refresh_token'],
        credentials_dict['token_expiry'],
        credentials_dict['token_uri'],
        credentials_dict['user_agent'],
        credentials_dict['revoke_uri'],
        credentials_dict['id_token'],
        credentials_dict['id_token_jwt'],
        credentials_dict['token_response'],
        credentials_dict['scopes']
    )

    # Asignar las credenciales al objeto gauth
    gauth.credentials = credentials

    # Verificar si el token de acceso está expirado y refrescarlo si es necesario
    if is_token_expired(credentials_dict['token_expiry']):
        gauth.Refresh()

    # Crear el objeto GoogleDrive con las credenciales configuradas
    drive = GoogleDrive(gauth)
    return drive

def is_token_expired(token_expiry_str):
    token_expiry_datetime = datetime.strptime(token_expiry_str, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.utcnow()
    return now >= token_expiry_datetime

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
    local_file_name = 'dataset/ultimo_documento.docx'

    drive = configure_google_drive()
    download_latest_google_doc(drive, folder_id, local_file_name)

if __name__ == "__main__":
    main()