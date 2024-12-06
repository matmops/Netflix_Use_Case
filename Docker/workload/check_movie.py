import os
import subprocess
import json
import configparser

# Lire l'URL depuis le fichier info.ini pour obtenir le nom du fichier
config = configparser.ConfigParser()
config.read('info.ini')
url = config.get('INFO', 'URL')

# Extraire le nom du fichier depuis l'URL
file_name = url.split('/')[-1]

# Chemin du fichier téléchargé
original_file_path = os.path.expanduser(f"~/file_to_process/{file_name}")

# Chemin du fichier converti
converted_file_path = os.path.expanduser(f"~/final/{os.path.splitext(file_name)[0]}.mp4")

# Fonction pour obtenir la durée d'un fichier vidéo
def get_video_duration(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = json.loads(result.stdout)["format"]["duration"]
    return float(duration)

# Vérifier si les fichiers existent
if not os.path.exists(original_file_path):
    print(f"Le fichier original {original_file_path} n'existe pas.")
    check_status = "Le fichier original n'existe pas."
elif not os.path.exists(converted_file_path):
    print(f"Le fichier converti {converted_file_path} n'existe pas.")
    check_status = "Le fichier converti n'existe pas."
else:
    # Obtenir la durée des deux fichiers
    original_duration = get_video_duration(original_file_path)
    converted_duration = get_video_duration(converted_file_path)

    # Comparer les durées
    if abs(original_duration - converted_duration) < 0.1:  # Tolérance de 0.1 seconde
        print("Le traitement a été bien effectué. Les durées des fichiers sont les mêmes.")
        check_status = "DONE"
    else:
        print(f"Le traitement a échoué. Durée originale: {original_duration} s, Durée convertie: {converted_duration} s.")
        check_status = "FAIL"

# Mettre à jour le fichier info.ini avec le statut du check
config.set('INFO', 'CHECK_STATUS', check_status)
with open('info.ini', 'w') as configfile:
    config.write(configfile)