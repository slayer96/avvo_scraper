import scrapy
from scrapy.spiders import CrawlSpider

from ..items import AvvoScrapyItem

STARS = 4.0
URL = 'https://www.avvo.com'


class AvvoSpider(CrawlSpider):
    name = 'avvospider'
    start_urls = [
        'https://www.avvo.com/search/lawyer_search.html?page='
    ]

    def parse(self, response):
        account_numbers = int(response.xpath('//div[@id="skip_to_content"]/following-sibling::div/@content').extract_first())
        pagination_page_numbers = divmod(account_numbers, 10)
        if pagination_page_numbers[1]:
            pagination_page_numbers = pagination_page_numbers[0] + 1
        else:
            pagination_page_numbers = pagination_page_numbers[0]

        for page_number in range(1, pagination_page_numbers+1):
            url = ''.join([self.start_urls[0], str(page_number)])
            yield scrapy.Request(url, callback=self.get_page_urls)

    def get_page_urls(self, response):
        page_urls = response.xpath('//div/a[@itemprop="url"]/@href').extract()
        for page_url in page_urls:
            url = ''.join([URL, page_url])
            yield scrapy.Request(url, callback=self.parse_account_page)

    def parse_account_page(self, response):
        item = AvvoScrapyItem()
        account_rating = check_account_rating(response)
        if account_rating:
            item['url'] = response.url
            item['name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
            item['address'] = ''.join(response.xpath('//span[@itemprop="address"]/p/span/text()').extract())
            item['phone'] = response.xpath('//span[@itemprop="telephone"]/a/span/text()').extract_first()
            item['website'] = response.xpath('//p[@itemprop="url"]/@content').extract_first()
            yield item
        else:
            yield


def check_account_rating(response):
    rating_value = response.xpath('//span[@itemprop="ratingValue"]/@content').extract_first()
    if rating_value and float(rating_value) <= STARS:
        return True
    else:
        return False


