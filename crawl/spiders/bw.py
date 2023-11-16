# -*- coding: utf-8 -*-
import datetime
import scrapy
from src.output import output
from pipelines.formatters import AZsPipeline, DatesPipeline, CourtsPipeline
from pipelines.texts import TextsPipeline
from pipelines.exporters import ExportAsHtmlPipeline, FingerprintExportPipeline, RawExporter
import json
from src import config
class SpdrBW(scrapy.Spider):
    name = "spider_bw"
    base_url = "https://lrbw.juris.de/cgi-bin/laender_rechtsprechung/"
    custom_settings = {
        "DOWNLOAD_DELAY": 1, # minimum download delay 
        "AUTOTHROTTLE_ENABLED": True,
        "ITEM_PIPELINES": { 
            AZsPipeline: 100,
            DatesPipeline: 200,
            CourtsPipeline: 300,
            TextsPipeline: 400,
            ExportAsHtmlPipeline: 500,
            FingerprintExportPipeline: 600,
            RawExporter : 900
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
        self.filter = []
        super().__init__(**kwargs)

    def start_requests(self):
        url = "https://www.landesrecht-bw.de/jportal/wsrest/recherche3/init"
        self.headers = config.bw_headers
        self.cookies = config.bw_cookies
        date = str(datetime.date.today())
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = config.st_body % (date, time)
        yield scrapy.Request(url=url, method="POST", headers=self.headers, body=body, cookies=self.cookies,
                             dont_filter=True, callback=self.parse)

    def parse(self, response):
        for result in self.extract_data(response):
            yield result
        url = "https://www.landesrecht-bw.de/jportal/wsrest/recherche3/search"
        self.headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
        date = str(datetime.date.today())
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = '{"searchTasks":{"RESULT_LIST":{"start":1,"size":25,"sort":"date","addToHistory":true,"addCategory":true},"RESULT_LIST_CACHE":{"start":25,"size":27},"FAST_ACCESS":{},"SEARCH_WORD_HITS":{}},"filters":{"CATEGORY":["Gesetze"]},"searches":[],"clientID":"bsst","clientVersion":"bsst - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (
        date, time)
        yield scrapy.Request(url=url, method="POST", headers=self.headers, body=body, cookies=self.cookies,
                             meta={"batch": 26}, dont_filter=True, callback=self.parse_nextpage)

    def parse_nextpage(self, response):
        results = json.loads(response.body)
        if "resultList" in results:
            for result in self.extract_data(response):
                yield result
            url = "https://www.landesrecht-bw.de/jportal/wsrest/recherche3/search"
            batch = response.meta["batch"]
            date = str(datetime.date.today())
            time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
            body = '{"searchTasks":{"RESULT_LIST":{"start":%s,"size":25,"sort":"date","addToHistory":true,"addCategory":true},"RESULT_LIST_CACHE":{"start":%s,"size":27},"FAST_ACCESS":{}},"filters":{"CATEGORY":["Gesetze"]},"searches":[],"clientID":"bsst","clientVersion":"bsst - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (
            batch, batch + 25, date, time)
            batch += 25
            yield scrapy.Request(url=url, method="POST", headers=self.headers, body=body, cookies=self.cookies,
                                 meta={"batch": batch}, dont_filter=True, callback=self.parse_nextpage)

    def extract_data(self, response):
        results = json.loads(response.body)
        if "resultList" in results:
            for result in results["resultList"]:
                r = {
                    "postprocess": self.postprocess,
                    "wait": self.wait,
                    "court": None,
                    "date": result["date"],
                    "link": "https://www.landesrecht.sachsen-anhalt.de/bsst/document/" + result["docId"],
                    "docId": result["docId"],
                    "xcsrft": self.headers["x-csrf-token"]
                }
                if self.filter:
                    for f in self.filter:
                        if r["court"][0:len(f)].lower() == f:
                            yield r
                else:
                    yield r

    """def start_requests(self):
        start_urls = []
        base_url = self.base_url + "list.py?Gericht=bw&Art=en"
        add_years = lambda url : [url + str(y) for y in reversed(range(2007, datetime.date.today().year + 1))] # Urteilsdatenbank BW startet mit dem Jahr 2007
        if self.courts:
            if "ag" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Amtsgerichte&Datum="))
            if "arbg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Arbeitsgerichte&Datum="))
            if "fg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Finanzgericht&Datum="))
            if "lag" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Arbeitsgerichte&Datum="))
            if "lg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Landgerichte&Datum="))
            if "lsg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Sozialgerichte&Datum="))
            if "olg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Oberlandesgerichte&Datum="))
            if "ovg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Verwaltungsgerichte&Datum="))
            if "sg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Sozialgerichte&Datum="))
            if "vg" in self.courts: start_urls.extend(add_years(base_url + "&GerichtAuswahl=Verwaltungsgerichte&Datum="))
        else:
            start_urls.extend(add_years(base_url + "&Datum="))
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not response.xpath("//p[@class='FehlerMeldung']"): #  Hinweis-Seite ohne Suchergebnisse, d.h. alle Seiten für das Jahr wurden durchgegangen
            for doc_link in response.xpath("//a[@class='doklink']"):
                if self.courts:
                    # Auswahl notwendig, da ArbG & LAG == Arbeitsgerichte, SG & LSG == Sozialgerichte, VG & VGH == Verwaltungserichte
                    # Nur wenn self.courts, um Geschwindigkeit (XPath...) bei ungefiltertem Durchgang nicht zu bremsen
                    doc_court = doc_link.xpath("../../td[@class='EGericht']/text()").get().split()[0].lower()
                    if not doc_court in self.courts:
                        continue
                    # Wenn Rechtsgebiet ausgewählt weitere Unterscheidung notwendig, da ag + lg + olg == Straf UND Zivil
                    # ggf. Filtern nach Aktenzeichen?
                    if "straf" in self.domains and not "zivil" in self.domains:
                        output("filter (-s bw -d straf) not yet implemented", "warn")
                        # Ausbauen ....
                    elif "zivil" in self.domains and not "straf" in self.domains:
                        output("filter (-s bw -d zivil) not yet implemented", "warn")
                        # Ausbauen ....            
                yield {
                    "postprocess": self.postprocess,
                    "wait": self.wait,
                    "court": doc_link.xpath("../../td[@class='EGericht']/text()").get(),
                    "date": doc_link.xpath("../../td[@class='EDatum']/text()").get(),
                    "az": doc_link.xpath("text()").get(),
                    "link": self.base_url + doc_link.xpath("@href").get() + "&Blank=1"
                }
        if response.xpath("//img[@title='nächste Seite']"):
            yield response.follow(response.xpath("//img[@title='nächste Seite']/../@href").get(), callback=self.parse)
"""