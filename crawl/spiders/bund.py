# -*- coding: utf-8 -*-
import re
import scrapy
import os
from bs4 import BeautifulSoup
from pipelines.formatters import AZsPipeline, CourtsPipeline
from pipelines.exporters import ExportAsHtmlPipeline,ExportAsPdfPipeline, FingerprintExportPipeline, RawExporter
from pipelines.texts import TextsPipeline

class SpdrBund(scrapy.Spider):
    name = "spider_bund"
    #start_urls = ["https://www.gesetze-im-internet.de/Teilliste_1.html, https://www.gesetze-im-internet.de/Teilliste_2.html",
                  #"https://www.gesetze-im-internet.de/Teilliste_3.html", "https://www.gesetze-im-internet.de/Teilliste_4.html",
                  #"https://www.gesetze-im-internet.de/Teilliste_5.html", "https://www.gesetze-im-internet.de/Teilliste_6.html",
                  #"https://www.gesetze-im-internet.de/Teilliste_7.html", "https://www.gesetze-im-internet.de/Teilliste_8.html",
                  #"https://www.gesetze-im-internet.de/Teilliste_9.html"]
    custom_settings = {
        "ITEM_PIPELINES": { 
            AZsPipeline: 100,
            CourtsPipeline: 200,
            TextsPipeline: 400,
            ExportAsPdfPipeline: 400,
            FingerprintExportPipeline: 400,
            RawExporter: 900
        }
    }

    def __init__(self, path, courts="", states="", fp=False, domains="", store_docId=False, postprocess=False, **kwargs):
        self.path = path
        self.courts = courts
        self.states = states
        self.fp = fp
        self.domains = domains
        self.store_docId = store_docId
        self.postprocess = postprocess
        """if ("zivil" in domains and not any(court in courts for court in ["bgh", "bpatg", "bag"])):
            courts.extend(["bgh", "bpatg", "bag"])
        if ("oeff" in domains and not any(court in courts for court in ["bfh", "bsg", "bverfg", "bverwg"])):
            courts.extend(["bfh", "bsg", "bverfg", "bverwg"])
        if ("straf" in domains and not "bgh" in courts):
            courts.append("bgh")"""
        super().__init__(**kwargs)

    def start_requests(self):

        start_urls = [
            "https://www.gesetze-im-internet.de/Teilliste_A.html",
            "https://www.gesetze-im-internet.de/Teilliste_B.html",
            "https://www.gesetze-im-internet.de/Teilliste_C.html",
            "https://www.gesetze-im-internet.de/Teilliste_D.html",
            "https://www.gesetze-im-internet.de/Teilliste_E.html",
            "https://www.gesetze-im-internet.de/Teilliste_F.html",
            "https://www.gesetze-im-internet.de/Teilliste_G.html",
            "https://www.gesetze-im-internet.de/Teilliste_H.html",
            "https://www.gesetze-im-internet.de/Teilliste_I.html",
            "https://www.gesetze-im-internet.de/Teilliste_J.html",
            "https://www.gesetze-im-internet.de/Teilliste_K.html",
            "https://www.gesetze-im-internet.de/Teilliste_L.html",
            "https://www.gesetze-im-internet.de/Teilliste_M.html",
            "https://www.gesetze-im-internet.de/Teilliste_N.html",
            "https://www.gesetze-im-internet.de/Teilliste_O.html",
            "https://www.gesetze-im-internet.de/Teilliste_P.html",
            "https://www.gesetze-im-internet.de/Teilliste_Q.html",
            "https://www.gesetze-im-internet.de/Teilliste_R.html",
            "https://www.gesetze-im-internet.de/Teilliste_S.html",
            "https://www.gesetze-im-internet.de/Teilliste_T.html",
            "https://www.gesetze-im-internet.de/Teilliste_U.html",
            "https://www.gesetze-im-internet.de/Teilliste_V.html",
            "https://www.gesetze-im-internet.de/Teilliste_W.html",
            "https://www.gesetze-im-internet.de/Teilliste_X.html",
            "https://www.gesetze-im-internet.de/Teilliste_Y.html",
            "https://www.gesetze-im-internet.de/Teilliste_Z.html",
            "https://www.gesetze-im-internet.de/Teilliste_1.html",
            "https://www.gesetze-im-internet.de/Teilliste_2.html",
            "https://www.gesetze-im-internet.de/Teilliste_3.html",
            "https://www.gesetze-im-internet.de/Teilliste_4.html",
            "https://www.gesetze-im-internet.de/Teilliste_5.html",
            "https://www.gesetze-im-internet.de/Teilliste_6.html",
            "https://www.gesetze-im-internet.de/Teilliste_7.html",
            "https://www.gesetze-im-internet.de/Teilliste_8.html",
            "https://www.gesetze-im-internet.de/Teilliste_9.html"]
        for url in start_urls:
            yield scrapy.Request(url=url,
                             dont_filter=True, callback=self.parse)


    
    def parse(self, response):
        #print('hi')
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = soup.find_all('div', id='paddingLR12')[0].find_all('p')

        # Iterate through paragraphs and extract the URL of the second <a> tag
        for i, paragraph in enumerate(paragraphs, start=1):
            second_a_tag = paragraph.find_all('a')[1]

            # If the second <a> tag is found, print its 'href' attribute
            if second_a_tag:
                second_a_href = second_a_tag.get('href')
                #pdf_file_name = os.path.basename(second_a_href)
                #print(pdf_file_name)
                y = {
                    "court": None,
                    "link": 'https://www.gesetze-im-internet.de' + second_a_href,
                    "docId": os.path.basename(second_a_href),
                    "postprocess": self.postprocess
                }
                if self.courts:
                    for court in self.courts:
                        if y["court"][0:len(court)].lower() == court:
                            if court == "bgh" and self.domains:
                                for domain in self.domains:
                                    if domain in y["court"].lower(): yield y
                            else:
                                yield y
                else:
                    yield y
                #print(f"URL of the second <a> tag in paragraph {i}: {second_a_href}")
            else:
                print(f"Second <a> tag not found in paragraph {i}.")
        """for item in response.xpath("//item"):
            link = item.xpath("link/text()").get()
            y = {
                "court": item.xpath("gericht/text()").get(),
                "date": item.xpath("entsch-datum/text()").get(),
                "az": item.xpath("aktenzeichen/text()").get(),
                "link": link,
                "docId": re.fullmatch(r'.+/jb\-([0-9A-Z]+)\.zip', link)[1],
                "postprocess": self.postprocess
            }"""

