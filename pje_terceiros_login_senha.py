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


# Load PJE credentials from another .env file
load_dotenv('credenciais/credenciais_pje.env')
usuario_pje = os.getenv("USERNAMEPJE")
senha_pje = os.getenv("PASSWORDPJE")
print(f"PJE Username: {usuario_pje}")
print(f"PJE Password: xxxxxxxxxxxx")

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Store the last clipboard content
last_clipboard_content = ""

def find_or_open_tab(driver, base_url, data_url=None):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if (base_url in driver.current_url or (data_url and data_url in driver.current_url)):
            return handle
    # Switch to the last tab before opening a new one
    driver.switch_to.window(driver.window_handles[-1])
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

try:
    while True:
        try:
            # Monitor clipboard for specific data pattern
            pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
            paste = pyperclip.paste()

            # Check if the clipboard content is new and matches the pattern
            if paste != last_clipboard_content and pattern.match(paste):
                print(f"Processo identificado: {paste}")
                last_clipboard_content = paste  # Update the last clipboard content

                #########################PJE######################################

                # Extract the TRT number (15th and 16th characters)
                trt_number = paste[18:20]

                # Remove leading zero if present
                trt_number = trt_number.lstrip('0')

                # Construct the base URL dynamically
                base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"

                # Find or open the tab for base_url
                base_url_handle = find_or_open_tab(driver, base_url)
                driver.switch_to.window(base_url_handle)

                # Wait for the "modo-operacao" element to be present
                modo_operacao_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao")))

                # Fill the input id=username with credentials (USERNAMEPJE)
                driver.find_element(By.ID, "username").send_keys(usuario_pje)
                # Fill the input id=password with credentials (PASSWORDPJE)
                driver.find_element(By.ID, "password").send_keys(senha_pje)
                # Press the button id=btnEntrar
                driver.find_element(By.ID, "btnEntrar").click()

                final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"

                # Open the final URL in a new tab and close the base URL tab
                driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                driver.execute_script(f"window.open('{final_url}', '_blank');")
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])

                # Wait for the "painel-escolha-processo" element to be present
                painel_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "painel-escolha-processo"))
                )

                # Split the paste value into the respective fields
                paste_parts = paste.split('-')
                numeroTst = paste_parts[0]
                remaining_parts = paste_parts[1].split('.')
                digitoTst = remaining_parts[0]
                anoTst = remaining_parts[1]
                orgaoTst = remaining_parts[2]
                tribunalTst = remaining_parts[3]
                varaTst = remaining_parts[4]

                # Construct the iframe URL
                iframe_url = f"https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do?conscsjt=&numeroTst={numeroTst}&digitoTst={digitoTst}&anoTst={anoTst}&orgaoTst={orgaoTst}&tribunalTst={tribunalTst}&varaTst={varaTst}&consulta=Consultar"
                
                
                # Add the title and iframe to the end of the body element
                driver.execute_script("""
                    var titleDiv = document.createElement('div');
                    titleDiv.innerHTML = '<h2>Consulta no TST (sistema antigo)</h2>';
                    titleDiv.style.marginTop = '550px';
                    document.body.appendChild(titleDiv);

                    var iframe = document.createElement('iframe');
                    iframe.src = arguments[0];
                    iframe.width = '100%';
                    iframe.height = '800px';
                    iframe.style.border = '2px solid black';
                    iframe.style.marginTop = '20px';
                    document.body.appendChild(iframe);

                """, iframe_url)

        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
        finally:
            time.sleep(1)  # Wait before checking the clipboard again

except Exception as e:
    print(f"An error occurred: {e}")