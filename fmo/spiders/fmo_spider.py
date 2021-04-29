from fmo.items import FmoItem
from scrapy import Spider, Request
import re

class BudgetSpider(Spider):
    name = 'fmo_spider'
    allowed_urls = ['https://www.fmo.nl']
    start_urls = ['https://www.fmo.nl/worldmap']


    def parse(self, response):
        num_pages = int(response.xpath('.//*[@id="pbuic-pager-1"]/li[7]/a/text()').extract_first())
        base_url = 'https://www.fmo.nl/worldmap'
        list_page_urls = [base_url +'?page={page_num}'.format(page_num = i) for i in range(2, num_pages + 1)]
        list_page_urls.append(base_url)
        for url in list_page_urls:
            yield Request(url = url, callback = self.parse_projects_list_page)


    def parse_projects_list_page(self, response):

        #Scrape table with all projects
        blocks = response.xpath('.//li[@class="ProjectList__item"]')
        for block in blocks:

            #Scrape stats of projects on list page and store as dictionary to later yield complete item once the details page has been scraped as well
            project_dict = {}
            project_dict['project_name'] = block.xpath('.//h3/text()').extract_first()
            project_dict['amount'] = block.xpath('.//span[@class="fmo-financing"]/text()').extract_first()

            date_text = block.xpath('.//span/span[2]/text()').extract_first()
            project_dict['date'] = re.search(r':\s(.+)', date_text).group(1)

            country_text = block.xpath('.//span/span[3]/text()').extract_first()
            project_dict['country'] = re.search(r':\s(.+)', country_text).group(1)

            industry_text = block.xpath('.//span/span[4]/text()').extract_first()
            project_dict['industry'] = re.search(r':\s(.+)', industry_text).group(1)

            #scrape url of details page and pass the details to that method for yielding a complete item within that method
            project_details_url = block.xpath('.//a[@class="ProjectList__projectLink"]/@href').extract_first()
            yield Request(url = project_details_url, callback = self.parse_project_details_page, meta = project_dict)


    def parse_project_details_page(self, response):

        #scrape detail description and combine into a dictionary with headers as keys
        headers = response.xpath('.//*[@class="ProjectDetail__main"]/h3/text()').extract()
        texts = response.xpath('.//*[@class="ProjectDetail__main"]/p/text()').extract()
        description = dict(zip(headers, texts))

        #scrape category
        #Other details listed here are sometimes in different order and hard to distinguish by path, better to scrape from list page
        category = response.xpath('.//div[@class="ProjectDetail__asideInner"]/dl/dd[-1]/text()').extract_first()

        #write into an item instance
        item = FmoItem()
        item['project_name'] = response.meta['project_name']
        item['amount'] = response.meta['amount']
        item['date'] = response.meta['date']
        item['country'] = response.meta['country']
        item['industry'] = response.meta['industry']
        item['description'] = description
        item['category'] = category
        yield item
