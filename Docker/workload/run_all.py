# Updated run_all.py
import subprocess
import os
import sys
import logging
from datetime import datetime
from log_message import create_base_log, send_log_to_queue

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
instance_id = os.getenv("AZURE_APP_INSTANCE_ID")
# Initialize shared log message
log_message = create_base_log(job_id=instance_id, message_id="run_all_12345")

def run_script(script_name):
    try:
        logging.info(f"Starting script: {script_name}")
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        log_message["status"] = "ÉCHEC"
        log_message["error_message"] = f"Error in {script_name}: {str(e)}"
        log_message["end_time"] = datetime.utcnow().isoformat() + "Z"
        send_log_to_queue(log_message)
        logging.error(f"Error occurred in script {script_name}. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    scripts = [
        "get_files.py",
        "get_movie.py",
        "process_movie.py",
        "check_movie.py",
        "send_back_movie.py"
    ]

    try:
        for script in scripts:
            run_script(script)

        # If all scripts pass
        log_message["status"] = "DONE"
        log_message["end_time"] = datetime.utcnow().isoformat() + "Z"
        send_log_to_queue(log_message)
        logging.info("All scripts completed successfully. Log message sent with status DONE.")

    except Exception as e:
        log_message["status"] = "ÉCHEC"
        log_message["error_message"] = str(e)
        log_message["end_time"] = datetime.utcnow().isoformat() + "Z"
        send_log_to_queue(log_message)
        logging.error("An unexpected error occurred in the run_all pipeline.")
        sys.exit(1)
