import csv
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item, Field


class ProddataparsSpider(CrawlSpider):
    name = 'mm_parser'
    allowed_domains = ['mnogomebeli.com']
    start_urls = [
        'https://mnogomebeli.com/divany/', 'https://mnogomebeli.com/tumby/',
        'https://mnogomebeli.com/krovati/', 'https://mnogomebeli.com/pufy/',
        'https://mnogomebeli.com/matrasy/', 'https://mnogomebeli.com/komody/',
        'https://mnogomebeli.com/stenki/', 'https://mnogomebeli.com/stulya/',
        'https://mnogomebeli.com/shkafy/', 'https://mnogomebeli.com/stellagi/',
        'https://mnogomebeli.com/stoly/', 'https://mnogomebeli.com/kresla/',
        'https://mnogomebeli.com/kuhni/',
    ]

    rules = (
        Rule(LinkExtractor(allow=(
            '/divany/', '/krovati/', '/matrasy/', '/stenki/', '/shkafy/', '/stoly/',
            '/tumby/', '/pufy/', '/komody/', '/stulya/', '/stellagi/', '/kresla/', '/kuhni/',),
            deny=('personal', 'reviews', 'about', 'filter', '/action/',)),
            callback='parse', follow=True),)

    with open("../mnogomebeli_parse_out.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Название",
                "Ссылка товара",
                "Старая цена",
                "Цена",
                "Скидка",
                "Ссылки на картинки",
                "Ссылки Доп Фото",
                "Описание",
                "Характеристики",
                "Преимущества",
            )
        )

    def parse(self, response):

        data = []

        # название
        title = response.xpath('//h1[@class="item-header__title t-h1"]/text()').get()
        product_url = response.url

        # описание
        descriptions = str(response.xpath('((//div[@class="item-info__desc"])[1]//p)/text()').get())

        # название характеристики
        specifications_1 = response.xpath('(//div[@class="item-info__specs"]/ul)[1]/li/p[1]/text()').getall()
        specifications_1 = [x.strip() for x in specifications_1]
        # specification_1 = ['\n'.join(specifications_1)]

        # значение характеристики
        specifications_2 = response.xpath('(//div[@class="item-info__specs"]/ul)[1]/li/p[2]/text()').getall()
        specifications_2 = [x.strip() for x in specifications_2]

        # объединение названия и значения характеристик "Название: значение"
        specification = [': '.join(x) for x in zip(specifications_1, specifications_2)]
        specification = ', '.join(specification)

        # преимущества
        advantages = response.xpath('(//div[@class="item-info__lists"])[1]/ul/li/text()').getall()
        advantages = [x.strip() for x in advantages]
        advantage = ', '.join(advantages)

        # старая цена
        old_price = response.xpath('//p[@class="item-header__price product__price--old"]//span[1]/text()').get()

        # новая цена
        new_price = response.xpath('//p[@class="item-header__price"]//span[1]/text()').get()

        # размер скидки
        discount = response.xpath(
            '(//div[@class="item-header__prices"]//p[@class="item-header__price product__price--sale"]//span)/text()').get()

        # собираем ссылки картинок товара
        img_url = response.xpath('(//div[@class="swiper-wrapper"])[1]//div[@class="item-slider__img"]/a/@href').getall()
        img_url = ['https://mnogomebeli.com' + x for x in img_url]
        img_urls = ', '.join(img_url)

        # собираем ссылки фотографий чертежей
        drawing = response.xpath('//div[@class="item-info__col"]//img/@src').getall()
        drawing = ['https://mnogomebeli.com' + draw.split('?')[0] for draw in drawing]

        # собираем ссылки на доп фото
        other_photo = response.xpath('(//div[@class="swiper-wrapper"])[3]//img[@class="img__i"]/@src').getall()
        other_photo = ['https://mnogomebeli.com' + o_p.split('?')[0] for o_p in other_photo]

        # проверяем список на одинаковые ссылки
        for url_o_p in drawing:
            if url_o_p not in other_photo:
                # Объединяем ссылки чертежей и доп. фото в один список
                other_photo.append(url_o_p)

        other_photo = list(dict.fromkeys(other_photo))
        other_photos = ', '.join(other_photo)

        if title is not None:
            data.append(
                {
                    "title": title,
                    "product_url": product_url,
                    "old_price": old_price,
                    "new_price": new_price,
                    "discount": discount,
                    "img_urls": img_urls,
                    "other_photos": other_photos,
                    "descriptions": descriptions,
                    "specification": specification,
                    "advantage": advantage,
                }
            )

            with open("../mnogomebeli_parse_out.csv", "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        title,
                        product_url,
                        old_price,
                        new_price,
                        discount,
                        img_urls,
                        other_photos,
                        descriptions,
                        specification,
                        advantage,
                    )
                )

    # Общее время выполнения кода
    def close(self, reason):
        start_time = self.crawler.stats.get_value('start_time')
        finish_time = self.crawler.stats.get_value('finish_time')
        print('[*INFO*] Общее время выполнения: ', finish_time - start_time)

# scrapy crawl mm_parser -- запуск парсера
