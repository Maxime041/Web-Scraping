import scrapy

from nicepresse.items import ArticleItem


class ArticlesSpider(scrapy.Spider):
    name = "articles"
    start_urls = ["https://nicepresse.com/page/actu-regionale/"]

    def parse(self, response):
        # 1) Chaque carte : le titre est dans un h2 ou un h4 selon sa position,
        # mais il porte toujours la classe post-title.
        for carte in response.css("article .post-title a"):
            yield response.follow(carte.attrib["href"],
                                  callback=self.parse_article,
                                  cb_kwargs={"titre": carte.css("::text").get("")})

        # 2) Pagination : le bouton "En voir plus" est un vrai lien.
        # On s'arrete a la page 3, ca fait deja plus de 30 articles.
        page = int(response.url.rstrip("/").split("/")[-1]) if response.url.rstrip("/")[-1].isdigit() else 1
        if page < 3:
            suivant = response.css(".pagination-more a::attr(href)").get()
            if suivant:
                yield response.follow(suivant, callback=self.parse)

    def parse_article(self, response, titre):
        yield ArticleItem(
            titre=titre,
            url=response.url,
            date=response.css("time::attr(datetime)").get(),
        )
