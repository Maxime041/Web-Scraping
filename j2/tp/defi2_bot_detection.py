from selenium import webdriver
import time, os, base64

os.makedirs("screenshots", exist_ok=True)

# save_screenshot() ne capture que la partie visible a l'ecran, et la page fait
# pres de 8000 px de haut. On passe donc par captureBeyondViewport, qui capture
# la page entiere. Agrandir la fenetre ne marche pas : Chrome la ramene a la
# hauteur de l'ecran.

# Tester 1 : sans flag anti-detection
opts = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=opts)
driver.get("https://bot.sannysoft.com")
time.sleep(6)                        # laisser les tests s'executer
capture = driver.execute_cdp_cmd("Page.captureScreenshot",
                                 {"format": "png", "captureBeyondViewport": True})
open("screenshots/bot_normal.png", "wb").write(base64.b64decode(capture["data"]))
driver.quit()

# Tester 2 : avec flags anti-detection
opts2 = webdriver.ChromeOptions()
opts2.add_argument("--disable-blink-features=AutomationControlled")
opts2.add_experimental_option("excludeSwitches", ["enable-automation"])
driver2 = webdriver.Chrome(options=opts2)
driver2.get("https://bot.sannysoft.com")
time.sleep(6)
capture2 = driver2.execute_cdp_cmd("Page.captureScreenshot",
                                   {"format": "png", "captureBeyondViewport": True})
open("screenshots/bot_stealth.png", "wb").write(base64.b64decode(capture2["data"]))
driver2.quit()

# Tester 3 : les memes flags, mais en mode headless
opts3 = webdriver.ChromeOptions()
opts3.add_argument("--headless=new")
opts3.add_argument("--no-sandbox")
opts3.add_argument("--disable-dev-shm-usage")
opts3.add_argument("--disable-blink-features=AutomationControlled")
opts3.add_experimental_option("excludeSwitches", ["enable-automation"])
driver3 = webdriver.Chrome(options=opts3)
driver3.get("https://bot.sannysoft.com")
time.sleep(6)
capture3 = driver3.execute_cdp_cmd("Page.captureScreenshot",
                                   {"format": "png", "captureBeyondViewport": True})
open("screenshots/bot_headless.png", "wb").write(base64.b64decode(capture3["data"]))
driver3.quit()

print("3 captures enregistrees dans screenshots/")
