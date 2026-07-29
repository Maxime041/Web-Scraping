import scrapy

from allocine.items import FilmItem


class FilmsSpider(scrapy.Spider):
    name = "films"
    start_urls = ["https://www.allocine.fr/film/meilleurs/"]
    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        # 1) Suivre chaque lien vers fiche detail
        for lien in response.css("h2.meta-title a::attr(href)").getall():
            yield response.follow(lien, callback=self.parse_film)

        # 2) Pagination -- il n'y a pas de lien "page suivante" identifiable,
        # les liens de pagination sont tous "?page=N". On lit le numero courant
        # dans l'URL. 10 films par page, on s'arrete a la page 5 = 50 films.
        page = int(response.url.split("page=")[-1]) if "page=" in response.url else 1
        if page < 5:
            yield response.follow(f"/film/meilleurs/?page={page + 1}",
                                  callback=self.parse)

    def parse_film(self, response):
        def safe(sel):
            v = response.css(sel).get()
            return v.strip() if v else ""

        def note(libelle):
            # L'ordre des blocs de notes change d'un film a l'autre : quand la
            # note presse manque, la note spectateurs prend sa place. On cible
            # donc le bloc par son libelle, en XPath.
            v = response.xpath(
                "//div[contains(@class,'rating-item')]"
                f"[.//span[contains(text(),'{libelle}')]]"
                "//span[@class='stareval-note']/text()"
            ).get()
            return v.strip() if v else ""

        yield FilmItem(
            titre       = safe(".titlebar-title::text"),
            annee       = safe(".meta-body-info .date::text")[-4:],
            realisateur = safe(".meta-body-direction .dark-grey-link::text"),
            note_presse = note("Presse"),
            note_spectateurs = note("Spectateurs"),
            url         = response.url,
        )
