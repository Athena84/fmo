# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FmoItem(scrapy.Item):
    project_name = scrapy.Field()
    amount = scrapy.Field()
    date = scrapy.Field()
    country = scrapy.Field()
    industry = scrapy.Field()
    description = scrapy.Field()
