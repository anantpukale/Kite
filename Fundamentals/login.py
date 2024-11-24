from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException,ElementClickInterceptedException

# Define the path to your chromedriver
#chromedriver_path = '/path/to/chromedriver'  # Replace with the actual path to your chromedriver
chrome_options = Options()

# Add argument to mimic a normal browser session
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Create a new Chrome session
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Go to the Screener login page
driver.get("https://www.screener.in/login/")

# Wait for the page to load
time.sleep(2)

# Locate the username and password input fields and fill them in
email_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")

email_input.send_keys("anant.pukale@gmail.com")  # Replace with your email
password_input.send_keys("277401anant")        # Replace with your password

# Press the Enter key or click the submit button
password_input.send_keys(Keys.RETURN)

# Wait for a few seconds to allow the login process to complete
time.sleep(5)

# Check if login was successful (you can check for certain elements like the dashboard or "Logout" button)
if "Logout" in driver.page_source:
    print("Login successful!")
else:
    print("Login failed. Check your credentials or inspect the website for CAPTCHAs.")

# Optionally, navigate to another page after logging in
dashboard_url = "https://www.screener.in/company/RELIANCE/consolidated/"
driver.get(dashboard_url)

# Wait for page to load
time.sleep(3)

# Print the page source or take some action on the dashboard
#print(driver.page_source)

# Close the browser session
#driver.quit()
