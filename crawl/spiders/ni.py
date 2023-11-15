# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
import datetime
import re
from src.output import output
from pipelines.formatters import AZsPipeline, DatesPipeline, CourtsPipeline
from pipelines.texts import TextsPipeline
from src import config
from pipelines.exporters import ExportAsHtmlPipeline, FingerprintExportPipeline, RawExporter

class SpdrNI(scrapy.Spider):
    name = "spider_ni"
    base_url = "https://voris.wolterskluwer-online.de/jportal/portal/"
    custom_settings = {
        "DOWNLOAD_DELAY": 2, # minimum download delay
        "AUTOTHROTTLE_ENABLED": False,
        "ITEM_PIPELINES": {
            AZsPipeline: 100,
            DatesPipeline: 200,
            CourtsPipeline: 300,
            TextsPipeline: 400,
            ExportAsHtmlPipeline: 500,
            FingerprintExportPipeline: 600,
            RawExporter: 900
        }
    }

    def __init__(self, path, courts="", states="", fp=False, domains="", store_docId=False, postprocess=False, wait=False, **kwargs):
        self.path = path
        self.courts = courts
        self.states = states
        self.fp = fp
        self.domains = domains
        self.store_docId = store_docId
        self.postprocess = postprocess
        self.wait = wait
        self.base_url = "https://voris.wolterskluwer-online.de/jportal/portal/"
        super().__init__(**kwargs)

    def start_requests(self):
        start_urls = []
        """filter_url = self.base_url + "page/bsndprod.psml?nav=ger&node=BS-ND%5B%23%5D%4000"
        if self.courts:
            if "ag" in self.courts:
                start_urls.append(filter_url + "40%40Amtsgerichte%5B%23%5D")
            if "arbg" in self.courts:
                # Herausfiltern des lag
                arbgs = ["Braunschweig", "Celle", "Emden", "Göttingen", "Hannover", "Lingen", "Nienburg", "Oldenburg+%28Oldenburg%29", "Osnabrück", "Verden"]
                for arbg in arbgs:
                    start_urls.append(filter_url + f"70%40Arbeitsgerichte%5B%23%5D%400002%40ArbG+{arbg}%5B%24%5DArbG+{arbg}%7B.%7D%5B%23%5D")
            if "fg" in self.courts:
                start_urls.append(filter_url + "80%40Finanzgericht%7B.%7D%5B%23%5D")
            if "lag" in self.courts:
                n = "Landesarbeitsgericht+Niedersachsen"
                start_urls.append(filter_url + f"70%40Arbeitsgerichte%5B%23%5D%400001%40{n}%5B%24%5D{n}%7B.%7D%5B%23%5D")
            if "lg" in self.courts:
                start_urls.append(filter_url + "30%40Landgerichte%5B%23%5D")
            if "lsg" in self.courts:
                n = "Landessozialgericht+Niedersachsen-Bremen"
                start_urls.append(filter_url + f"60%40Sozialgerichte%5B%23%5D%400001%40{n}%5B%24%5D{n}%7B.%7D%5B%23%5D")
            if "olg" in self.courts:
                start_urls.append(filter_url + "20%40Oberlandesgerichte%5B%23%5D")
            if "ovg" in self.courts:
                n = "Niedersächsiches+Oberverwaltungsgericht"
                start_urls.append(filter_url + f"50%40Verwaltungsgerichte%5B%23%5D%400001%40{n}%5B%24%5D{n}%7B.%7D%5B%23%5D")
            if "sg" in self.courts:
                # Herausfiltern des lsg
                sgs = ["Aurich", "Braunschweig", "Hannover", "Hildesheim", "Lüneburg", "Oldenburg+%28Oldenburg%29", "Osnabrück", "Stade"]
                for sg in sgs:
                    start_urls.append(filter_url + f"60%40Sozialgerichte%5B%23%5D%400002%40SG+{sg}%5B%24%5DSG+{sg}%7B.%7D%5B%23%5D")
            if "vg" in self.courts:
                # Herausfiltern des ovg
                vgs = ["Braunschweig", "Göttingen", "Hannover", "Lüneburg", "Oldenburg+%28Oldenburg%29", "Osnabrück", "Stade"]
                for vg in vgs:
                    start_urls.append(filter_url + f"50%40Verwaltungsgerichte%5B%23%5D%400002%40Verwaltungsgericht+{vg}%5B%24%5DVerwaltungsgericht+{vg}%7B.%7D%5B%23%5D")
        else:
            start_urls.append(self.base_url + "page/bsndprod.psml/js_peid/FastSearch/media-type/html?form=bsIntFastSearch&sm=fs&query=")

        for url in start_urls:
            yield scrapy.Request(url=url, headers=config.ni_headers,   callback=self.parse)"""
        url = "https://voris.wolterskluwer-online.de/"
        date = str(datetime.date.today())
        self.headers = config.ni_headers
        self.cookies = config.ni_cookies
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = config.rp_body % (date, time)
        filter_urls = ['ATS_Rechtsprechung_Arbeitsgerichte_ArbG', 'ATS_Rechtsprechung_Arbeitsgerichte_LAG',
                       'ATS_Rechtsprechung_Finanzgerichte_FG', 'ATS_Rechtsprechung_Sozialgerichte_LSG',
                       'ATS_Rechtsprechung_Sozialgerichte_SG', 'ATS_Rechtsprechung_Strafgerichte_AG',
                       'ATS_Rechtsprechung_Strafgerichte_LG', 'ATS_Rechtsprechung_Strafgerichte_OLG',
                       'ATS_Rechtsprechung_Verfassungsgerichte_VerfG', 'ATS_Rechtsprechung_Verwaltungsgerichte_OVG_VGH',
                       'ATS_Rechtsprechung_Verwaltungsgerichte_VG', 'ATS_Rechtsprechung_Zivilgerichte_AG',
                       'ATS_Rechtsprechung_Zivilgerichte_AGH', 'ATS_Rechtsprechung_Zivilgerichte_LG',
                       'ATS_Rechtsprechung_Zivilgerichte_OLG']

        #for filter in filter_urls:
        print(url + 'search?query=&publicationtype=publicationform-ats-filter%21ATS_Rechtsprechung_Arbeitsgerichte_LAG_Niedersachsen')

        yield scrapy.Request(url='https://voris.wolterskluwer-online.de/browse/csh-da-filter%21WKDE-LTR-VORIS-DOCS-PHC-%7B00000000-0000-0000-0001-000000000000%7D#csh-da-filter!6c5b57fb-d0b6-49c9-b3e0-89e2a4e81639;csh-da-filter!ba8aab30-5735-4894-be1d-0b29a7e05527;csh-da-filter!572139ca-c71a-4a1f-9431-56fa524531f0;csh-da-filter!572139ca-c71a-4a1f-9431-56fa524531f0--WKDE_LTR_0000014930%235dad5597e5f23e0992d8b1889ef81b04;csh-da-filter!572139ca-c71a-4a1f-9431-56fa524531f0--WKDE_LTR_0000014930%2324fd6c607bf1303599c949ab7909dca1',
                     callback=self.parse)

    """def parse(self, response):
        print('current url',response.url)
        if response.xpath("//*[@id='block-voris-nds-content']/div/div/div[2]/div/ul//li"):
            #print('11')
            for item in response.xpath("//*[@id='block-voris-nds-content']/div/div/div[2]/div/ul//li"):
                #print(item)
                partial_xpath_0 = './/div/div/div[2]/div[1]/ol/'
                for position in ['li[7]', 'li[8]', 'li[6]']:
                    court = item.xpath(
                        partial_xpath_0 + position + '//span[1]//text()').extract()
                    if court:
                        break


                #court = item.xpath(".//div/div/div[2]/div[1]/ol/li[8]/span[1]//text()").extract()
                #print(court)
                links = item.xpath(".//div/div/div[2]/div[2]/h3/a//@href").extract()
                #print(links)

                for co, link in zip(court, links):
                    date = re.search("([0-9]{2}\.[0-9]{2}\.[0-9]{4})", co)[0]
                    # print(date)
                    #print(co)
                    az = co.split('-')[-1].strip()

                    #print(az)
                    parts = link.split('/')

                    # Get the last part after the last '/'
                    document_id = parts[-1]
                    # print(document_id)
                    if "," in co: co = co.split(",")[0]
                    # print(co)
                    yield {
                        "postprocess": self.postprocess,
                        "wait": self.wait,
                        "court": co,
                        "date": date,
                        "link": 'https://voris.wolterskluwer-online.de' + link,
                        "az": az,
                        "docId": document_id,

                    }

            partial_xpath = '//*[@id="block-voris-nds-content"]/div/div/div[3]/div/nav/ul/'

            # Iterate through possible positions to find the 'next page' link
            for position in ['li[5]', 'li[7]']:
                next_page_link = response.xpath(partial_xpath + position + '/a[contains(@title, "Zur nächsten Seite")]/@href').get()

                if next_page_link:
                    current_page_url = response.url
                    next_page_url = response.urljoin(next_page_link)

                    if next_page_url != current_page_url:
                        print('Following next page:', next_page_url)
                        yield response.follow(next_page_url, dont_filter=True, callback=self.parse)
                        break  # Exit loop if next page found
                    else:
                        print('Already on the last page. Parsing finished.')
                        break  # Exit loop if already on the last page
        else:
            print('Not ab;e to parse')"""


    def parse(self, response):
        print('current url',response.url)
        if response.xpath("//*[@id='csh-da-filter!WKDE-LTR-VORIS-DOCS-PHC-{00000000-0000-0000-0001-000000000000}']/li[2]/div[1]/div[2]/a"):
            print('11')
            for item in response.xpath("//*[@id='csh-da-filter!WKDE-LTR-VORIS-DOCS-PHC-{00000000-0000-0000-0001-000000000000}']/li[2]/div[2]/ul"):
                print(item)
                partial_xpath_0 = './/div/div/div[2]/div[1]/ol/'
                for position in ['li[7]', 'li[8]', 'li[6]']:
                    court = item.xpath(
                        partial_xpath_0 + position + '//span[1]//text()').extract()
                    if court:
                        break


                #court = item.xpath(".//div/div/div[2]/div[1]/ol/li[8]/span[1]//text()").extract()
                #print(court)
                links = item.xpath(".//div/div/div[2]/div[2]/h3/a//@href").extract()
                #print(links)

                for co, link in zip(court, links):
                    date = re.search("([0-9]{2}\.[0-9]{2}\.[0-9]{4})", co)[0]
                    # print(date)
                    #print(co)
                    az = co.split('-')[-1].strip()

                    #print(az)
                    parts = link.split('/')

                    # Get the last part after the last '/'
                    document_id = parts[-1]
                    # print(document_id)
                    if "," in co: co = co.split(",")[0]
                    # print(co)
                    yield {
                        "postprocess": self.postprocess,
                        "wait": self.wait,
                        "court": co,
                        "date": date,
                        "link": 'https://voris.wolterskluwer-online.de' + link,
                        "az": az,
                        "docId": document_id,

                    }

            partial_xpath = '//*[@id="block-voris-nds-content"]/div/div/div[3]/div/nav/ul/'

            # Iterate through possible positions to find the 'next page' link
            for position in ['li[5]', 'li[7]']:
                next_page_link = response.xpath(partial_xpath + position + '/a[contains(@title, "Zur nächsten Seite")]/@href').get()

                if next_page_link:
                    current_page_url = response.url
                    next_page_url = response.urljoin(next_page_link)

                    if next_page_url != current_page_url:
                        print('Following next page:', next_page_url)
                        yield response.follow(next_page_url, dont_filter=True, callback=self.parse)
                        break  # Exit loop if next page found
                    else:
                        print('Already on the last page. Parsing finished.')
                        break  # Exit loop if already on the last page
        else:
            print('Not ab;e to parse')




