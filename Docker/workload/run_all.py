import subprocess
import time

def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")

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

    # Keep the container running for a maximum of 5 minutes
    time.sleep(60)
