import os
import time
import random
import math
import cv2
import keyboard
import mss
import numpy as np
import pygetwindow as gw
import win32api
import win32con
import warnings
from pywinauto import Application

# Interval for checking the "Play" button in seconds
CHECK_INTERVAL = 5

warnings.filterwarnings("ignore", category=UserWarning, module='pywinauto')


def list_windows_by_title(title_keywords):
    windows = gw.getAllWindows()
    filtered_windows = []
    for window in windows:
        for keyword in title_keywords:
            if keyword.lower() in window.title.lower():
                filtered_windows.append((window.title, window._hWnd))
                break
    return filtered_windows


class Logger:
    def __init__(self, prefix=None):
        self.prefix = prefix

    def log(self, data: str):
        if self.prefix:
            print(f"{self.prefix} {data}")
        else:
            print(data)


class AutoClicker:
    def __init__(self, hwnd, target_colors_hex, nearby_colors_hex, threshold, logger, target_percentage):
        self.hwnd = hwnd
        self.target_colors_hex = target_colors_hex
        self.nearby_colors_hex = nearby_colors_hex
        self.threshold = threshold
        self.logger = logger
        self.target_percentage = target_percentage
        self.running = False
        self.clicked_points = []
        self.iteration_count = 0
        self.last_check_time = time.time()

    @staticmethod
    def hex_to_hsv(hex_color):
        hex_color = hex_color.lstrip('#')
        h_len = len(hex_color)
        rgb = tuple(int(hex_color[i:i + h_len // 3], 16) for i in range(0, h_len, h_len // 3))
        rgb_normalized = np.array([[rgb]], dtype=np.uint8)
        hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)
        return hsv[0][0]

    @staticmethod
    def click_at(x, y):
        try:
            if not (0 <= x < win32api.GetSystemMetrics(0) and 0 <= y < win32api.GetSystemMetrics(1)):
                raise ValueError(f"Off-screen coordinates: ({x}, {y})")
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        except Exception as e:
            print(f"Error when setting cursor position: {e}")

    def toggle_script(self):
        self.running = not self.running
        r_text = "running" if self.running else "stopped"
        self.logger.log(f'Status changed: {r_text}')

    def is_near_color(self, hsv_img, center, target_hsvs, radius=8):
        x, y = center
        height, width = hsv_img.shape[:2]
        for i in range(max(0, x - radius), min(width, x + radius + 1)):
            for j in range(max(0, y - radius), min(height, y + radius + 1)):
                distance = math.sqrt((x - i) ** 2 + (y - j) ** 2)
                if distance <= radius:
                    pixel_hsv = hsv_img[j, i]
                    for target_hsv in target_hsvs:
                        if np.allclose(pixel_hsv, target_hsv, atol=[1, 50, 50]):
                            return True
        return False

    def check_and_click_play_button(self, sct, monitor):
        current_time = time.time()
        if current_time - self.last_check_time >= CHECK_INTERVAL:
            self.last_check_time = current_time
            templates = [
                cv2.imread(os.path.join("template_png", "template_play_button.png"), cv2.IMREAD_GRAYSCALE),
                cv2.imread(os.path.join("template_png", "template_play_button1.png"), cv2.IMREAD_GRAYSCALE),
                cv2.imread(os.path.join("template_png", "close_button.png"), cv2.IMREAD_GRAYSCALE),
                cv2.imread(os.path.join("template_png", "captcha.png"), cv2.IMREAD_GRAYSCALE)  # Adding a new template
            ]

            for template in templates:
                if template is None:
                    self.logger.log("The template file could not be loaded.")
                    continue

                template_height, template_width = template.shape

                img = np.array(sct.grab(monitor))
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= self.threshold)

                matched_points = list(zip(*loc[::-1]))

                if matched_points:
                    pt_x, pt_y = matched_points[0]
                    cX = pt_x + template_width // 2 + monitor["left"]
                    cY = pt_y + template_height // 2 + monitor["top"]

                    self.click_at(cX, cY)
                    self.logger.log(f'Clicked the button: {cX} {cY}')
                    self.clicked_points.append((cX, cY))
                    break  # Stop checking after the first match found


    def click_color_areas(self):
        app = Application().connect(handle=self.hwnd)
        window = app.window(handle=self.hwnd)
        window.set_focus()

        target_hsvs = [self.hex_to_hsv(color) for color in self.target_colors_hex]
        nearby_hsvs = [self.hex_to_hsv(color) for color in self.nearby_colors_hex]

        with mss.mss() as sct:
            keyboard.add_hotkey('F6', self.toggle_script)

            while True:
                if self.running:
                    rect = window.rectangle()
                    monitor = {
                        "top": rect.top,
                        "left": rect.left,
                        "width": rect.width(),
                        "height": rect.height()
                    }
                    img = np.array(sct.grab(monitor))
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

                    for target_hsv in target_hsvs:
                        lower_bound = np.array([max(0, target_hsv[0] - 1), 30, 30])
                        upper_bound = np.array([min(179, target_hsv[0] + 1), 255, 255])
                        mask = cv2.inRange(hsv, lower_bound, upper_bound)
                        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                        num_contours = len(contours)
                        num_to_click = int(num_contours * self.target_percentage)
                        contours_to_click = random.sample(contours, num_to_click)

                        for contour in reversed(contours_to_click):
                            if cv2.contourArea(contour) < 6:
                                continue

                            M = cv2.moments(contour)
                            if M["m00"] == 0:
                                continue
                            cX = int(M["m10"] / M["m00"]) + monitor["left"]
                            cY = int(M["m01"] / M["m00"]) + monitor["top"]

                            if not self.is_near_color(hsv, (cX - monitor["left"], cY - monitor["top"]), nearby_hsvs):
                                continue

                            if any(math.sqrt((cX - px) ** 2 + (cY - py) ** 2) < 35 for px, py in self.clicked_points):
                                continue
                            cY += 5
                            self.click_at(cX, cY)
                            self.logger.log(f'clicked: {cX} {cY}')
                            self.clicked_points.append((cX, cY))

                    self.check_and_click_play_button(sct, monitor)
                    time.sleep(0.1)
                    self.iteration_count += 1
                    if self.iteration_count >= 5:
                        self.clicked_points.clear()
                        self.iteration_count = 0


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    keywords = ["Blum", "Telegram"]
    windows = list_windows_by_title(keywords)

    if not windows:
        print("There are no windows containing the specified \"Blum\" or \"Telegram\" keywords.")
        exit()

    print("Available windows to choose from:")
    for i, (title, hwnd) in enumerate(windows):
        print(f"{i + 1}: {title}")

    choice = int(input("Enter the window number where the Blum bot is open: ")) - 1
    if choice < 0 or choice >= len(windows):
        print("Wrong choice.")
        exit()

    hwnd = windows[choice][1]

    while True:
        try:
            target_percentage = input("Enter a value between 0 and 1 to randomize star clicking, where 1 means collecting all the stars. (The choice of value depends on many factors: screen size, window size, etc.)\nI recommend choosing a value between 0.04 and 0.08 to collect around 100-160 stars.\nYou need to select the required value yourself: ")
            target_percentage = target_percentage.replace(',', '.')
            target_percentage = float(target_percentage)
            if 0 <= target_percentage <= 1:
                break
            else:
                print("Please enter a value between 0 and 1.")
        except ValueError:
            print("Invalid format. Please enter a number.")

    logger = Logger()
    logger.log("Welcome to the AutoClickerBlum")
    logger.log('After launching the Blum mini-game, press the F6 key on your keyboard to start/pause the script.')
    target_colors_hex = ["#c9e100", "#bae70e"]
    nearby_colors_hex = ["#abff61", "#87ff27"]
    threshold = 0.8  # Threshold of template matching

    auto_clicker = AutoClicker(hwnd, target_colors_hex, nearby_colors_hex, threshold, logger, target_percentage)
    try:
        auto_clicker.click_color_areas()
    except Exception as e:
        logger.log(f"An error has occurred: {e}")
    for i in reversed(range(5)):
        print(f"The script will stop in {i}")
        time.sleep(1)
