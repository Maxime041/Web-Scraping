import sys
from bs4 import BeautifulSoup
from main import get_page, sauver_csv

def parse_trashtalk(soup: BeautifulSoup) -> list[dict]:
    """Extrait les articles de TrashTalk."""
    articles = []
    seen = set()

    for card in soup.select("div"):
        link_el = card.select_one("a[href*='/20']")
        if not link_el:
            continue

        raw_url = link_el.get("href", "").strip()
        if raw_url in seen:
            continue

        titre = link_el.get_text(strip=True)
        if len(titre) < 10:
            continue
        seen.add(raw_url)

        url = f"https://trashtalk.co{raw_url}" if raw_url.startswith("/") else raw_url
        date = raw_url[1:11].replace("/", "-")

        cat_el = card.select_one("a[href*='/category/']")
        categorie = cat_el.get_text(strip=True) if cat_el else "NBA"

        chapeau_el = card.select_one("p")
        chapeau = chapeau_el.get_text(strip=True)[:300] if chapeau_el else ""

        articles.append({
            "titre": titre,
            "url": url,
            "date": date,
            "categorie": categorie,
            "chapeau": chapeau
        })

    return articles

def main():
    soup = get_page("https://trashtalk.co/category/news-nba/")
    arts = parse_trashtalk(soup)[:20]
    sauver_csv(arts, "trashtalk_articles.csv")
    print(f"TrashTalk : {len(arts)} articles extraits dans trashtalk_articles.csv")

if __name__ == "__main__":
    main()
