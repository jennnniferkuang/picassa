import os
import time
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
from datetime import datetime

# === Parameters ===
image_dir = "captured_images"
feedback_interval = 10  # Seconds between feedback
max_feedback_length = 50

# === Load BLIP-2 Model ===
print("🔄 Loading BLIP-2 model (this may take a moment)...")
device = "cuda" if torch.cuda.is_available() else "cpu"

processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16 if device == "cuda" else torch.float32)
model.to(device)
print("✅ BLIP-2 model loaded.")

def get_sorted_images():
    files = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    files.sort(key=lambda f: os.path.getctime(os.path.join(image_dir, f)))
    return files

def give_feedback(image_path):
    with Image.open(image_path) as img:
        image = img.convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device, torch.float16 if device == "cuda" else torch.float32)

    generated_ids = model.generate(**inputs, 
    max_new_tokens=max_feedback_length,
    do_sample=True,
    temperature=0.9,
    top_p=0.95
    )
    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n📝 [{timestamp}] Feedback for {os.path.basename(image_path)}:\n➡ {caption}")

def delete_oldest():
    images = get_sorted_images()
    while len(images) > 2:
        oldest = images[0]
        os.remove(os.path.join(image_dir, oldest))
        print(f"🗑️ Deleted oldest image: {oldest}")
        images = get_sorted_images()  # Refresh the list after deletion

# === Main Loop ===
def main():    
    print("\n🎬 Monitoring images and generating feedback...")
    while True:
        images = get_sorted_images()
        if images:
            latest_image = os.path.join(image_dir, images[-1])
            give_feedback(latest_image)

        delete_oldest()
        time.sleep(feedback_interval)

if __name__ == "__main__":
    main()
