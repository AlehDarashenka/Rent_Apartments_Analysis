import json
import re
import scrapy


class RealtSpider(scrapy.Spider):
    name = 'realt'
    start_urls = ['https://realt.by/rent/flat-for-long/?view=0&page={}#tabs'.format(i) for i in range(100)]


    def parse(self, response):

        for flat in response.css('div.bd-table-item'):
            details_page_url = flat.css('div.ad a::attr(href)').extract_first()
            features = {
                'code': details_page_url.split('/')[-2],   # code from url
                'kv': flat.css('div.kv span::text').extract_first(),
                'address': flat.css('div.ad a::text').extract_first(),
                'floor': flat.css('div.ee span::text').extract_first(),
                'area': flat.css('div.pl span::text').extract_first(),
                'photos': flat.css('div.bd-table-item-wrapper a.f11::text').extract_first(),
            }

            request = response.follow(details_page_url, callback=self.parse_details)
            request.meta['features'] = features
            yield request

    def parse_details(self, response):
        features = response.meta['features']

        params = {}
        params["description"] = self.get_description(response.css('div.text-12'))

        views = response.css('span.views-control span::text').extract_first()
        views = re.findall(r'\d+', views)
        params['views_day'] = views[0]
        params['views_week'] = views[2]

        params['price_local'] = response.css('span.b14')[0].css('span::text').extract_first().replace('&nbsp;', '')
        params['price_usa'] = response.css('span.b14')[1].css('span::attr(data-840)').extract_first().replace('&nbsp;', '')

        except_set = {'Телефоны',
                      'Контактное лицо',
                      'E-mail',
                      'Область',
                      'Адрес',
                      'Ориентировочная стоимость эквивалентна',
                      'Комнат всего/разд.',
                      'Площадь общая/жилая/кухня',
                      None}
        for item in response.css('tr.table-row'):
            key = item.css('td.table-row-left::text').extract_first()
            if key not in except_set:
                if key == 'Район города':
                    # Район
                    params[key] = item.css('td.table-row-right a::text')[0].extract()
                    # "подрайон" (Вокзал, Серебрянка)
                    params['zones'] = item.css('td.table-row-right a::text')[1].extract()
                elif key == 'Населенный пункт':
                    params[key] = item.css('td.table-row-right a strong::text').extract_first()
                elif key == 'Агентство':
                    params[key] = item.css('td.table-row-right a::text').extract_first()
                else:
                    params[key] = item.css('td.table-row-right::text').extract_first()

        # location
        position = response.css('div[id="map-center"]::attr(data-center)').extract_first()
        position = json.loads(position)
        params['longitude'] = position['position.']['x']
        params['latitude'] = position['position.']['y']

        features.update(params)
        yield features

    def get_description(self, code):
        s = ' '.join(code.css('span::text').extract())
        s += ' '.join(code.css('p::text').extract())
        return s
