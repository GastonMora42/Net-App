import subprocess
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os


def configure_google_drive():
    gauth = GoogleAuth()
    # Cargar o crear las credenciales en un archivo
    gauth.LoadCredentialsFile("mycreds.txt")

    # Obtener el token de acceso desde la variable de entorno
    access_token = os.getenv('MYCREDSGOOGLE')

    if gauth.credentials is None:
        # Autenticar por primera vez
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refrescar el token si está expirado
        gauth.Refresh()
    else:
        # Autorización válida
        gauth.Authorize()

    # Configurar el token de acceso
    gauth.credentials.access_token = access_token

    # Guardar las credenciales actualizadas
    gauth.SaveCredentialsFile("mycreds.txt")

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
    folder_id = '15ID0ejJRXM7t9GJSKu6Oqjsjc2twimNF'
    local_file_name = '/Users/gastonmora/Desktop/Net-App/dataset/ultimo_documento.docx'
    drive = configure_google_drive()
    download_latest_google_doc(drive, folder_id, local_file_name)

if __name__ == "__main__":
    main()