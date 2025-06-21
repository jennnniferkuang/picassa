import os
import time
import base64
from datetime import datetime
from openai import OpenAI  
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key="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")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "captured_images"))

feedback_interval = 10
cleanup_interval = feedback_interval * 2

def get_sorted_images():
    files = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    files.sort(key=lambda f: os.path.getctime(os.path.join(image_dir, f)))
    return files

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def stream_feedback(image_path):
    image_b64 = image_to_base64(image_path)
    image_url = f"data:image/png;base64,{image_b64}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an art critic. Provide constructive, kind feedback on a drawing work in progress."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Here is my current work in progress drawing. What should I improve on?"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            stream=True 
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
    except Exception as e:
        print(f"❌ Error generating feedback: {e}")

def delete_oldest_image():
    images = get_sorted_images()
    if images:
        oldest = os.path.join(image_dir, images[0])
        os.remove(oldest)
        print(f"🗑️ Deleted oldest image: {os.path.basename(oldest)}")

def main():
    last_cleanup = time.time()
    print("\n🎬 Monitoring images and generating feedback...")

    while True:
        images = get_sorted_images()

        if images:
            latest_image = os.path.join(image_dir, images[-1])
            stream_feedback(latest_image)

        if time.time() - last_cleanup >= cleanup_interval:
            delete_oldest_image()
            last_cleanup = time.time()

        time.sleep(feedback_interval)

if __name__ == "__main__":
    main()
