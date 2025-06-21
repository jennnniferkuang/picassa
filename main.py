import subprocess
import os
import time

window_capture = "getWindow.py"
feedback = "blip2.py"
image_dir = "captured_images"

def wait_for_first_image():
    print("⏳ Waiting for images to appear in 'captured_images/'...")
    while True:
        if os.listdir(image_dir):
            print("✅ Image(s) found. Starting feedback system...")
            return
        time.sleep(1)

def run_script_background(script_name):
    return subprocess.Popen(["python", script_name])

def main():
    os.makedirs(image_dir, exist_ok=True)

    print("Launching canvas capture")
    capture_proc = run_script_background(window_capture)

    wait_for_first_image()

    print("Launching analysis")
    feedback_proc = run_script_background(feedback)

    try:
        capture_proc.wait()
        feedback_proc.wait()
    except KeyboardInterrupt:
        print("\nTerminating process")
        capture_proc.terminate()
        feedback_proc.terminate()

if __name__ == "__main__":
    main()