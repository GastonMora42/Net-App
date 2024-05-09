import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def get_drive_service():
    # Obtener las credenciales desde el secreto en GitHub
    credentials_json = os.getenv('DRIVE_CREDS')

    if not credentials_json:
        raise ValueError("Las credenciales de Google no fueron encontradas en el secreto.")

    credentials_dict = json.loads(credentials_json)

    # Crea las credenciales desde el diccionario JSON
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)

    # Crea el servicio de Google Drive
    service = build('drive', 'v3', credentials=credentials)
    return service

def download_latest_google_doc(service, folder_id, local_file_name):
    try:
        # Busca los archivos en la carpeta específica ordenados por fecha de modificación descendente
        file_list = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.document'",
            orderBy='modifiedTime desc',
        ).execute()

        if 'files' in file_list and len(file_list['files']) > 0:
            latest_google_doc = file_list['files'][0]
            print(f"Descargando el último documento de Google: {latest_google_doc['name']}, ID: {latest_google_doc['id']}, Fecha de modificación: {latest_google_doc.get('modifiedTime', 'N/A')}")

            # Exportar el documento de Google como un archivo de Word (.docx)
            request = service.files().export_media(fileId=latest_google_doc['id'], mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            with open(local_file_name, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            print(f"El último documento se ha descargado exitosamente como {local_file_name}")
        else:
            print("No se encontraron documentos de Google en la carpeta especificada.")

    except Exception as e:
        print(f"Error al descargar el documento: {e}")

def main():
    folder_id = '15ID0ejJRXM7t9GJSKu6Oqjsjc2twimNF'
    local_file_name = 'dataset/ultimo_documento.docx'

    service = get_drive_service()
    if service:
        download_latest_google_doc(service, folder_id, local_file_name)

if __name__ == "__main__":
    main()
