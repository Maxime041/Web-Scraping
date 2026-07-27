# diff_scrapes.py
import csv

def charger_urls(chemin: str) -> set:
    with open(chemin, encoding="utf-8") as f:
        return {row["url"] for row in csv.DictReader(f)}

def diff_scrapes(csv_ancien: str, csv_nouveau: str) -> dict:
    anciens = charger_urls(csv_ancien)
    nouveaux = charger_urls(csv_nouveau)
    return {
        "nouveaux" : sorted(nouveaux - anciens),
        "disparus" : sorted(anciens - nouveaux),
        "inchanges" : len(anciens & nouveaux),
    }
 
if __name__ == "__main__":
    import sys
    csv_ancien = sys.argv[1] if len(sys.argv) > 1 else "articles.csv"
    csv_nouveau = sys.argv[2] if len(sys.argv) > 2 else "trashtalk_articles.csv"

    print(f"Comparaison de '{csv_ancien}' et '{csv_nouveau}' :")
    r = diff_scrapes(csv_ancien, csv_nouveau)
    print(f"Nouveaux  : {len(r['nouveaux'])}")
    print(f"Disparus  : {len(r['disparus'])}")
    print(f"Stables   : {r['inchanges']}")
