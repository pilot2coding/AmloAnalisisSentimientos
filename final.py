import pandas as pd
from scrapy.item import Item, Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
import re

#class Articulo(Item):
    #titulo = Field()
    #fecha = Field()
    #contenido = Field()
    #descripcion = Field()
class Articulo(Item):
    titulo = Field()
    fecha = Field()
    contenido = Field()
    descripcion = Field()
    participantes = Field()

    def clean_text(self, text):
        # Eliminar saltos de línea, retorno de carro y espacios en blanco adicionales
        cleaned_text = re.sub(r'[\n\r]+', ' ', text)
        cleaned_text = cleaned_text.strip()
        return cleaned_text

    def to_dict(self):
        return {
            'titulo': self['titulo'],
            'fecha': self['fecha'],
            'participantes': self['participantes'],
            'contenido': self.clean_text(self['contenido']),
            'descripcion': self.clean_text(self['descripcion'])
        }


class AmloScrapper(CrawlSpider):
    name = 'AMLOScraper'
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
        "CLOSESPIDER_PAGECOUNT": 950,
    }
    download_delay = 2

    start_urls = ['https://www.gob.mx/presidencia/es/archivo/articulos?filter_origin=archive&idiom=es&order=DESC&page=1']
    allowed_domains = ['gob.mx']

    rules = (
        # Paginacion
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="next" and @rel="next"]')), follow=True),
        # Detalle de los articulos
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@aria-label][@class][@rel]')), follow=True, callback="parse_articulo"),
    )

    def parse_articulo(self, response):
        #sel = Selector(response)
        #item = ItemLoader(Articulo(), sel)
        #item.add_xpath('titulo', '//h1[@class="bottom-buffer"]/text()')
        #item.add_xpath('descripcion', '//h2/text()')
        #item.add_xpath('fecha', '(//section/p/text())[1]')
        #item.add_xpath('contenido', '//div[@class="article-body"]/p/text()')
        #yield item.load_item()
        #articulo = item.load_item()
        #yield articulo.to_dict()

        sel = Selector(response)

        titulo = sel.xpath('//h1[@class="bottom-buffer"]/text()').get()
        descripcion = sel.xpath('//h2/text()').get()
        fecha = sel.xpath('//section/p/text()').get()
        participantes = sel.xpath('//div[@class="article-body"]/p/strong/text()').getall()
        # Extrae todos los párrafos dentro de "article-body"
        contenido_paragraphs = sel.xpath('//div[@class="article-body"]/p/text()').getall()
        #contenido_paragraphs = sel.xpath('//div[@class="article-body"]/p[strong[contains(text(), "PRESIDENTE ANDRÉS MANUEL LÓPEZ OBRADOR:")]]/text()').getall()

        # Combina todos los párrafos en un solo texto
        contenido = " ".join(contenido_paragraphs)

        # Crea el objeto Articulo y asigna los datos extraídos
        articulo = Articulo()
        articulo['titulo'] = titulo
        articulo['participantes'] = participantes
        articulo['descripcion'] = descripcion
        articulo['fecha'] = fecha
        articulo['contenido'] = contenido


        yield articulo.to_dict()


process = CrawlerProcess({'FEED_FORMAT': 'csv', 'FEED_URI': 'mananera_feelings.csv'})
process.crawl(AmloScrapper)
process.start()

#//strong/text() |
#//div[@class="article-body"]