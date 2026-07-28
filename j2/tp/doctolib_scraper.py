from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, json, os

options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")  # decommenter pour headless
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=options)
wait   = WebDriverWait(driver, 15)

URL = "https://www.doctolib.fr/hematologue/nice"
driver.get(URL)

# Strategie 1 (RECOMMANDEE) : cliquer sur le bouton Accepter
try:
    btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@id="didomi-notice-agree-button" or contains(.,"Accepter") or contains(.,"Tout accepter")]')
    ))
    btn.click()
    print("Cookies acceptes")
except:
    # Capture screenshot pour debug
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot("screenshots/doctolib_erreur.png")
    print("Pas de banniere detectee")

# Strategie 2 : injecter le cookie directement (plus robuste)
# driver.add_cookie({"name": "cookie_consent", "value": "true", "domain": ".doctolib.fr"})
# Strategie 3 : profil Chrome persistant
# options.add_argument("--user-data-dir=/tmp/chrome_profile")

# Attendre que les cartes medecins soient visibles
try:
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.dl-card:has(h2)")
    ))
    print("Resultats charges")
except Exception as e:
    # Capture screenshot pour debug
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot("screenshots/doctolib_erreur.png")
    raise RuntimeError(f"Resultats non charges : {e}")

# Defiler pour charger les resultats hors viewport
def scroll_to_bottom(driver, pauses=3):
    last_h = driver.execute_script("return document.body.scrollHeight")
    for _ in range(pauses):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h

scroll_to_bottom(driver)

def extraire_medecins(driver) -> list[dict]:
    cartes = driver.find_elements(By.CSS_SELECTOR, "div.dl-card:has(h2)")
    resultats = []
    for carte in cartes[:10]:  # limiter a 10
        try:
            nom = carte.find_element(By.CSS_SELECTOR, "h2").text.split("\n")[0].strip()
            spec = carte.find_elements(By.CSS_SELECTOR, "div.flex.flex-col.w-full p")
            nom_specialite = f"{nom} - {spec[0].text.strip()}" if spec else nom
            adr = carte.find_element(
                By.CSS_SELECTOR, "div.flex.gap-8:has(> div > svg[aria-label='Adresse'])"
            ).text.strip().replace("\n", ", ")
            url_el = carte.find_element(By.CSS_SELECTOR, "a[href]")
            url = url_el.get_attribute("href")
            creneaux = [
                el.text.strip()
                for el in carte.find_elements(
                    By.CSS_SELECTOR, "div[data-test-id='availabilities-container'] button")
                if el.text.strip()
            ][:3]
            types = [
                el.text.strip()
                for el in carte.find_elements(By.XPATH, ".//*[contains(text(),'Consultation vid')]")
            ]
            resultats.append({
                "nom_specialite": nom_specialite, "adresse": adr,
                "type_consultation": types or ["Cabinet"],
                "prochains_creneaux": creneaux,
                "url_fiche": url,
            })
        except Exception as e:
            print(f"Carte ignoree : {e}")
    return resultats

medecins = extraire_medecins(driver)
driver.quit()

with open("doctolib.json","w",encoding="utf-8") as f:
    json.dump(medecins, f, indent=2, ensure_ascii=False)

print(f"{len(medecins)} medecins exportes dans doctolib.json")
