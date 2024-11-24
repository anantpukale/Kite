import pyautogui
import time

# # Wait for 3 seconds before starting (so you can switch to the desired window)
time.sleep(3)

# Click at specific coordinates (x, y)
x, y = 952, 671  # Change these coordinates as needed
pyautogui.click(x, y)

# You can also specify the number of clicks and interval between clicks
# For example: Double-click
while True:
	time.sleep(0.5)
	pyautogui.click(x, y, clicks=2, interval=0.25)

# time.sleep(3)  # Move your mouse to the desired position
# print(pyautogui.position())  # Prints the current mouse coordinates (x, y)
