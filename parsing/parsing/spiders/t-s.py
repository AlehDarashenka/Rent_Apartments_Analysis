import re
import scrapy

class TSSpider(scrapy.Spider):
    name = 't-s'
    start_urls = ['https://www.t-s.by/rent/flats/']

    def parse(self, response):

        for flat in response.css('li.apart_item'):
            details_page_url = flat.css('div.item_descr h4 a::attr(href)').extract_first()
            features = {
                "code": flat.css('td.code div.apart-item_body::text').extract_first(),
                "address": flat.css('td.address > div.apart-item_body > span::text').extract_first().strip(),
                "rooms": flat.css('td.rooms div.apart-item_body::text').extract_first(),
                "price": flat.css('div.usd_price::text').extract_first().strip(),
                "furniture": len(flat.css('i.furniture')),
                "washing": len(flat.css('i.washing')),
                "refrigerator": len(flat.css('i.refrigerator')),
                "tv": len(flat.css('i.tv')),
                "metro": flat.css('td.params span::text').extract_first(),
                "date": flat.css('td.date div.apart-item_body::text').extract_first(),
                "info1": flat.css('div.item_descr i::text').extract_first(),
                "info2": flat.css('div.item_descr p::text').extract()[2],
            }

            request = response.follow(details_page_url, callback=self.parse_details)
            request.meta['features'] = features

            yield request

        next_page = response.css('li.arr a.page-lnk::attr(href)').extract_first()
        if next_page is not None:
          yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        features = response.meta['features']

        params = {}
        params["price"] = response.css('div.about_price_ye::text').extract_first()
        params["views_week"] = response.css('div.views  span::text').extract_first()
        params["description"] = response.css('div.about_descr p::text').extract_first()

        for item in response.css('ul.about_params li.about_param'):
            key = item.css('div.param_name::text').extract_first()
            try:
                params[key] = item.css('div.param_descr::text').extract_first().strip()
            except AttributeError:
                params[key] = item.css('a::text').extract_first().strip()

        location_code = response.css('div.bx-yandex-view-map script::text').extract_first()
        params['latitude'] = re.findall(r'\d+\.\d+', location_code)[0]
        params['longitude'] = re.findall(r'\d+\.\d+', location_code)[1]

        features.update(params)
        yield features
