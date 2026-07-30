BOT_NAME = "veille"

SPIDER_MODULES = ["veille.spiders"]
NEWSPIDER_MODULE = "veille.spiders"

ADDONS = {}

ITEM_PIPELINES = {
    "veille.pipelines.CleanPipeline" : 100,
    "veille.pipelines.SQLitePipeline": 200,
}

FEEDS = {
    "mentions.csv": {"format": "csv", "encoding": "utf-8", "overwrite": True},
}
