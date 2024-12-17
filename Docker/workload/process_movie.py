import os
import subprocess
import configparser
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Read info.ini
config = configparser.ConfigParser()
config.read('info.ini')
url = config.get('INFO', 'URL')

# Extract file name
file_name = url.split('/')[-1]
download_file_path = os.path.expanduser(f"~/file_to_process/{file_name}")

# Verify file existence
if not os.path.exists(download_file_path):
    logging.error(f"File {download_file_path} does not exist.")
    exit(1)

# Convert the file using ffmpeg
output_folder = os.path.expanduser("~/final")
os.makedirs(output_folder, exist_ok=True)
output_file_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.mp4")

try:
    subprocess.run(["ffmpeg", "-i", download_file_path, output_file_path], check=True)
    logging.info(f"File converted successfully to {output_file_path}")
except subprocess.CalledProcessError as e:
    logging.error(f"Error during ffmpeg processing: {e}")
    exit(1)
