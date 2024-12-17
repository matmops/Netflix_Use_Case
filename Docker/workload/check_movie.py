import os
import subprocess
import json
import configparser
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Read info.ini
config = configparser.ConfigParser()
config.read('info.ini')
url = config.get('INFO', 'URL')

file_name = url.split('/')[-1]
original_file_path = os.path.expanduser(f"~/file_to_process/{file_name}")
converted_file_path = os.path.expanduser(f"~/final/{os.path.splitext(file_name)[0]}.mp4")

# Function to get video duration
def get_video_duration(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True
        )
        duration = json.loads(result.stdout)["format"]["duration"]
        return float(duration)
    except Exception as e:
        logging.error(f"Error getting duration for {file_path}: {e}")
        return None

# Default status
check_status = "FAIL"

# Check if files exist
if not os.path.exists(original_file_path):
    logging.error(f"Original file does not exist: {original_file_path}")
elif not os.path.exists(converted_file_path):
    logging.error(f"Converted file does not exist: {converted_file_path}")
else:
    # Compare durations
    try:
        original_duration = get_video_duration(original_file_path)
        converted_duration = get_video_duration(converted_file_path)

        if original_duration is None or converted_duration is None:
            logging.error("Failed to retrieve durations for video files.")
        elif abs(original_duration - converted_duration) < 0.1:  # Tolerance of 0.1 seconds
            logging.info("Video durations match. Check passed.")
            check_status = "DONE"
        else:
            logging.error(
                f"Video durations do not match. Original: {original_duration}s, Converted: {converted_duration}s"
            )
    except Exception as e:
        logging.error(f"Error during video check: {e}")

# Update the CHECK_STATUS in info.ini
config.set('INFO', 'CHECK_STATUS', check_status)
with open('info.ini', 'w') as configfile:
    config.write(configfile)

logging.info(f"CHECK_STATUS updated to '{check_status}' in info.ini.")
