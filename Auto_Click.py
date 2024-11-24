import time
import pyautogui
print(pyautogui.size())
#pyautogui.moveTo(100, 100, duration = 1)
print(pyautogui.position())
#pyautogui.click(659, 660)
count = 0
while(count < 700):
	time.sleep(1)
	#pyautogui.click(1259, 660)
	pyautogui.click(617, 660)
	count = count + 1
	print(count)
##Point(x=488, y=655)
