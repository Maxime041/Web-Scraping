from urllib.parse import urljoin
import argparse
import csv
import sqlite3
import requests, time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

BASE_URL = "https://www.blogdumoderateur.com/articles/page/{n}/"
MAX = 200
CHAMPS = ["titre", "url", "date", "categorie", "chapeau"]

DDL = '''
CREATE TABLE IF NOT EXISTS articles (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 titre TEXT NOT NULL,
 url TEXT NOT NULL UNIQUE,
 date TEXT,
 categorie TEXT,
 chapeau TEXT,
 scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
)
'''

def get_page(url: str, tries: int = 3) -> BeautifulSoup:
    """Effectue une requête GET HTTP sécurisée avec retries, gestion des 429 et retourne l'objet BeautifulSoup."""
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"429 - attente {wait}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            try:
                return BeautifulSoup(r.text, "lxml")
            except Exception:
                return BeautifulSoup(r.text, "html.parser")
        except requests.Timeout:
            print(f"Timeout tentative {attempt+1}/{tries}")
            time.sleep(2 ** attempt)
        except requests.HTTPError as e:
            if e.response and e.response.status_code < 500:
                raise  # 4xx definitif
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Echec apres {tries} tentatives : {url}")

# Ancienne version imperative de parse_articles :
# def parse_articles(soup: BeautifulSoup) -> list[dict]:
#     articles = []
#     for card in soup.select("article.post"):
#         # Extraire le titre
#         titre_el = card.select_one(".entry-header a") or card.select_one("h2.post-title a") or card.select_one("h2") or card.select_one("h3") or card.select_one(".entry-title")
#         titre = titre_el.get_text(strip=True) if titre_el else ""
# 
#         # Extraire l'URL absolue
#         link_el = card.select_one(".entry-header a") or card.select_one("h2 a") or card.select_one("a")
#         raw_url = link_el.get("href", "").strip() if link_el else ""
#         if raw_url.startswith("/"):
#             url = f"https://www.blogdumoderateur.com{raw_url}"
#         else:
#             url = raw_url
# 
#         # Extraire l'attribut datetime
#         date_el = card.select_one("time[datetime]") or card.select_one("time")
#         raw_date = date_el.get("datetime", "").strip() if date_el and date_el.has_attr("datetime") else (date_el.get_text(strip=True) if date_el else "")
#         date = raw_date[:10]
# 
#         # Extraire la categorie
#         cat_el = card.select_one(".favtag") or card.select_one(".cat-links a") or card.select_one(".entry-category")
#         categorie = cat_el.get_text(strip=True) if cat_el else ""
# 
#         # Extraire le chapeau
#         chapeau_el = card.select_one(".entry-excerpt") or card.select_one(".entry-summary") or card.select_one(".post-excerpt")
#         chapeau = chapeau_el.get_text(strip=True) if chapeau_el else ""
# 
#         articles.append({
#             "titre": titre, "url": url, "date": date,
#             "categorie": categorie, "chapeau": chapeau
#         })
# 
#     return articles

# Version refactorisee avec list-comprehension
def parse_articles(soup: BeautifulSoup) -> list[dict]:
    """Extrait les champs de chaque article (titre, url, date, catégorie, chapeau) sous forme de liste de dictionnaires."""
    return [
        {
            "titre": (c.select_one(".entry-header a") or c.select_one("h2.post-title a") or c.select_one("a")).get_text(strip=True),
            "url": (c.select_one(".entry-header a") or c.select_one("h2.post-title a") or c.select_one("a")).get("href", ""),
            "date": (c.select_one("time[datetime]") or {}).get("datetime", "")[:10],
            "categorie": (c.select_one(".favtag") or c.select_one(".cat-links a")).get_text(strip=True) if (c.select_one(".favtag") or c.select_one(".cat-links a")) else "",
            "chapeau": (c.select_one(".entry-excerpt") or c.select_one(".entry-summary") or c.select_one(".post-excerpt")).get_text(strip=True)[:300] if (c.select_one(".entry-excerpt") or c.select_one(".entry-summary") or c.select_one(".post-excerpt")) else "",
        }
        for c in soup.select("article.post")
        if c.select_one(".entry-header a") or c.select_one("h2.post-title a") or c.select_one("a")
    ]

def scrape_all(max_articles=MAX) -> list[dict]:
    """Parcourt les pages du site pour récolter jusqu'à max_articles avec une pause de temporisation entre requêtes."""
    tous = []
    page = 1
    while len(tous) < max_articles:
        url = "https://www.blogdumoderateur.com/" if page == 1 else BASE_URL.format(n=page)
        soup = get_page(url)
        nouveaux = parse_articles(soup)
        if not nouveaux:
            print(f"Plus d'articles a la page {page}, arret.")
            break
        tous.extend(nouveaux)
        print(f"Page {page} => {len(nouveaux)} articles | total={len(tous)}")
        page += 1
        time.sleep(1.5)  # throttling : au moins 1 s entre requetes
    return tous[:max_articles]

def sauver_csv(articles: list[dict], chemin: str = "articles.csv") -> None:
    """Exporte les articles scrapés dans un fichier CSV encodé en UTF-8."""
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS, extrasaction="ignore")
        w.writeheader()
        w.writerows(articles)
    print(f"CSV : {len(articles)} lignes -> {chemin}")

def sauver_sqlite(articles: list[dict], chemin: str = "articles.db") -> None:
    """Sauvegarde les articles scrapés dans la base SQLite en évitant les doublons (UNIQUE sur l'URL)."""
    with sqlite3.connect(chemin) as cx:
        cx.execute(DDL)
        inserted = 0
        for a in articles:
            try:
                cx.execute(
                    "INSERT OR IGNORE INTO articles (titre,url,date,categorie,chapeau) "
                    "VALUES (:titre,:url,:date,:categorie,:chapeau)", a
                )
                inserted += cx.execute("SELECT changes()").fetchone()[0]
            except sqlite3.Error as e:
                print(f"Erreur SQLite : {e}")
        cx.commit()
    print(f"SQLite : {inserted} nouvelles lignes inserees dans {chemin}")

def main():
    """Fonction principale : gère les arguments CLI, lance le scraping et les sauvegardes CSV/SQLite."""
    p = argparse.ArgumentParser(description="Scraper Blog du Moderateur")
    p.add_argument("--max", type=int, default=200, help="Nb max d'articles")
    p.add_argument("--csv", default="articles.csv")
    p.add_argument("--db", default="articles.db")
    args = p.parse_args()
    print(f"Demarrage - cible : {args.max} articles")
    articles = scrape_all(args.max)
    sauver_csv(articles, args.csv)
    sauver_sqlite(articles, args.db)
    print(f"Termine : {len(articles)} articles")

if __name__ == "__main__":
    main()