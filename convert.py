from docx import Document
import csv
import pandas as pd

def convert_docx_to_csv(docx_file, csv_file):
    document = Document(docx_file)

    # Extracción de texto del documento
    text_content = []
    for paragraph in document.paragraphs:
        text_content.append(paragraph.text)

    # Guardar el texto en un archivo CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for line in text_content:
            csv_writer.writerow([line])

def merge_csvs(input_csv, output_csv):
    # Leer los archivos CSV
    df1 = pd.read_csv(output_csv)
    df2 = pd.read_csv(input_csv)

    # Concatenar los DataFrames
    df_combined = pd.concat([df1, df2], ignore_index=True)

    # Escribir el DataFrame combinado de vuelta a un archivo CSV
    df_combined.to_csv(output_csv, index=False)

if __name__ == "__main__":
    # Rutas de los archivos
    input_docx_file = '/Users/gastonmora/Desktop/Net-App/src/dataset/ultimo_documento.docx'
    output_csv_file = '/Users/gastonmora/Desktop/Net-App/src/dataset/output.csv'
    temporary_csv_file = '/Users/gastonmora/Desktop/Net-App/src/dataset/temporary.csv'

    # Convertir documento de Word a CSV
    convert_docx_to_csv(input_docx_file, temporary_csv_file)

    # Combinar archivos CSV
    merge_csvs(temporary_csv_file, output_csv_file)

    print("Proceso completado.")
