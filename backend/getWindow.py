import win32gui
import win32ui
import win32con
import win32api
import os
import time
from datetime import datetime
from PIL import Image
from pynput import mouse

clicks = []

# === Global Variables ===
feedback_interval = 10

# === Step 1: Get window handle by title ===
def get_hwnd(title_keyword):
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_keyword.lower() in window_title.lower():
                result.append(hwnd)

    result = []
    win32gui.EnumWindows(enum_handler, result)
    if not result:
        raise Exception(f"No window found with title containing '{title_keyword}'")
    return result[0]

# === Step 2: Capture from window's framebuffer using GDI ===
def capture_window_region(hwnd, region):
    left, top, width, height = region['left'], region['top'], region['width'], region['height']

    window_dc = win32gui.GetWindowDC(hwnd)
    dc_obj = win32ui.CreateDCFromHandle(window_dc)
    cdc = dc_obj.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dc_obj, width, height)
    cdc.SelectObject(bmp)

    # BitBlt from window's DC
    cdc.BitBlt((0, 0), (width, height), dc_obj, (left, top), win32con.SRCCOPY)

    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)

    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    # Cleanup
    win32gui.DeleteObject(bmp.GetHandle())
    cdc.DeleteDC()
    dc_obj.DeleteDC()
    win32gui.ReleaseDC(hwnd, window_dc)

    return img

# === Step 3: Mouse click calibration ===
def on_click(x, y, button, pressed):
    if pressed:
        print(f"Clicked at ({x}, {y})")
        clicks.append((x, y))
        if len(clicks) == 2:
            return False

def calibrate_canvas_click(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x0, y0 = rect[0], rect[1]

    print("\nClick the **top-left corner** of the canvas inside the app window.")
    print("Then click the **bottom-right corner** of the canvas.")

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    x1, y1 = clicks[0]
    x2, y2 = clicks[1]

    region = {
        'left': min(x1, x2) - x0,
        'top': min(y1, y2) - y0,
        'width': abs(x2 - x1),
        'height': abs(y2 - y1)
    }

    print(f"\nCalibrated window-relative region: {region}")
    return region

# === Main Loop ===
def main():
    window_title = "CLIP STUDIO PAINT"
    try:
        hwnd = get_hwnd(window_title)
        print(f"\nFound window handle for '{window_title}'")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Unminimize if minimized
        win32gui.SetForegroundWindow(hwnd)              # Focus the window
        time.sleep(1)
    except Exception as e:
        print(e)
        return

    canvas_region = calibrate_canvas_click(hwnd)

    # Output directory
    output_dir = "captured_images"
    os.makedirs(output_dir, exist_ok=True)

    try:
        while True:
            img = capture_window_region(hwnd, canvas_region)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filepath = os.path.join(output_dir, f"canvas_{timestamp}.png")
            img.save(filepath)
            print(f"Saved canvas image to {filepath}")
            time.sleep(feedback_interval) # in seconds
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

if __name__ == "__main__":
    main()
