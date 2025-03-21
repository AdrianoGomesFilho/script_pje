import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup


# Function to prompt user for credentials using a GUI and save them to a file
def prompt_for_credentials(file_path, credentials, driver=None):
    main_window = tk.Tk()
    main_window.title("PJE Automático")
    main_window.attributes('-topmost', True)
    main_window.configure(bg="#e8f5e9")  # Light green background

    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    window_width = 500
    window_height = 300
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    main_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 10)

    tk.Label(main_window, text="E-mail do Astrea:", bg="#e8f5e9", fg="#1b5e20", font=font_style).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    username_astrea_entry = tk.Entry(main_window, width=40, font=font_style)
    username_astrea_entry.grid(row=0, column=1, padx=10, pady=5)
    username_astrea_entry.insert(0, credentials.get("USERNAMEASTREA", ""))

    tk.Label(main_window, text="Senha do Astrea:", bg="#e8f5e9", fg="#1b5e20", font=font_style).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    password_astrea_entry = tk.Entry(main_window, show='*', width=40, font=font_style)
    password_astrea_entry.grid(row=1, column=1, padx=10, pady=5)
    password_astrea_entry.insert(0, credentials.get("PASSWORDASTREA", ""))

    tk.Label(main_window, text="CPF para login no PJE:", bg="#e8f5e9", fg="#1b5e20", font=font_style).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    username_pje_entry = tk.Entry(main_window, width=40, font=font_style)
    username_pje_entry.grid(row=2, column=1, padx=10, pady=5)
    username_pje_entry.insert(0, credentials.get("USERNAMEPJE", ""))

    tk.Label(main_window, text="Senha para login no PJE:", bg="#e8f5e9", fg="#1b5e20", font=font_style).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    password_pje_entry = tk.Entry(main_window, show='*', width=40, font=font_style)
    password_pje_entry.grid(row=3, column=1, padx=10, pady=5)
    password_pje_entry.insert(0, credentials.get("PASSWORDPJE", ""))

    tk.Label(main_window, text="Método de Login:", bg="#e8f5e9", fg="#1b5e20", font=font_style).grid(row=4, column=0, padx=10, pady=5, sticky="e")

    login_method = tk.StringVar(value="Astrea + PJE (Senha)")
    methods = ["Astrea + PJE (Senha)", "Astrea + PJE (Token)", "Somente Astrea", "Somente PJE"]
    for i, method in enumerate(methods):
        tk.Radiobutton(main_window, text=method, variable=login_method, value=method, bg="#e8f5e9", fg="#1b5e20", font=font_style).grid(row=4 + i, column=1, sticky="w")

    def save_and_run():
        username_pje = re.sub(r'\D', '', username_pje_entry.get())
        password_pje = password_pje_entry.get()
        username_astrea = username_astrea_entry.get()
        password_astrea = password_astrea_entry.get()
        selected_login_method = login_method.get()

        credentials = {
            "USERNAMEPJE": username_pje,
            "PASSWORDPJE": password_pje,
            "USERNAMEASTREA": username_astrea,
            "PASSWORDASTREA": password_astrea,
            "LOGIN_METHOD": selected_login_method
        }

        with open(file_path, 'w') as cred_file:
            json.dump(credentials, cred_file)

        if driver:
            driver.quit()

        main_window.destroy()
        run_script(credentials)

    tk.Button(main_window, text="Iniciar", command=save_and_run, bg="#4CAF50", fg="white", width=15, font=font_style).grid(row=8, column=0, columnspan=2, pady=10)

    main_window.mainloop()
    return credentials

def prompt_for_pje_level(paste):
    pje_level_window = tk.Tk()
    pje_level_window.title("Escolha o Grau")
    pje_level_window.attributes('-topmost', True)
    pje_level_window.configure(bg="#e3f2fd")  # Light blue background

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 400
    window_height = 300
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)

    tk.Label(pje_level_window, text="Escolha o grau", bg="#e3f2fd", fg="#0d47a1", font=font_style).pack(pady=10)
    tk.Label(pje_level_window, text=f"Processo que será aberto: {paste}", bg="#e3f2fd", fg="#0d47a1", font=font_style).pack(pady=10)

    pje_level = tk.StringVar()

    def select_level(level):
        pje_level.set(level)
        pje_level_window.destroy()

    tk.Button(pje_level_window, text="Primeiro Grau", command=lambda: select_level("Primeiro grau"), bg="#4CAF50", fg="white", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Segundo Grau", command=lambda: select_level("Segundo grau"), bg="#2196F3", fg="white", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="TST", command=lambda: select_level("TST"), bg="#FF5722", fg="white", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Ignorar e Aguardar", command=lambda: select_level("Ignore"), bg="#9E9E9E", fg="white", width=20, font=font_style).pack(pady=5)

    pje_level_window.mainloop()
    return pje_level.get()

def prompt_for_pje_level_with_buttons(driver, paste, trt_number):
    # Open the URL to fetch process details
    detail_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"
    driver.execute_script(f"window.open('{detail_url}', '_blank');")
    detail_handle = driver.window_handles[-1]
    driver.switch_to.window(detail_handle)

    try:
        # Wait for the buttons to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "selecao-processo"))
        )
        buttons = driver.find_elements(By.CLASS_NAME, "selecao-processo")
        button_labels = [button.text for button in buttons]
    except TimeoutException:
        button_labels = []

    # Create a prompt window with the buttons
    pje_level_window = tk.Tk()
    pje_level_window.title("Escolha o Grau")
    pje_level_window.attributes('-topmost', True)
    pje_level_window.configure(bg="#e3f2fd")  # Light blue background

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 400
    window_height = 300
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)

    tk.Label(pje_level_window, text="Escolha o grau", bg="#e3f2fd", fg="#0d47a1", font=font_style).pack(pady=10)
    tk.Label(pje_level_window, text=f"Processo que será aberto: {paste}", bg="#e3f2fd", fg="#0d47a1", font=font_style).pack(pady=10)

    pje_level = tk.StringVar()

    def select_level(level):
        pje_level.set(level)
        pje_level_window.destroy()

    for label in button_labels:
        tk.Button(pje_level_window, text=label, command=lambda l=label: select_level(l), bg="#4CAF50", fg="white", width=20, font=font_style).pack(pady=5)

    tk.Button(pje_level_window, text="Ignorar e Aguardar", command=lambda: select_level("Ignore"), bg="#9E9E9E", fg="white", width=20, font=font_style).pack(pady=5)

    pje_level_window.mainloop()
    return pje_level.get()

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
    global usuario_pje, senha_pje, usuario_astrea, senha_astrea, login_method, pje_level
    usuario_pje = credentials["USERNAMEPJE"]
    senha_pje = credentials["PASSWORDPJE"]
    usuario_astrea = credentials["USERNAMEASTREA"]
    senha_astrea = credentials["PASSWORDASTREA"]
    login_method = credentials["LOGIN_METHOD"]

    print(f"CPF para login no PJE: {usuario_pje}")
    print(f"Senha para login no PJE: xxxxxxxxxxxx")
    print(f"E-mail do Astrea: {usuario_astrea}")
    print(f"Senha do Astrea: xxxxxxxxxxxx")
    print(f"Método de Login: {login_method}")

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


    def fetch_process_id(driver, id_url):
        driver.execute_script(f"window.open('{id_url}', '_blank');")
        id_url_handle = driver.window_handles[-1]
        driver.switch_to.window(id_url_handle)
        try:
            # Wait for the page to load and fetch the process ID from the HTML
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            process_id_element = soup.find('pre')
            if not process_id_element:
                raise ValueError("Process ID not found")
            process_id = json.loads(process_id_element.text.strip())[0]['id']
            return process_id
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

    try:
        while True:
            # Monitor clipboard for specific data pattern
            pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
            paste = pyperclip.paste()

            # Check if the clipboard content is new, matches the pattern, and is not ignored
            if paste != last_clipboard_content and pattern.match(paste):
                print(f"Processo identificado: {paste}")
                last_clipboard_content = paste  # Update the last clipboard content

                #########################ASTREA######################################

                if login_method in ["Astrea + PJE (Senha)", "Astrea", "Astrea + PJE (Token)"]:
                    # Perform Astrea login and other actions
                    astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
                    driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                    driver.execute_script(f"window.open('{astrea_url}', '_blank');")
                    astrea_handle = driver.window_handles[-1]
                    driver.switch_to.window(astrea_handle)

                    try:
                        # Wait for either the 'search' element or the 'submit' button to appear
                        element_present = WebDriverWait(driver, 25).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Digite seu email']")),
                                EC.presence_of_element_located((By.ID, "search"))
                            )
                        )

                        if element_present.get_attribute("id") == "search":
                            print("Element with ID 'search' is present. Proceeding to open PJE.")
                            # Proceed to open PJE
                            # ...existing code to open PJE...
                        else:
                            print("Login form is present. Performing login.")
                            # Credentials
                            username_field = driver.find_element(By.NAME, "username")
                            password_field = driver.find_element(By.NAME, "password")

                            username_field.send_keys(usuario_astrea)
                            password_field.send_keys(senha_astrea)

                            # Submit the login form
                            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                            login_button.click()
                            print("Login realizado. Proceeding to open PJE.")
                            # Proceed to open PJE after login
                            # ...existing code to open PJE...
                    except TimeoutException:
                        print("Neither 'search' element nor 'submit' button found. Unable to proceed.")
                else:
                    print("Já logado Astrea ou ignorando login Astrea (método).")
                    
                while True:  # Loop to allow the user to choose another PJE level if needed
                    # Extract the TRT number (15th and 16th characters)
                    trt_number = paste[18:20]
                    trt_number = trt_number.lstrip('0')

                    # Prompt user to choose the PJE level with buttons
                    pje_level = prompt_for_pje_level_with_buttons(driver, paste, trt_number)

                    if pje_level == "Ignore":
                        print("Opção ignorada. Aguardando novo conteúdo na área de transferência.")
                        break  # Exit the inner loop and wait for new clipboard content

                    # Map the selected level to the corresponding URLs
                    if "1° Grau" in pje_level:
                        base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
                        id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                    elif "2° Grau" in pje_level:
                        base_url = f"https://pje.trt{trt_number}.jus.br/segundograu/login.seam"
                        id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                    elif "TST" in pje_level:
                        paste_parts = paste.split('-')
                        numeroTst = paste_parts[0]
                        remaining_parts = paste_parts[1].split('.')
                        digitoTst = remaining_parts[0]
                        anoTst = remaining_parts[1]
                        orgaoTst = remaining_parts[2]
                        tribunalTst = remaining_parts[3]
                        varaTst = remaining_parts[4]

                        antigo_tst_url = f"https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do?conscsjt=&numeroTst={numeroTst}&digitoTst={digitoTst}&anoTst={anoTst}&orgaoTst={orgaoTst}&tribunalTst={tribunalTst}&varaTst={varaTst}&consulta=Consultar"

                        base_url = "https://pje.tst.jus.br/tst/login.seam"
                        id_url = f"https://pje.tst.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                    
                    if pje_level == "TST":
                        driver.execute_script(f"window.open('{antigo_tst_url}', '_blank');")
                        base_url_handle = find_or_open_tab(driver, base_url)
                        driver.switch_to.window(base_url_handle)
                    else:
                        base_url_handle = find_or_open_tab(driver, base_url)
                        driver.switch_to.window(base_url_handle)

                    botao_pdpj = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSsoPdpj")))
                    botao_pdpj.click()

                    try:
                        # Custom function to wait for either of two elements to be present
                        def wait_for_any_element(driver, locators, timeout=10):
                            for _ in range(timeout * 10):  # Check every 0.1 seconds
                                for locator in locators:
                                    try:
                                        element = driver.find_element(*locator)
                                        if element.is_displayed():
                                            return element
                                    except:
                                        continue
                                time.sleep(0.1)
                            raise TimeoutException("Neither element was found within the timeout period.")

                        # Wait for either "botao-certificado-titulo" or "brasao-republica" to be present
                        elemento_login = wait_for_any_element(driver, [
                            (By.ID, "kc-login"),
                            (By.ID, "brasao-republica"),
                            (By.ID, "formPesquisa")
                        ])

                        if elemento_login.get_attribute("ID") == "kc-login":
                            if login_method in ["Astrea + PJE (Token)", "PJE (token)"]:
                                driver.find_element(By.NAME, "login-pje-office").click()
                                elemento_login = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "brasao-republica")) or
                                    EC.presence_of_element_located((By.ID, "formPesquisa"))
                                )
                                process_id = fetch_process_id(driver, id_url)
                            else:
                                driver.find_element(By.ID, "username").send_keys(usuario_pje)
                                driver.find_element(By.ID, "password").send_keys(senha_pje)
                                driver.find_element(By.ID, "kc-login").click()
                                elemento_login = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "brasao-republica")) or
                                    EC.presence_of_element_located((By.ID, "formPesquisa"))
                                )
                                process_id = fetch_process_id(driver, id_url)
                        elif elemento_login.get_attribute("id") in ["brasao-republica", "formPesquisa"]:
                            process_id = fetch_process_id(driver, id_url)
                    except (ValueError, TimeoutException):
                        messagebox.showinfo("Aviso", "Processo sem cadastro neste PJE. Se desejar abrir outro grau clique OK!")
                        driver.close()  # Close the current base_url tab
                        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last remaining tab
                        continue  # Prompt the user to choose another PJE level
                    else:
                        break  # Exit the loop if process_id is successfully fetched

                # Debugging and normalization for pje_level
                print(f"Debug: pje_level value before normalization: '{pje_level}'")
                pje_level = pje_level.strip().upper()  # Normalize by stripping spaces and converting to uppercase

                if "TST" in pje_level:  # Check if "TST" is a substring
                    final_url = f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
                else:
                    final_url = f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"

                print(f"final_url: {final_url}")  # Print final_url

                # Close the id_url tab
                driver.close()

                # Switch to the last tab before opening the final_url
                driver.switch_to.window(driver.window_handles[-1])

                # Ensure the final_url tab is opened without replacing the last PJE tab
                final_url_handle = find_or_open_tab(driver, final_url)
                driver.switch_to.window(final_url_handle)               

            time.sleep(1)  # Wait before checking the clipboard again

    except Exception as e:
        print(f"An error occurred in the main loop: {e}")
        update_credentials(driver)

# Show the credentials window before running the script
prompt_for_credentials(credentials_file, credentials)