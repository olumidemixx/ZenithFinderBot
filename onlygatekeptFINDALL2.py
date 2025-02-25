from selenium import webdriver
import time

# Keep the browser window open for 10 seconds before closing it.

#from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager

#driver = webdriver.Chrome(ChromeDriverManager().install())
# Path to your ChromeDriver executable
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip
import random
import os
# Create a Service instance with ChromeDriverManager



#list_of_tokens = ['3zimMehCqwba1ZPwx6KWdqYWVDmTrQLNRkpPsBYapump','7EznqpQk1HXC9JQpaBgi1k9EHN8ooHLwsNgw78R4pump']
# Open a website
def zenithfinderbot(list_of_tokens):
    all_addresses=[]
    for token in list_of_tokens:
        options = webdriver.ChromeOptions()
        options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/chrome"
        #options.binary_location = os.getenv('CHROME_PATH')
        #options.binary_location = '/opt/render/project/.render/chromedriver/chromedriver-linux64/chromedriver'#"/usr/bin/google-chrome"
        #/opt/google/chrome/google-chrome #"/usr/bin/google-chrome-stable"
        options.add_argument("--headless=new")  # Use the new headless mode
        chromedriver_path = "/opt/render/project/.render/chromedriver/chromedriver-linux64/chromedriver"
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        #service = Service(ChromeDriverManager().install())

    # Initialize Chrome driver using the service instance
        #driver = webdriver.Chrome(service=service)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.get("https://gatekept.io/token/"+token)
        time.sleep(random.uniform(14, 21))

        wait = WebDriverWait(driver, 20)


        copy_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "copy-icon")))

        #print(f"Found {len(copy_buttons)} copy buttons")
        addresses = []

        # Click each button and get the clipboard content
        for i, button in enumerate(copy_buttons, 1):
                    try:
                        # Scroll the button into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(random.uniform(1,3))  # Small pause to let the page settle

                        # Click the button
                        button.click()
                        time.sleep(random.uniform(0.8,2.5))  # Wait for clipboard to be updated

                        # Get clipboard content
                        address = pyperclip.paste()
                        if address:
                            addresses.append(address)
                            #print(f"Copied address {i}: {address}")
                        
                        time.sleep(random.uniform(1,2.4))  # Small pause between clicks

                    except Exception as e:
                        print(f"Error processing button {i}: {e}")
                        continue
                    

        # Print the title of the page
        #print(driver.title)
        time.sleep(random.uniform(1,2))
        # Close the browser
        #driver.quit()



        #service = Service(ChromeDriverManager().install())

        # Initialize Chrome driver using the service instance
        #driver = webdriver.Chrome(service=service)


        # Open a website
        #driver.get("https://gatekept.io/token/3zimMehCqwba1ZPwx6KWdqYWVDmTrQLNRkpPsBYapump")
        #time.sleep(15)

        wait = WebDriverWait(driver, 40)
        insider_buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//img[@alt='Insider Wallets']")))

            
        for i, button in enumerate(insider_buttons, 1):
            try:
                    # Scroll the button into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(random.uniform(1, 3))  # Small pause to let the page settle
                    
                    # Click the button
                    button.click()
                    
                    time.sleep(1)  # Wait after click
                    
            except Exception as e:
                    print(f"Error clicking button-text element {i}: {e}")
                    continue

        copy_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "copy-icon")))
        for i, button in enumerate(copy_buttons, 1):
                    try:
                        # Scroll the button into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(random.uniform(1,3))  # Small pause to let the page settle

                        # Click the button
                        button.click()
                        time.sleep(random.uniform(0.8,2.5))  # Wait for clipboard to be updated

                        # Get clipboard content
                        address = pyperclip.paste()
                        if address:
                            addresses.append(address)
                            #print(f"Copied address {i}: {address}")
                        
                        time.sleep(random.uniform(1,2.4))  # Small pause between clicks

                    except Exception as e:
                        print(f"Error processing button {i}: {e}")
                        continue
        addresses = list(set(addresses))
        all_addresses.append(addresses)
        driver.quit()


    common_addresses = { "No Addresses Found": 0}

    from collections import Counter

    def count_elements(all_addresses):
        # Flatten the list of lists into a single list
        flat_list = [item for sublist in all_addresses for item in sublist]
        
        # Use Counter to count occurrences of each element
        return Counter(flat_list)

    # Example usage

    counts = count_elements(all_addresses)

    print("Element Counts:")
    for key, value in counts.items():
        if value > 1:
            common_addresses[key] = value
            return(common_addresses)
        return(common_addresses)
        


