import logging

import scrapy
from scrapy.utils.log import configure_logging
from scrapy.spiders import CrawlSpider

from ..items import AvvoScrapyItem
from ..settings import STARS


URL = 'https://www.avvo.com'


configure_logging(install_root_handler=False)
logging.basicConfig(
    # filename='log/log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)


class AvvoSpider(CrawlSpider):
    name = 'avvospider'
    start_urls = [
        'https://www.avvo.com/search/lawyer_search.html?page='
    ]

    def parse(self, response):
        account_numbers = int(
            response.xpath('//div[@id="skip_to_content"]/following-sibling::div/@content').extract_first())
        pagination_page_numbers = divmod(account_numbers, 10)

        if pagination_page_numbers[1]:
            pagination_page_numbers = pagination_page_numbers[0] + 1
        else:
            pagination_page_numbers = pagination_page_numbers[0]

        for page_number in range(1, pagination_page_numbers + 1):
            logging.info(page_number)
            url = ''.join([self.start_urls[0], str(page_number)])
            yield scrapy.Request(url, callback=self.get_page_urls)

    def get_page_urls(self, response):
        page_urls = check_account_rating(response)
        # logging.info(page_urls)
        for page_url in page_urls:
            url = ''.join([URL, page_url])
            yield scrapy.Request(url, callback=self.parse_account_page)

    def parse_account_page(self, response):
        item = AvvoScrapyItem()
        item['url'] = response.url
        item['name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
        item['address'] = ''.join(response.xpath('//span[@itemprop="address"]/p/span/text()').extract())
        item['phone'] = response.xpath('//span[@itemprop="telephone"]/a/span/text()').extract_first()
        item['website'] = response.xpath('//p[@itemprop="url"]/@content').extract_first()
        item['rating'] = response.xpath('//span[@itemprop="ratingValue"]/@content').extract_first()
        yield item


def check_account_rating(response):
    page_urls = []
    account_xpath_list = response.xpath('//div[@itemscope="itemscope"]')
    for account in account_xpath_list:
        rating = account.xpath('div//span[@class="sr-only"]/text()').extract_first()
        try:
            if not rating.isalpha() and float(rating[:3]) <= STARS:
                page_urls.append(account.xpath('div//a/@href').extract_first())
        except AttributeError:
            continue
    return page_urls



