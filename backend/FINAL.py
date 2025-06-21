# from PIL import Image
# import numpy as np
# from pathlib import Path
# import shutil
# import imageio.v2 as imageio

# INPUT_FOLDER = "initial_frames"
# OUTPUT_FOLDER = "interpolated_output"
# VIDEO_NAME = "interpolated_video.mp4"
# FPS = 30

# NUM_INTERPOLATED_FRAMES = int(input("How many frames should be interpolated between each keyframe? "))

# def simple_blend_interpolation(img1, img2, num_frames=2):
#     if img1.size != img2.size:
#         img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

#     arr1 = np.array(img1, dtype=np.float32)
#     arr2 = np.array(img2, dtype=np.float32)

#     frames = []
#     for i in range(1, num_frames + 1):
#         alpha = i / (num_frames + 1)
#         blended = (1 - alpha) * arr1 + alpha * arr2
#         blended = np.clip(blended, 0, 255).astype(np.uint8)
#         frames.append(Image.fromarray(blended, 'RGBA'))

#     return frames

# def interpolate_sequence():
#     input_dir = Path(INPUT_FOLDER)
#     output_dir = Path(OUTPUT_FOLDER)
#     output_dir.mkdir(exist_ok=True)

#     # Clear output folder
#     for f in output_dir.glob("*.png"):
#         f.unlink()

#     frame_files = sorted(input_dir.glob("*.png"))
#     if len(frame_files) < 2:
#         print("❌ Need at least 2 frames to interpolate.")
#         return

#     frame_counter = 0
#     all_frames = []

#     for i in range(len(frame_files) - 1):
#         img1 = Image.open(frame_files[i]).convert('RGBA')
#         img2 = Image.open(frame_files[i + 1]).convert('RGBA')

#         # Save original frame image & keep for video
#         output_path = output_dir / f"frame_{frame_counter:04d}.png"
#         img1.save(output_path)
#         print(f"Saved keyframe -> {output_path.name}")
#         all_frames.append(np.array(img1.convert('RGB')))
#         frame_counter += 1

#         # Generate and save interpolated frames & keep for video
#         interpolated = simple_blend_interpolation(img1, img2, NUM_INTERPOLATED_FRAMES)
#         for frame in interpolated:
#             output_path = output_dir / f"frame_{frame_counter:04d}.png"
#             frame.save(output_path)
#             print(f"Saved inbetween -> {output_path.name}")
#             all_frames.append(np.array(frame.convert('RGB')))
#             frame_counter += 1

#     # Save last original frame & keep for video
#     final_img = Image.open(frame_files[-1]).convert('RGBA')
#     output_path = output_dir / f"frame_{frame_counter:04d}.png"
#     final_img.save(output_path)
#     print(f"Saved keyframe -> {output_path.name}")
#     all_frames.append(np.array(final_img.convert('RGB')))
#     frame_counter += 1

#     print(f"\n✅ Done! {frame_counter} frames saved to '{OUTPUT_FOLDER}'.")
#     create_video(all_frames)

# def create_video(frames):
#     print(f"🎞 Creating video '{VIDEO_NAME}' at {FPS} FPS...")
#     with imageio.get_writer(VIDEO_NAME, fps=FPS, codec='libx264', quality=8) as writer:
#         for frame in frames:
#             writer.append_data(frame)
#     print(f"✅ Video saved to '{VIDEO_NAME}'")

# if __name__ == "__main__":
#     interpolate_sequence()

from PIL import Image
import numpy as np
from pathlib import Path
import shutil
import imageio.v2 as imageio
import re

INPUT_FOLDER = "initial_frames"
OUTPUT_FOLDER = "interpolated_output"
VIDEO_NAME = "interpolated_video.mp4"
FPS = 64

NUM_INTERPOLATED_FRAMES = int(input("How many frames should be interpolated between each keyframe? "))

def simple_blend_interpolation(img1, img2, num_frames=2):
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)

    frames = []
    for i in range(1, num_frames + 1):
        alpha = i / (num_frames + 1)
        blended = (1 - alpha) * arr1 + alpha * arr2
        blended = np.clip(blended, 0, 255).astype(np.uint8)
        frames.append(Image.fromarray(blended, 'RGBA'))

    return frames

def extract_number(fpath):
    match = re.search(r'(\d+)', fpath.stem)
    return int(match.group(1)) if match else -1

def interpolate_sequence():
    input_dir = Path(INPUT_FOLDER)
    output_dir = Path(OUTPUT_FOLDER)
    output_dir.mkdir(exist_ok=True)

    # Clear output folder
    for f in output_dir.glob("*.png"):
        f.unlink()

    frame_files = sorted(input_dir.glob("*.png"), key=extract_number)
    if len(frame_files) < 2:
        print("❌ Need at least 2 frames to interpolate.")
        return

    frame_counter = 0
    all_frames = []

    for i in range(len(frame_files) - 1):
        img1 = Image.open(frame_files[i]).convert('RGBA')
        img2 = Image.open(frame_files[i + 1]).convert('RGBA')

        # Save original frame image & keep for video
        output_path = output_dir / f"frame_{frame_counter:04d}.png"
        img1.save(output_path)
        print(f"Saved keyframe -> {output_path.name}")
        all_frames.append(np.array(img1.convert('RGB')))
        frame_counter += 1

        # Generate and save interpolated frames & keep for video
        interpolated = simple_blend_interpolation(img1, img2, NUM_INTERPOLATED_FRAMES)
        for frame in interpolated:
            output_path = output_dir / f"frame_{frame_counter:04d}.png"
            frame.save(output_path)
            print(f"Saved inbetween -> {output_path.name}")
            all_frames.append(np.array(frame.convert('RGB')))
            frame_counter += 1

    # Save last original frame & keep for video
    final_img = Image.open(frame_files[-1]).convert('RGBA')
    output_path = output_dir / f"frame_{frame_counter:04d}.png"
    final_img.save(output_path)
    print(f"Saved keyframe -> {output_path.name}")
    all_frames.append(np.array(final_img.convert('RGB')))
    frame_counter += 1

    print(f"\n✅ Done! {frame_counter} frames saved to '{OUTPUT_FOLDER}'.")
    create_video(all_frames)

def create_video(frames):
    print(f"🎞 Creating video '{VIDEO_NAME}' at {FPS} FPS...")
    with imageio.get_writer(VIDEO_NAME, fps=FPS, codec='libx264', quality=8) as writer:
        for frame in frames:
            writer.append_data(frame)
    print(f"✅ Video saved to '{VIDEO_NAME}'")

if __name__ == "__main__":
    interpolate_sequence()
