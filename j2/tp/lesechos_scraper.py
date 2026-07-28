import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.lesechos.fr",
                 headers={"User-Agent":"IPSSI-scraper (+contact@ipssi.fr)"},
                 timeout=10)
try:
    soup = BeautifulSoup(r.text,"lxml")
except:
    soup = BeautifulSoup(r.text,"html.parser")
titres = soup.select("h2, h3")
print(f"{len(titres)} balises de titre trouvees")
# Si 0 => page chargee en JS => Selenium necessaire

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time

def make_driver(headless: bool = False):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=opts)

# Mesurer le temps
t0 = time.time()
driver = make_driver(headless=False)
driver.get("https://www.lesechos.fr")
WebDriverWait(driver,15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"article, div[type='article']"))
)
t_normal = time.time() - t0
print(f"Mode normal : {t_normal:.1f}s")

def extraire_articles(driver) -> list[dict]:
    articles = driver.find_elements(By.CSS_SELECTOR,
        "article, div[type='article']")
    resultats = []
    for art in articles:
        try:
            titre = art.find_element(By.CSS_SELECTOR, "h1, h2, h3").text.split("\n")[0].strip()
            if not titre: continue
            rubrique = ""
            try:
                rubrique = art.find_element(By.CSS_SELECTOR,
                    "[data-testid='hubpage-links'] a").text.strip()
            except: pass
            chapeau = ""
            try:
                chapeau = art.find_element(By.CSS_SELECTOR, "p").text.strip()[:300]
            except: pass
            heure = ""
            try:
                heure = art.find_element(By.CSS_SELECTOR,
                    "div[class*='sc-1h4katp-1'] span").text.strip()
            except: pass
            # Detecter le contenu premium (icone cadenas)
            premium = bool(art.find_elements(By.CSS_SELECTOR,
                "[data-testid='subscribe-badge']"))
            resultats.append({
                "titre": titre, "rubrique": rubrique,
                "chapeau": chapeau, "heure_publi": heure, "premium": premium,
            })
        except Exception as e:
            pass
    return resultats

arts = extraire_articles(driver)
driver.quit()

with open("lesechos.json","w",encoding="utf-8") as f:
    json.dump(arts, f, indent=2, ensure_ascii=False)
print(f"{len(arts)} articles exportes")

# Comparer les temps headless vs normal
t0 = time.time()
d2 = make_driver(headless=True)
d2.get("https://www.lesechos.fr")
WebDriverWait(d2,15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"article")))
t_headless = time.time() - t0
d2.quit()
print(f"Normal  : {t_normal:.1f}s")
print(f"Headless: {t_headless:.1f}s")
print(f"Gain    : {t_normal/t_headless:.1f}x plus rapide")
