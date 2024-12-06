import os
import subprocess
import configparser

# Lire l'URL depuis le fichier info.ini pour obtenir le nom du fichier
config = configparser.ConfigParser()
config.read('info.ini')
url = config.get('INFO', 'URL')

# Extraire le nom du fichier depuis l'URL
file_name = url.split('/')[-1]

# Chemin du fichier téléchargé
download_file_path = os.path.expanduser(f"~/file_to_process/{file_name}")

# Vérifier si le fichier existe
if not os.path.exists(download_file_path):
    print(f"Le fichier {download_file_path} n'existe pas.")
else:
    # Convertir le fichier en format MP4
    output_folder = os.path.expanduser("~/final")
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.mp4")

    # Utiliser ffmpeg pour convertir le fichier
    subprocess.run(["ffmpeg", "-i", download_file_path, output_file_path])

    print(f"Fichier converti et stocké dans {output_file_path}")