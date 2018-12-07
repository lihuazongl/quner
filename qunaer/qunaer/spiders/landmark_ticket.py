# -*- coding: utf-8 -*-
from copy import deepcopy

import scrapy
from scrapy_redis.spiders import RedisSpider


class LandmarkTicketSpider(scrapy.Spider):
    name = 'landmark_ticket'
    allowed_domains = ['piao.qunar.com']
    # start_urls = ['http://piao.qunar.com']
    redis_key = 'qunaer:start_urls'

    def parse(self, response):
        """解析首页获取各省url"""
        # 获取省级a标签
        div_list = response.xpath("//div[@class='mp-city-list-province']")
        for div in div_list:
            item = {}
            # 省名称
            item['province'] = div.xpath('./a/text()').extract_first()
            # 获取各省url
            item['province_url'] = response.urljoin(div.xpath('./a/@href').extract_first())
            # print(item)
            yield scrapy.Request(item['province_url'], callback=self.city_url_parse, meta={'item': deepcopy(item)})

    def city_url_parse(self, response):
        """进入到门票详情页"""
        item = response.meta['item']
        # 进入到门票详情页
        # detail_html_url = response.urljoin(response.xpath("//div[@class='mp-section-caption']//a[contains(text(),'景点')]/@href").extract_first())
        item['detail_html_url'] = response.urljoin(response.xpath("//div[@class='mp-section-caption']//a[contains(text(),'景点')]/@href").extract_first())

        yield scrapy.Request(item['detail_html_url'], callback=self.detail_list_parse, meta={'item': item})

    def detail_list_parse(self, response):
        """解析景点列表页"""
        item = response.meta['item']

        # 门票div标签
        div_list = response.xpath('//*[@id="search-list"]/div/div/div')

        for div in div_list:
            # 景点详情url
            item['detail_url'] = response.urljoin(div.xpath('./h3/a/@href').extract_first())

            yield scrapy.Request(item['detail_url'], callback=self.detail_parse, meta={'item':deepcopy(item)})

        # 提取下一页
        # 判断 页码div中的 '下一页' 是否为空
        if response.xpath('//*[@id="pager-container"]/div/a[10]/text()'):
            # 当前页
            cur_page = response.xpath('//*[@id="pager-container"]/div/em/text()')
            next_page = int(cur_page) + 1
            next_url = item['detail_html_url'] + '&page=' + str(next_page)
            yield scrapy.Request(next_url, callback=self.detail_list_parse, meta={'item':deepcopy(item)})



    def detail_parse(self, response):
        item = response.meta['item']

        # 景区名
        item['scenic_name'] = response.xpath("/html/body/div[2]/div[2]/div[2]/div[1]/span[1]/text()").extract_first()
        # 价格
        item['price'] = str(response.xpath('/html/body/div[2]/div[2]/div[2]/div[7]/span/em/text()').extract_first()) + '起'
        # 地理位置
        item['location'] = response.xpath('/html/body/div[2]/div[2]/div[2]/div[3]/span[3]/text()').extract_first()
        yield item

