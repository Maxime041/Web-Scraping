import scrapy

from boursorama.items import ActionItem


class CacSpider(scrapy.Spider):
    name = "cac"
    start_urls = ["https://www.boursorama.com/bourse/actions/palmares/france/"]

    def parse(self, response):
        for row in response.css("table.c-table tbody tr"):
            cells = row.css("td.c-table__cell")
            if len(cells) < 5: continue
            lien = cells[0].css("a")
            href = lien.attrib.get("href","")
            # Extraire le code ISIN depuis l'URL (ex: /cours/1rXXXX/)
            isin = href.split("/")[-2] if href else ""
            try:
                cours     = float(cells[1].css("::text").get("0").replace(",",".").strip())
                variation = float(cells[2].css("::text").get("0").replace(",",".").replace("%","").strip())
                # Le tableau a 8 colonnes : le volume est en 7e position, pas en 4e.
                # La cellule 3 contient le cours d'ouverture.
                volume    = int(cells[6].css("::text").get("0").replace(" ","").replace(",","").strip() or 0)
            except (ValueError, TypeError):
                cours = variation = 0.0; volume = 0
            yield ActionItem(
                libelle=lien.css("::text").get("").strip(),
                cours=cours, variation=variation, volume=volume, isin=isin
            )
