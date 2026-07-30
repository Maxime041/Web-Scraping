from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time

UA_NORMAL = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")

XPATH_ACCEPTER = '//button[contains(., "ACCEPTER") or contains(., "Accepter")]'
BLOC = "[class*='quarter']"

BASE = "https://www.lachainemeteo.com/meteo-france"
VILLES = {
    "Paris": "ville-33/previsions-meteo-paris-aujourdhui",
    "Marseille": "ville-341/previsions-meteo-marseille-aujourdhui",
    "Lyon": "ville-55/previsions-meteo-lyon-aujourdhui",
    "Toulouse": "ville-302/previsions-meteo-toulouse-aujourdhui",
    "Nice": "ville-6590/previsions-meteo-nice-aujourdhui",
}


def make_driver(headless: bool = True):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(f"--user-agent={UA_NORMAL}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1400, 1200)
    return driver


def accepter_consentement(driver, limite=25):
    """Clique sur Accepter. La modale est dans une iframe qui n'est pas prete tout de suite."""
    fin = time.time() + limite
    while time.time() < fin:
        driver.switch_to.default_content()
        boutons = driver.find_elements(By.XPATH, XPATH_ACCEPTER)
        if boutons:
            boutons[0].click()
            return True
        for frame in driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                driver.switch_to.frame(frame)
                boutons = driver.find_elements(By.XPATH, XPATH_ACCEPTER)
                if boutons:
                    boutons[0].click()
                    driver.switch_to.default_content()
                    return True
            except Exception:
                pass
            driver.switch_to.default_content()
        time.sleep(1)
    return False


def texte(element, selecteur, defaut=""):
    """Retourne le texte du premier element trouve, ou une valeur par defaut."""
    trouves = element.find_elements(By.CSS_SELECTOR, selecteur)
    return trouves[0].text.strip() if trouves else defaut


def releve(driver, ville, chemin) -> dict:
    """Ouvre la page de la ville et en extrait les 5 champs."""
    driver.get(f"{BASE}/{chemin}")
    accepter_consentement(driver)

    # Tant que la modale est affichee le bloc existe mais son texte est vide,
    # donc on attend le degre plutot que la simple presence de l'element.
    wait = WebDriverWait(driver, 20)
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, BLOC), "°"))

    lignes = [l.strip() for l in driver.find_element(By.CSS_SELECTOR, BLOC).text.split("\n") if l.strip()]
    return {
        "ville": ville,
        "temperature": next((l for l in lignes if l.endswith("°")), ""),
        "min": texte(driver, ".tt-tempe-min"),
        "max": texte(driver, ".tt-tempe-max"),
        "conditions": next((l for l in lignes if l.endswith(".")), ""),
        "humidite": "",  # reservee aux abonnes, voir selecteurs.md
        "creneau": lignes[0] if lignes else "",
        "heure_mesure": texte(driver, "[class*='forecast']").split("\n")[-1],
    }


def main():
    driver = make_driver(headless=True)
    releves = []
    try:
        for ville, chemin in VILLES.items():
            r = releve(driver, ville, chemin)
            releves.append(r)
            print(f"{ville:<10} {r['temperature']:>5}  min {r['min']} / max {r['max']}  {r['conditions'][:28]}")
    finally:
        driver.quit()

    with open("meteo.json", "w", encoding="utf-8") as f:
        json.dump(releves, f, indent=2, ensure_ascii=False)
    print(f"\n{len(releves)} villes exportees dans meteo.json")


if __name__ == "__main__":
    main()
