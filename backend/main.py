import subprocess
import os
import time

# ...existing code...
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

window_capture = os.path.join(BASE_DIR, "getWindow.py")
feedback = os.path.join(BASE_DIR, "critiqueResponse.py")
image_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "captured_images"))
# ...existing code...

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

    print("🚀 Launching canvas capture")
    capture_proc = run_script_background(window_capture)

    wait_for_first_image()

    print("🎨 Launching drawing feedback system")
    feedback_proc = run_script_background(feedback)

    try:
        capture_proc.wait()
        feedback_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Terminating processes")
        capture_proc.terminate()
        feedback_proc.terminate()

if __name__ == "__main__":
    main()