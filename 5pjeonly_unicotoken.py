import time
import re
from threading import Thread
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv

# Specify the path to your external .env file like this load_dotenv('credenciais.env')
load_dotenv('credenciais.env')
print("Loaded .env file")

# Get credentials from environment variables
usuario = os.getenv("USERNAMEASTREA")
senha = os.getenv("PASSWORDASTREA")
print(f"Username: {usuario}")
print(f"Password: xxxxxxxxxxxx")

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
chrome_options.add_argument("--start-maximized")
# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Store the last clipboard content
last_clipboard_content = ""
def find_or_open_tab(driver, base_url):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if base_url in driver.current_url:
            return handle
    # If the tab is not found, open a new one
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

def monitor_clipboard():
    global last_clipboard_content
    try:
        while True:
            # Monitor clipboard for specific data pattern
            pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
            paste = pyperclip.paste()

            # Check if the clipboard content is new and matches the pattern
            if paste != last_clipboard_content and pattern.match(paste):
                print(f"Processo identificado: {paste}")
                
                # Update the last clipboard content
                last_clipboard_content = paste
                
                # Extract the TRT number (15th and 16th characters)
                trt_number = paste[18:20]
                
                # Remove leading zero if present
                trt_number = trt_number.lstrip('0')
                
                # Construct the base URL dynamically
                base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
                
                # # Find or open the tab for base_url
                base_url_handle = find_or_open_tab(driver, base_url)
                driver.switch_to.window(base_url_handle)

                # Wait for the "modo-operacao" element to be present
                modo_operacao_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao")))
                modo_operacao_element.click()

                try:
                    # Find all elements that match the partial ID
                    buttons = driver.find_elements(By.XPATH, "//*[contains(@id, 'UtilizarPjeOffice')]")

                    if not buttons:
                        raise TimeoutException("No elements with ID containing 'UtilizarPjeOffice' found.")

                    # Scroll to the element and make sure it's in view
                    button_id = buttons[0].get_attribute('id')
                    button_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, button_id)))
                    driver.execute_script("arguments[0].scrollIntoView(true);", button_element)

                    # Wait for the element to be clickable
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id))).click()

                except TimeoutException as e:
                    print(f"TimeoutException: {e}")

                # Wait for the "loginAplicacaoButton" button to be clickable and click it
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()

                ###### PJE TOKEN UNICO ##############################################
            
                meu_painel_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Meu Painel")))
                meu_painel_button.click()

                input_numero_processo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputNumeroProcesso")))

                input_numero_processo.clear()  # Clear any pre-existing text
                input_numero_processo.send_keys(paste)

                try:
                    detalhes_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[mattooltip='Detalhes do Processo']")))

                    if detalhes_button:
                        detalhes_button.click()
                        new_title = paste.replace("'", "\\'")
                        driver.execute_script(f"document.title = '{new_title}';")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                except TimeoutException:
                    # Element not found within the wait time, so execute the else block
                    # Construct the final URL with the specific data pattern appended
                    final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"

                    # Open the final URL in a new tab
                    driver.execute_script(f"window.open('{final_url}', '_blank');")

                    # Close the base_url tab
                    driver.close()

                    # Switch back to the original tab
                    driver.switch_to.window(driver.window_handles[0])

            time.sleep(1)  # Wait before checking the clipboard again

    except Exception as e:
        print(f"An error occurred: {e}")

# Start the clipboard monitoring in a separate thread
clipboard_thread = Thread(target=monitor_clipboard)
clipboard_thread.start()