BOT_NAME = "nicepresse"

SPIDER_MODULES = ["nicepresse.spiders"]
NEWSPIDER_MODULE = "nicepresse.spiders"

ADDONS = {}

USER_AGENT = "IPSSI-scraper (+contact@ipssi.fr)"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 429]

ITEM_PIPELINES = {
    "nicepresse.pipelines.CleanPipeline": 100,
}

FEEDS = {
    "articles.csv": {"format": "csv", "encoding": "utf-8", "overwrite": True},
}
