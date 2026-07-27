import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)

articles = []
page = 1
MAX_ARTICLES = 200

while len(articles) < MAX_ARTICLES:
    url = f"https://www.blogdumoderateur.com/articles/page/{page}/" if page > 1 else "https://www.blogdumoderateur.com/"
    print(f"--- REQUÊTE GET --- Page {page}")

    try:
        requete = session.get(url, timeout=10)
        requete.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP sur la page {page} : {e}")
        break
    except requests.exceptions.Timeout:
        print(f"Timeout dépassé sur la page {page}")
        break

    soup = BeautifulSoup(requete.text, "html.parser")
    elements = soup.select("article")

    if not elements:
        print("Aucun article trouvé, fin de la pagination.")
        break

    for el in elements:
        if len(articles) >= MAX_ARTICLES:
            break

        titre_el = el.select_one(".entry-header a") or el.select_one("h2.post-title a") or el.select_one(".entry-title")

        if titre_el:
            titre = titre_el.text.strip()

            link_el = el.select_one(".entry-header a") or el.select_one("h2.post-title a") or el.find_parent("a") or el.select_one("a")
            url_article = link_el.get("href", "").strip() if link_el else ""

            date_el = el.select_one("time[datetime]")
            date = date_el.get("datetime", "").strip() if date_el else ""

            cat_el = el.select_one(".favtag") or el.select_one(".cat-links a")
            categorie = cat_el.text.strip() if cat_el else ""

            chapeau_el = el.select_one(".entry-excerpt") or el.select_one(".entry-summary") or el.select_one("p")
            chapeau = chapeau_el.text.strip() if chapeau_el else ""

            articles.append({
                "titre": titre,
                "url": url_article,
                "date": date,
                "categorie": categorie,
                "chapeau": chapeau
            })

            print(f"[{len(articles)}/{MAX_ARTICLES}] Article extrait : {titre}")

    page += 1
    time.sleep(1)

champs = ["titre", "url", "date", "categorie", "chapeau"]
lignes = [{ champs: article[champs] for champs in champs } for article in articles]

with open("articles.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print(f"\nTerminé ! {len(articles)} articles ont été exportés dans articles.csv.")