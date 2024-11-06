# Import necessary libraries
from selenium import webdriver  # to control the web browser
from selenium.webdriver.common.by import By  # to locate elements on the page
import time  # to add delays


# get tdp information for older Intel CPUs, before 2nd generation. For CPU that are 2nd or later, you can just use intel power gadget

def get_tdp(cpu_model):
    """
    Retrieves the TDP (Thermal Design Power) for a specified CPU model from Intel's ARK website.

    Args:
        cpu_model (str): The CPU model to search for (e.g., "i5-14500hx").

    Returns:
        str: The TDP value for the specified CPU model.
    """

    # Step 1: Initialize the WebDriver
    # Ensure you have the WebDriver installed and updated for your browser (e.g., ChromeDriver for Chrome).
    # Download the WebDriver from https://sites.google.com/chromium.org/driver/
    # Make sure the WebDriver executable is in your PATH or specify the executable's path like so:
    # driver = webdriver.Chrome(executable_path='/path/to/chromedriver')
    driver = webdriver.Chrome()  # or use webdriver.Firefox() for Firefox

    # Step 2: Open the Intel ARK website
    driver.get("https://ark.intel.com/content/www/us/en/ark.html")

    # Step 3: Locate the search box, input the CPU model, and submit the search
    search_box = driver.find_element(By.ID, "ark-searchbox")  # Locate the search box by its ID
    search_box.send_keys(cpu_model)  # Enter the CPU model (e.g., "i5-14500hx")
    search_box.submit()  # Submit the search form

    # Step 4: Wait for the page to load
    # You may need to adjust the sleep time depending on your connection speed.
    time.sleep(2)  # Basic wait; you can also use WebDriverWait for more control

    # Step 5: Try to locate the TDP element on the page
    try:
        tdp_element = driver.find_element(By.XPATH, "//span[@data-modal='tt-MaxTDP']")
        tdp_value = tdp_element.text.strip()  # Extract and clean up the TDP value text
    except Exception as e:
        tdp_value = "TDP not found"  # If TDP field not found, return an appropriate message

    # Step 6: Close the browser
    driver.quit()  # Close the WebDriver session

    # Return the retrieved TDP value
    return tdp_value


