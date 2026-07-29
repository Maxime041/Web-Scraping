import scrapy


class ArticleItem(scrapy.Item):
    titre = scrapy.Field()
    url   = scrapy.Field()
    date  = scrapy.Field()
