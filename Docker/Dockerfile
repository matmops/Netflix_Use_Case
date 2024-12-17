# Utiliser une image de base Python 3.9 slim
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app/workload

# Installer Azure CLI et la bibliothèque azure-identity
RUN apt-get update && \
  apt-get install -y curl ffmpeg && \
  curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
  pip install azure-identity azure-storage-blob azure-servicebus


# Copier le contenu local dans le conteneur
COPY . /app

# Commande par défaut pour garder le conteneur en cours d'exécution
CMD sh -c "python get_files.py && python get_movie.py && python process_movie.py && python check_movie.py && python send_back_movie.py"

