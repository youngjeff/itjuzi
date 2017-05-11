# coding:utf-8

from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scrapy_redis.spiders import RedisCrawlSpider
from itjuzi_dis.items import CompanyItem


class ITjuziSpider(RedisCrawlSpider):
    name = 'itjuzi_dis'
    allowed_domains = ['itjuzi.com']
    # start_urls = ['http://www.itjuzi.com/company/157']
    redis_key = 'itjuziCrawler:start_urls'
    rules = [
        # 获取每一页的链接
        Rule(link_extractor=LinkExtractor(allow=('/company\?page=\d+'))),
        # 获取每一个公司的详情
        Rule(link_extractor=LinkExtractor(allow=('/company/\d+')), callback='parse_item')
    ]

    def parse_item(self, response):
        try:
            
            soup = BeautifulSoup(response.body, 'lxml')
            item = CompanyItem()
            cpy1 = soup.find('div', class_='infoheadrow-v2')
            item['info_id'] = response.url.split('/')[-1:][0]
            if cpy1:
                item['company_name'] = cpy1.find('div',class_='line-title').find('h1','seo-important-title').get_text().strip().replace('\t', '').replace('\n', '')
               
                temp = cpy1.find('div','picinfo').find_all('div','info-line')
                item['slogan'] = temp[0].get_text()
                scope_a = temp[1].find('span','scope c-gray-aset').find_all('a')
                item['scope'] = scope_a[0].get_text().strip() if len(scope_a) > 0 else ''
                item['sub_scope'] = scope_a[1].get_text().strip() if len(scope_a) > 1 else ''
                city_a = temp[1].find('span', 'loca c-gray-aset').find_all('a')
                city_a[0].get_text().strip() if len(city_a) > 0 else ''
                area = city_a[1].get_text().strip() if len(city_a) > 1 else ''
                item['home_page'] = cpy1.find('div', class_ = 'link-line').find('a',class_='weblink')['href']
              
                item['tags'] = cpy1.find('div',class_='tagset dbi c-gray-aset').get_text().strip().strip().replace('\n', ',')
                
            cpy2 = soup.find('div', class_='block-inc-info on-edit-hide')
            if cpy2:
                item['company_intro'] = cpy2.find(class_='des').get_text().strip()
                cpy2_content = cpy2.find(class_='des-more').contents
                item['company_full_name'] = cpy2_content[1].get_text().strip()[len('公司全称：'):] if cpy2_content[1] else ''
                item['found_time'] = cpy2_content[3].contents[1].get_text().strip()[len('成立时间：'):] if cpy2_content[3] else ''
                item['company_size'] = cpy2_content[3].contents[3].get_text().strip()[len('公司规模：'):] if cpy2_content[3] else ''
                item['company_status'] = cpy2_content[5].get_text().strip() if cpy2_content[5] else ''
    
            main = soup.find('div', class_='main')
    
            # 投资
            tz = main.find('table', 'list-round-v2')
            tz_list = []
            if tz:
                all_tr = tz.find_all('tr')
                for tr in all_tr:
                    tz_dict = {}
                    all_td = tr.find_all('td')
                    tz_dict['tz_time'] = all_td[0].span.get_text().strip()
                    tz_dict['tz_round'] = all_td[1].get_text().strip()
                    tz_dict['tz_finades'] = all_td[2].get_text().strip()
                    tz_dict['tz_capital'] = all_td[3].get_text().strip().replace('\n', ',')
                    tz_list.append(tz_dict)
                    item['tz_info'] = tz_list
    
            # 团队 team
            tm = main.find('ul', class_='list-prodcase limited-itemnum')
            tm_list = []
            if tm:
                for li in tm.find_all('li'):
                    tm_dict = {}
                    tm_dict['tm_m_name'] = li.find('span', class_='c').get_text().strip()
                    tm_dict['tm_m_title'] = li.find('span', class_='c-gray').get_text().strip()
                    tm_dict['tm_m_intro'] = li.find('p', class_='mart10 person-des').get_text().strip()
                    tm_list.append(tm_dict)
                    item['tm_info'] = tm_list
    
            pdt = main.find('ul', class_='list-prod limited-itemnum')
            pdt_list = []
            if pdt:
                for li in pdt.find_all('li'):
                    pdt_dict = {}
                    pdt_dict['pdt_name'] = li.find('h4').b.get_text().strip()
                    pdt_dict['pdt_type'] = li.find('span', class_='tag yellow').get_text().strip()
                    pdt_dict['pdt_intro'] = li.find(class_='on-edit-hide').p.get_text().strip()
                    pdt_list.append(pdt_dict)
                    item['pdt_info'] = pdt_list
    
            
            print item
            return item
        except Exception, e:
            print e.message        