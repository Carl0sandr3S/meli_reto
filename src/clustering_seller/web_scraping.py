from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import Spider,CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

class MeliData(Item):
    url_  = Field()


class Meli(CrawlSpider):
    name = "links_celulares"
    custom_settings= {
    "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "CLOSESPIDER_PAGECOUNT" : 5
    
    }
    allowed_domains = ['mercadolibre.com.co']
    start_urls = ["https://listado.mercadolibre.com.co/celulares-y-smartphones?sb=all_mercadolibre#D[A:celulares%20y%20smartphones]"] 
    download_delay = 3
    rules = (
        Rule(LinkExtractor(allow = r'/_Desde_'), follow = True), #pagina
        Rule(LinkExtractor(allow = r'/p/MCO'), follow = True,callback="parse_meli"), #detalles
            )
    def parse_meli(self, response):
        sel = Selector(response)
        url_actual = response.url
        item = ItemLoader(MeliData(), sel)
        item.add_value('url_', url_actual)
        yield item.load_item()