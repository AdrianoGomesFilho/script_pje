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
import json
import tkinter as tk
from tkinter import simpledialog, messagebox

# Function to prompt user for credentials using a GUI and save them to a file
def prompt_for_credentials(file_path, credentials, driver=None):
    main_window = tk.Tk()
    main_window.title("Dados para login")
    main_window.attributes('-topmost', True)  # Make the window stay on top

    # Get the screen width and height
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # Calculate the position to center the window
    window_width = 300
    window_height = 210
    position_right = int(screen_width/2 - window_width/2)
    position_down = int(screen_height/2 - window_height/2)

    # Set the geometry of the window
    main_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    tk.Label(main_window, text="CPF para login no PJE:").grid(row=0, column=0, padx=10, pady=5)
    username_pje_entry = tk.Entry(main_window)
    username_pje_entry.grid(row=0, column=1, padx=10, pady=5)
    username_pje_entry.insert(0, credentials.get("USERNAMEPJE", ""))

    tk.Label(main_window, text="Senha para login no PJE:").grid(row=1, column=0, padx=10, pady=5)
    password_pje_entry = tk.Entry(main_window, show='*')
    password_pje_entry.grid(row=1, column=1, padx=10, pady=5)
    password_pje_entry.insert(0, credentials.get("PASSWORDPJE", ""))

    tk.Label(main_window, text="E-mail do Astrea:").grid(row=2, column=0, padx=10, pady=5)
    username_astrea_entry = tk.Entry(main_window)
    username_astrea_entry.grid(row=2, column=1, padx=10, pady=5)
    username_astrea_entry.insert(0, credentials.get("USERNAMEASTREA", ""))

    tk.Label(main_window, text="Senha do Astrea:").grid(row=3, column=0, padx=10, pady=5)
    password_astrea_entry = tk.Entry(main_window, show='*')
    password_astrea_entry.grid(row=3, column=1, padx=10, pady=5)
    password_astrea_entry.insert(0, credentials.get("PASSWORDASTREA", ""))

    def save_and_run(event=None):
        username_pje = username_pje_entry.get()
        password_pje = password_pje_entry.get()
        username_astrea = username_astrea_entry.get()
        password_astrea = password_astrea_entry.get()

        if not username_pje or not password_pje or not username_astrea or not password_astrea:
            messagebox.showerror("Error", "All fields are required!")
            return

        credentials = {
            "USERNAMEPJE": username_pje,
            "PASSWORDPJE": password_pje,
            "USERNAMEASTREA": username_astrea,
            "PASSWORDASTREA": password_astrea
        }

        with open(file_path, 'w') as cred_file:
            json.dump(credentials, cred_file)

        if driver:
            driver.quit()

        main_window.destroy()
        run_script(credentials)

    def edit_credentials():
        username_pje_entry.config(state=tk.NORMAL)
        password_pje_entry.config(state=tk.NORMAL)
        username_astrea_entry.config(state=tk.NORMAL)
        password_astrea_entry.config(state=tk.NORMAL)

    tk.Button(main_window, text="Save and Run", command=save_and_run).grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(main_window, text="Edit", command=edit_credentials).grid(row=5, column=0, columnspan=2, pady=10)
    main_window.bind('<Return>', save_and_run)

    main_window.mainloop()
    return credentials

# Load credentials from a file or prompt the user if the file doesn't exist
credentials_file = os.path.expanduser('~/credentials.json')
credentials = {}
if os.path.exists(credentials_file):
    with open(credentials_file, 'r') as cred_file:
        credentials = json.load(cred_file)
else:
    credentials = prompt_for_credentials(credentials_file, credentials)

# Allow the user to update credentials
def update_credentials(driver):
    global credentials
    credentials = prompt_for_credentials(credentials_file, credentials, driver)

# Function to run the main script
def run_script(credentials):
    global usuario_pje, senha_pje, usuario_astrea, senha_astrea
    usuario_pje = credentials["USERNAMEPJE"]
    senha_pje = credentials["PASSWORDPJE"]
    usuario_astrea = credentials["USERNAMEASTREA"]
    senha_astrea = credentials["PASSWORDASTREA"]

    print(f"CPF para login no PJE: {usuario_pje}")
    print(f"Senha para login no PJE: xxxxxxxxxxxx")
    print(f"E-mail do Astrea: {usuario_astrea}")
    print(f"Senha do Astrea: xxxxxxxxxxxx")

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

                    #########################ASTREA######################################

                    # Perform Astrea login and other actions
                    astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
                    driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                    driver.execute_script(f"window.open('{astrea_url}', '_blank');")
                    astrea_handle = driver.window_handles[-1]
                    driver.switch_to.window(astrea_handle)

                    logged_in = False

                    if not logged_in:
                        try:
                            # Check if the login element is present
                            login_element = WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located((By.NAME, "username"))
                            )

                            # Credentials
                            username_field = driver.find_element(By.NAME, "username")
                            password_field = driver.find_element(By.NAME, "password")

                            username_field.send_keys(usuario_astrea)
                            password_field.send_keys(senha_astrea)

                            # Submit the login form
                            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                            login_button.click()

                            # Check for login failure
                            try:
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "erro")))
                                messagebox.showerror("Error", "Login no Astrea falhou. Edite o login ou senha novamente!.")
                                update_credentials(driver)
                                return
                            except TimeoutException:
                                print("Login no Astrea realizado.")
                                logged_in = True
                        except:
                            print("Already logged in to Astrea or login page not detected.")
                    else:
                        print("Skipping login as already logged in.")

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

                    # Check for login failure
                    try:
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rich-messages")))
                        messagebox.showerror("Error", "Login no PJE falhou. Edite o login ou senha novamente!.")
                        update_credentials(driver)
                        return
                    except TimeoutException:
                        print("Logged in to PJE successfully.")

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
                update_credentials(driver)
            finally:
                time.sleep(1)  # Wait before checking the clipboard again

    except Exception as e:
        print(f"An error occurred: {e}")
        update_credentials(driver)

# Show the credentials window before running the script
prompt_for_credentials(credentials_file, credentials)