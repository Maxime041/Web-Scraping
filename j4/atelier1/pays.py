import csv
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

URL_PAYS = "https://fr.wikipedia.org/wiki/Liste_des_pays_du_monde"
URL_ISO = "https://fr.wikipedia.org/wiki/ISO_3166-1"

CHAMPS = ["nom_officiel", "capitale", "continent", "code_iso", "url_fiche"]


def get_page(url: str, tries: int = 3) -> BeautifulSoup:
    """Effectue une requête GET avec retries, gestion des 429, et retourne le BeautifulSoup."""
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"429 - attente {wait}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")
        except requests.Timeout:
            print(f"Timeout tentative {attempt+1}/{tries}")
            time.sleep(2 ** attempt)
        except requests.HTTPError as e:
            if e.response and e.response.status_code < 500:
                raise  # 4xx definitif
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Echec apres {tries} tentatives : {url}")


def lien_article(cellule):
    """Renvoie le premier lien vers un article, en ignorant les liens d'images."""
    for a in cellule.select("a[href*='/wiki/']"):
        if "Fichier:" not in a["href"]:
            return a
    return None


def parse_pays(soup) -> list[dict]:
    """Extrait le nom officiel et le lien de fiche des tableaux de la page."""
    pays = []
    for table in soup.select("table.wikitable"):
        for tr in table.select("tbody tr"):
            cellules = tr.find_all(["td", "th"])
            if len(cellules) != 3:
                continue
            court = lien_article(cellules[1])
            officiel = cellules[2].select_one("a")
            if not court or not officiel:
                continue
            pays.append({
                "nom_officiel": officiel.get_text(strip=True),
                "capitale": "",   # absente de la page
                "continent": "",  # absent de la page
                "code_iso": "",   # rempli par la page ISO 3166-1
                "url_fiche": court["href"],
            })
    return pays


def parse_iso(soup) -> dict:
    """Renvoie un dictionnaire {url de la fiche pays : code alpha-2}."""
    codes = {}
    for tr in soup.select("table.wikitable")[0].select("tbody tr"):
        cellules = tr.find_all(["td", "th"])
        if len(cellules) < 7:
            continue
        lien = lien_article(cellules[4])
        if lien:
            codes[lien["href"]] = cellules[2].get_text(strip=True)
    return codes


def sauver_csv(pays: list[dict], chemin: str = "pays.csv") -> None:
    """Exporte les pays dans un fichier CSV encodé en UTF-8."""
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS)
        w.writeheader()
        w.writerows(pays)
    print(f"CSV : {len(pays)} lignes -> {chemin}")


def main():
    """Scrape les deux pages, croise les codes ISO sur l'url de fiche, exporte le CSV."""
    pays = parse_pays(get_page(URL_PAYS))
    print(f"{len(pays)} pays trouves")

    time.sleep(1.5)  # throttling entre les deux requetes
    codes = parse_iso(get_page(URL_ISO))
    print(f"{len(codes)} codes ISO trouves")

    for p in pays:
        p["code_iso"] = codes.get(p["url_fiche"], "")

    trouves = sum(1 for p in pays if p["code_iso"])
    print(f"Croisement : {trouves}/{len(pays)} pays avec un code ISO")
    sauver_csv(pays)


if __name__ == "__main__":
    main()
