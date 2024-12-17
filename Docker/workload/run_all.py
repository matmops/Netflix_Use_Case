import subprocess
import time
import sys

def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
        print(f"Script {script_name} ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        sys.exit(1)  # Exit the entire process with an error code

if __name__ == "__main__":
    scripts = [
        "get_files.py",
        "get_movie.py",
        "process_movie.py",
        "check_movie.py",
        "send_back_movie.py"
    ]

    for script in scripts:
        run_script(script)

    # If all scripts ran successfully, this will be executed
    print("All scripts completed successfully.")

    # Keep the container running for a maximum of 60 seconds (1 minute)
    time.sleep(60)
