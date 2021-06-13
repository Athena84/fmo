from fmo.items import FmoItem
from scrapy import Spider, Request
import re

class fmoSpider(Spider):
    name = 'fmo_spider'
    allowed_urls = ['https://www.fmo.nl']
    start_urls = ['https://www.fmo.nl/worldmap']


    def parse(self, response):
        #Scrape number of pages
        num_pages = int(response.xpath('.//*[@id="pbuic-pager-1"]/li[7]/a/text()').extract_first())

        #Create all the urls
        base_url = 'https://www.fmo.nl/worldmap'
        list_page_urls = [base_url +'?page={page_num}'.format(page_num = i) for i in range(2, num_pages + 1)]
        list_page_urls.append(base_url) #Note: first page without number also has projects so must be scraped too

        #Create request for each url
        for url in list_page_urls:
            yield Request(url = url, callback = self.parse_projects_list_page)


    #Handles each request for a page with list of projects
    def parse_projects_list_page(self, response):

        #Scrape the projects table
        blocks = response.xpath('.//li[@class="ProjectList__item"]')

        #Loop through the list to scrape the data and make request to each underlying detail page
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
        #headers = response.xpath('.//*[@class="ProjectDetail__main"]/h3/text()').extract()
        #texts = response.xpath('.//*[@class="ProjectDetail__main"]/p/text()').extract()
        #description = dict(zip(headers, texts))

        #scrape detail descriptions and combine into a single string. The questions and headers differ and key information is typically spread over various answers
        texts = response.xpath('.//*[@class="ProjectDetail__main"]/p/text()').extract()
        sep = ""
        description = sep.join(texts).lower().strip()

        #Note: Other details listed on project detail page are sometimes in different order and hard to distinguish by path, better to scrape from list page

        #write into an item instance
        item = FmoItem()
        item['project_name'] = response.meta['project_name']
        item['amount'] = response.meta['amount']
        item['date'] = response.meta['date']
        item['country'] = response.meta['country']
        item['industry'] = response.meta['industry']
        item['description'] = description
        yield item
