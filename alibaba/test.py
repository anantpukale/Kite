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

# Initialize the driver (here Chrome)
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
chrome_options = Options()

# Add argument to mimic a normal browser session
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Launch Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Remove the WebDriver flag from the navigator
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


# Define the URL for Alibaba login and the product page
login_url = "https://login.alibaba.com"
#product_url = "https://www.aliexpress.com/item/1005007550287799.html"
#product_url = "https://www.alibaba.com/product-detail/6-ch-r-c-construction-toy_1600341626120.html?spm=a2700.galleryofferlist.wending_right.4.4dcf13a0pRbhIB"

def alibaba_login(username, password):
    # Navigate to login page
    driver.get(login_url)
    time.sleep(5)  # Wait for the page to load

    # Locate username and password fields and enter credentials
    #username_input = driver.find_element(By.ID, "sign-in-form-pc")
    username_input = driver.find_element(By.CSS_SELECTOR, "input[name='account']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")

    username_input.send_keys(username)
    password_input.send_keys(password)

    # Submit login form
    login_button = driver.find_element(By.CLASS_NAME, "sif_form-submit")
    login_button.click()

    time.sleep(5)  # Wait for login to complete

    try:
        # Switch to the iframe containing the slider
        iframe = driver.find_element(By.ID, "baxia-dialog-content")
        driver.switch_to.frame(iframe)

        # Wait for the slider to become visible
        time.sleep(2)

        # Locate the slider element (adjust the selector if necessary)
        slider = driver.find_element(By.CLASS_NAME, "nc_iconfont.btn_slide")

        # Create ActionChains object to simulate the slider movement
        action = ActionChains(driver)

        # Click and hold the slider
        action.click_and_hold(slider).perform()
        print("slider functionality")
        # Move the slider to the right by an offset (experiment with this value)
        action.move_by_offset(100, 0).perform()  # Move slider by 300 pixels to the right (adjust if necessary)
        time.sleep(2)
        action.move_by_offset(200, 0).perform()
        # Wait for any further actions to complete
        time.sleep(2)
        action.move_by_offset(20, 0).perform()
        # Wait for any further actions to complete
        time.sleep(2)
        action.move_by_offset(50, 0).perform()
        # Wait for any further actions to complete
        time.sleep(12)
        # Release the slider
        action.release().perform()

        # Wait for any further actions to complete
        time.sleep(2)

        # Optionally, switch back to the default content if you need to interact with the rest of the page
        driver.switch_to.default_content()
    except:
        time.sleep(2)
        return False
    return True

def purchase_product(product_url):
    print(product_url)
    # Navigate to the product page
    driver.get(product_url)
    time.sleep(5)  # Wait for the page to load
    is_item_available= False
    try:
        # Find the element that contains the "Item no longer available" message (adjust the XPath or CSS selector accordingly)
        # Example using XPath
        item_status_element = driver.find_element("xpath", "//div[contains(text(), 'Sorry, this item is no longer available!')]")

        # Check if the text exists in the element
        if "Sorry, this item is no longer available!" in item_status_element.text:
            print("Sorry, this item is no longer available!")
            return None
        else:
            print("Item is available.")
    except:
        is_item_available=True
        print("Item is available.")
    try:
        # Wait for the page to load (adjust sleep time if needed)
        time.sleep(5)

        # Locate the "Start order request" button using XPath or CSS selector
        # Using XPath (find button by data-type-btn attribute)
        start_order_button = driver.find_element("xpath", "//button[@data-type-btn='po']")

        # Click the "Start order request" button
        start_order_button.click()
        print("Successfully clicked the 'Start order request' button.")

    except NoSuchElementException:
        print("The 'Start order request' button was not found on the page.")
    except ElementClickInterceptedException:
        print("The 'Start order request' button is not clickable (possibly obscured by another element).")

    try:
        quality_div = driver.find_element("css selector", "div.quality")

        # Get the text content inside the div
        quality_text = quality_div.text
        quantities = list(quality_text.split(" "))
        quantity = quantities[0]

        # Print the extracted text
        print(f"Quality: {quantity}")
    except:
        print("Get min quantity failed")

    try:
        # Wait for the page to load (adjust time as necessary)
        time.sleep(5)

        # Locate the number picker input field
        number_picker_input = driver.find_element(By.CSS_SELECTOR, "input.number-picker-input")

        # Clear the current value in the input field
        number_picker_input.clear()

        # Enter the desired value (10 in this case)
        number_picker_input.send_keys(quantity)

        # Optionally, press ENTER to trigger any potential JavaScript events
        number_picker_input.send_keys(Keys.ENTER)

        print("Number picker updated to 10.")

    except Exception as e:
        print(f"Error: {e}")


    time.sleep(5)  # Wait for the product to be added to the cart

    try:
        # Wait for the page to load (adjust sleep time if needed)
        time.sleep(5)

        # Locate the "Start order request" button using XPath or CSS selector
        # Using XPath (find button by data-type-btn attribute)
        complete_order_button = driver.find_element("xpath", "//button[@data-type-btn='po' and text()='Complete order request']")

        # Click the "Start order request" button
        complete_order_button.click()
        print("Successfully clicked the 'Start order request' button.")

    except NoSuchElementException:
        print("The 'complete_order_button' button was not found on the page.")
    except ElementClickInterceptedException:
        print("The 'complete_order_button request' button is not clickable (possibly obscured by another element).")
    # Proceed to checkout
    #checkout_button = driver.find_element(By.CSS_SELECTOR, ".checkout-button")
    #checkout_button.click()

    # Complete the checkout process (this will vary based on the site's flow)
    time.sleep(5)  # Adjust this as needed based on loading times and processes

# Example credentials (replace with real credentials)
username = "anant.pukale@gmail.com"
password = "Anant@1234"

# Perform login and purchase process
is_log_in = alibaba_login(username, password)
# while(~ is_log_in):
#     time.sleep(5)
#     # Quit the driver when done
#     driver.quit()
#     time.sleep(5)
#     # Launch Chrome
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#
#     # Remove the WebDriver flag from the navigator
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     is_log_in = alibaba_login(username, password)

df = pd.read_csv("config.csv")
product_link_list = list(df['product_link'].values)
for product_link in product_link_list:
    purchase_product(product_link)

# Quit the driver when done
driver.quit()
