from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pickle
from base64 import b64decode

from io import BytesIO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from threading import Thread, Barrier, Semaphore
import threading
import time


class API:
    def __init__(
        self,
        invisible=False,
        CookiesRoute="sessions",
        multitasks=100,
        dbConnection=None,
        service_=Service("chromedriver.exe")
    ):
        if False:
            service_=Service(ChromeDriverManager().install())
        self.CookiesRoute = CookiesRoute
        self.Threads = []
        self.MultiTasks = Semaphore(multitasks)
        self.dbConnection = dbConnection

        self.edge_options = Options()
       
        self.edge_options.binary_location = "chrome-win64/chrome.exe"
        self.service = service_
        
        if invisible:
            self.edge_options.add_argument("--headless")  # Ejecutar en modo headless
            self.edge_options.add_argument(
                "--disable-gpu"
            )  # Desactivar la aceleración por GPU (opcional)
            self.edge_options.add_argument(
                "--no-sandbox"
            )  # Desactivar sandbox (opcional)

    def SaveCookies(self, driver, user, password):
        try:
            with open(f"{self.CookiesRoute}/{user}.pkl", "wb") as file:
                pickle.dump(driver.get_cookies(), file)
        except Exception as e:
            print(f"Error al guardar cookies {user}: {e}")
        return driver

    def GotoLogin(self):
        driver = webdriver.Chrome(service=self.service, options=self.edge_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.get("https://facebook.com/")
        return driver

    def GetCookiesManual(self, user, password):
        driver = webdriver.Chrome(service=self.service, options=self.edge_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.get("https://facebook.com/")
        input("PRESIONE ENTER CUANDO SE HAYA LOGUEADO")
        self.SaveCookies(driver, user, password)
        print("Su cookie se ha guardado en la carpeta session")
        input()

    def GetCookiesAuto(self, user, password):
        driver = webdriver.Chrome(service=self.service, options=self.edge_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.get("https://facebook.com/")
        user_ = driver.find_element(By.XPATH, '//*[@id="email"]')

        user_.send_keys(user)

        password_ = driver.find_element(By.XPATH, '//*[@id="pass"]')
        password_.send_keys(password)

        confirm_button = driver.find_element(By.NAME, "login")
        confirm_button.click()
        if "two_step_verification/authentication/" in driver.current_url:
            imagen = driver.find_element(By.TAG_NAME, "img")
            # Obtener la imagen como una cadena de texto en formato Base64
            imagen_base64 = imagen.screenshot_as_base64
            # Decodificar la cadena de texto en formato Base64
            imagen_bytes = b64decode(imagen_base64)
            # Abrir la imagen como un archivo
            imagen = Image.open(BytesIO(imagen_bytes))
            # Guardar la imagen en un archivo
            imagen.save(f"{user}_captcha.png")
            captchaInput = driver.find_element(By.TAG_NAME, "input")

            captcha = input("resuelve la captcha")
            captchaInput.send_keys(captcha)
            continueButton = driver.find_element(
                By.XPATH, "//span[contains(text(), 'Continuar')]"
            )
            continueButton.click()
        if "login/web/?email=" in driver.current_url:
            inputPass = driver.find_element(By.XPATH, '//*[@id="pass"]')
            confirmButton = driver.find_element(By.XPATH, '//*[@id="loginbutton"]')
            inputPass.send_keys(password)
            confirmButton.click()
        if "auth_platform/" in driver.current_url:
            print("Alerta facebook pidiendo notificacion")

        driver.close()

    def Login(self, user, password):
        try:
            driver = webdriver.Chrome(service=self.service, options=self.edge_options)
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            driver.get("https://facebook.com/")
            with open(f"flaskr/sessions/{user}.pkl", "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:

                    driver.add_cookie(cookie)
            driver.refresh()

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.xzsf02u.x1rg5ohu",
                    )
                )
            )

            return driver

            # self.SaveCookies(driver,user, password)
        except Exception as e:
            print(f"Error al iniciar sesion {e} con {user}")
            driver.quit()

    def Publicar(self, driver, grupo, text):

        try:

            driver.get(grupo)
            elemento_ = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//img[@data-imgperflogname="profileCoverPhoto"]',
                    )
                )
            )
            elemento = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "div.xi81zsa.x1lkfr7t.xkjl1po.x1mzt3pk.xh8yej3.x13faqbe",
                    )
                )
            )
            elemento.click()

            # Escribir el mensaje
            input_ = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3",
                    )
                )
            )

            input_.send_keys(text)

            elemento_ = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@aria-label="Publicar"]',
                    )
                )
            )

            elemento_.click()

            # Esperar a que se complete la publicación
            driver.implicitly_wait(15)

            print(f"Publicación exitosa en: {grupo}")
            return "OK!"

        except Exception as e:
            print(f"Error durante la publicacion en el grupo{grupo} {e} ")
            return "fail!"

    def Compartir(self, driver, grupo, post):

        try:
            driver.get(grupo)
            elemento_ = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//img[@data-imgperflogname="profileCoverPhoto"]',
                    )
                )
            )

            GroupName = driver.title.split()
            GroupName = GroupName[1:-2]
            GroupName = " ".join(GroupName)
            driver.get(post)

            shareButton = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//div[@aria-label="Envía esto a tus amigos o publícalo en tu perfil." and @role="button"]',
                    )
                )
            )

            driver.execute_script("arguments[0].click();", shareButton)
            groupButton = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//span[text()="Grupo"]',
                    )
                )
            )
            groupButton.click()

            searhBar = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//input[@role="textbox" and @type="search" and @aria-label="Buscar grupos"]',
                    )
                )
            )
            searhBar.send_keys(GroupName)

            selectedOption = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//div[@data-visualcompletion="ignore-dynamic" and @role="listitem"]',
                    )
                )
            )

            selectedOption.click()
            publicButton = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//div[@role="button" and @aria-label="Publicar"]',
                    )
                )
            )
            publicButton.click()
            driver.implicitly_wait(15)
            return "OK!"
        except Exception as e:
            print(f"Error al compartir en el grupo {grupo} {e}")
            return "fail!"

    def shareSubprocess_(self, user, password, groups, post):
        self.MultiTasks.acquire()
        startTime = time.time()
        logs = "None"
        try:
            for post_ in post:
                try:
                    login_ = self.Login(user, password)

                    for gp in groups:
                        result = self.Compartir(login_, gp, post_)
                        logs += f"{post} {gp} {result}\n"
                except Exception as e:
                    print(f"Error en shareSubprocess {e}")
                    logs += f"{post_} fail!\n"
        except Exception as e:
            print(f"Error en shareSubprocess {e}")

        self.MultiTasks.release()
        endTime = time.time()
        totalTime = endTime - startTime
        logs += f"\n\nProceso terminado  en {totalTime} segundos"
        if not self.dbConnection:
            return
        try:
            self.dbConnection.execute(
                "UPDATE asociatedAccounts SET logs = ?," " WHERE accCookieName = ?",
                (logs, user),
            )
        except Exception as e:
            print(f"Error en logs save{e}")

    def ShareProcess(self, user, password, groups, post):

        task = Thread(
            name=user, target=self.shareSubprocess_, args=(user, password, groups, post)
        )
        task.start()
        # self.Threads.append(task)

    def publicationSubprocess_(self, user, password, groups, text):
        self.MultiTasks.acquire()
        startTime = time.time()
        logs = "None"
        try:
            login_ = self.Login(user, password)

            for gp in groups:
                result = self.Publicar(login_, gp, text)
                logs += f"{gp} {result}\n"
        except Exception as e:
            print(f"Error en publicationSubprocess {e}")
            logs += "fail!\n"
        self.MultiTasks.release()

        endTime = time.time()
        totalTime = endTime - startTime
        logs += f"\n\nProceso terminado  en {totalTime} segundos"
        if not self.dbConnection:
            return
        try:
            self.dbConnection.execute(
                "UPDATE asociatedAccounts SET logs = ?," " WHERE accCookieName = ?",
                (logs, user),
            )
        except Exception as e:
            print(f"Error en logs save{e}")

    def PublicationProcess(self, user, password, groups, text):
        task = Thread(
            name=user,
            target=self.publicationSubprocess_,
            args=(user, password, groups, text),
        )
        task.start()
        # self.Threads.append(task)

    def CheckThreadState(self,id):
        hilos_actuales = threading.enumerate()

        for hilo in hilos_actuales:
            if hilo.name == id:
                return True
        return False
api=API()
api.GetCookiesManual("59642893","asas")