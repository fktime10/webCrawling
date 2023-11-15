# -*- coding: utf-8 -*-
from . import config
from .output import output
from lxml import etree, html
import datetime
from urllib.parse import quote

import requests
import time as timelib
import requests
from bs4 import BeautifulSoup

def bb(item):
    if not "tree" in item:
        try:
            txt = requests.get(item["link"]).text
            if (item["wait"] == True): timelib.sleep(1.5)
        except:
            output("could not retrieve " + item["link"], "err")
        else:
            try:
                item["tree"] = html.fromstring(txt)
            except:
                output("could not parse " + item["link"], "err")
    if not item["tree"].xpath("//h1[@id='header']/text()")[0].rstrip().strip() == "Entscheidung": # Herausfiltern von leeren Seiten
        # Dokument Aufräumen (nur bestimmte Bereiche übernehmen)...
        body_meta = html.tostring(item["tree"].xpath("//div[@id='metadata']")[0]).decode("utf-8")
        body_content = html.tostring(item["tree"].xpath("//div[@id='metadata']/following::div[1]")[0]).decode("utf-8")
        doc = "<html><head><title>%s</title></head><body>%s%s</body></html>" % (item["az"], body_meta, body_content)
        item["text"] = doc
        item["filetype"] = "html"
        return item
    else:
        output("could not retrieve " + item["link"], "err")


def be(item, headers, cookies):
    url = "https://gesetze.berlin.de/jportal/wsrest/recherche3/document"

    #item["docId"] = quote(item["docId"], safe=':/')
    #headers["Referer"] = f"https://gesetze.berlin.de/bsbe/document/{quote(item['docId'], safe=':/')}/part/X"

    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    doc_parts = ["S","X"]
    result_items = []
    encoded_docId = quote(item["docId"], safe=':/')

    headers["x-csrf-token"] = item["xcsrft"]
    headers["Cookie"] = 'r3autologin="bsbe"'

    for doc_part in doc_parts:
        # print('In--------------', doc_part)
        headers[
            "Referer"] = "https://gesetze.berlin.de/bsbe/document/" + encoded_docId + "/part/" + doc_part
        item["link"] = headers["Referer"]

        body = {"docId": item["docId"], "format": "xsl", "keyword": None, "docPart": doc_part,
                "sourceParams": {"source": "Unknown", "category": "Alles"}, "searches": [], "clientID": "bsbe",
                "clientVersion": "bsbe - V06_07_00 - 23.06.2022 11:20", "r3ID": date + "T" + time + "Z"}

        # print(body)

        if item["wait"]:
            timelib.sleep(1.75)

        try:
            import json
            req = requests.post(url=url, cookies=cookies, headers=headers, data=json.dumps(body))
            # print(req.text)
            req.raise_for_status()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            # Log the exception details for debugging
            # print(f"Response text: {req.text}")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head></head><body>{data["head"]}{data["text"]}</body></html>')
            processed_item = {
                "text": html.tostring(doc, pretty_print=True).decode("utf-8"),
                "link": item["link"],
                "docId": item["docId"],
                "doc_part": doc_part,
                "url": "gesetze.berlin.de",
                "filetype": "html"
            }
            result_items.append(processed_item)

    # print(result_items)

    return result_items

def bw(item):
    if (item["wait"] == True): timelib.sleep(1)
    try:
        item["text"] = requests.get(item["link"], headers=config.HEADERS).text
    except:
        output("could not retrieve " + item["link"], "err")
    else:
        if item["text"][1] == "h": # Herausfiltern von leeren Seiten / bei leeren Seite ist text[1] == "!" / schnellere Version
            item["filetype"] = "html"
            return item
        else:
            output("empty page " + item["link"], "err")

def by(item):
    try:
        txt = requests.get(item["link"], headers=config.HEADERS).text
    except:
        output("could not retrieve " + item["link"], "err")
    else:
        if txt[154:160] != "Fehler": # Herausfiltern von leeren Seiten / bei leeren Seite ist text[10] == "h" / schnellere Version
            tree = etree.fromstring(txt.replace('\r\n', '\n'))
            tree.xpath("//script")[0].getparent().remove(tree.xpath("//script")[0]) # Druck-Dialog entfernen
            item["text"] = etree.tostring(tree, pretty_print=True, xml_declaration=True).decode("ascii")
            item["filetype"] = "xhtml"
            return item
        else:
            output("empty page " + item["link"], "err")

def he(item, headers, cookies): # spider.headers, spider.cookies
    # item["text"]: Hessen ist JSON-Post-Response
    url = "https://www.lareda.hessenrecht.hessen.de/jportal/wsrest/recherche3/document"
    encoded_docId = quote(item["docId"], safe=':/')

    headers["x-csrf-token"] = item["xcsrft"]
    headers["Cookie"] = 'r3autologin="bshe"'
    #headers["Referer"] = f"https://www.lareda.hessenrecht.hessen.de/bshe/document/{item['docId']}/part/X"
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    doc_parts = ["X"]
    result_items = []

    for doc_part in doc_parts:
        # print('In--------------', doc_part)
        headers[
            "Referer"] = "https://www.lareda.hessenrecht.hessen.de/bshe/document/" + encoded_docId + "/part/" + doc_part
        item["link"] = headers["Referer"]

        body = {"docId": item["docId"], "format": "xsl", "keyword": None, "docPart": doc_part,
                "sourceParams": {"source": "Unknown", "category": "Alles"}, "searches": [], "clientID": "bsmv",
                "clientVersion": "bsmv - V07_11_01 - 16.10.2023 10:55", "r3ID": date + "T" + time + "Z"}

        # print(body)

        if item["wait"]:
            timelib.sleep(1.75)

        try:
            import json
            req = requests.post(url=url, cookies=cookies, headers=headers, data=json.dumps(body))
            # print(req.text)
            req.raise_for_status()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            # Log the exception details for debugging
            # print(f"Response text: {req.text}")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head></head><body>{data["head"]}{data["text"]}</body></html>')
            processed_item = {
                "text": html.tostring(doc, pretty_print=True).decode("utf-8"),
                "link": item["link"],
                "docId": item["docId"],
                "doc_part": doc_part,
                "url": "www.lareda.hessenrecht.hessen.de",
                "filetype": "html"
            }
            result_items.append(processed_item)

    # print(result_items)

    return result_items

def hh(item, headers, cookies): # spider.headers, spider.cookies
    # item["text"]: Hamburg ist JSON-Post-Response
    url = 'https://www.landesrecht-hamburg.de/jportal/wsrest/recherche3/document'
    headers["Referer"] = "https://www.landesrecht-hamburg.de/bsha/document/" + item["docId"]
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    body = '{"docId":"%s","format":"xsl","keyword":null,"docPart":"L","sourceParams":{"source":"TL","position":1,"sort":"date","category":"Rechtsprechung"},"searches":[],"clientID":"bsha","clientVersion":"bsha - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (item["docId"], date, time)
    if (item["wait"] == True): timelib.sleep(1.75)
    try:
        req = requests.post(url=url, cookies=cookies, headers=headers, data=body)
    except:
        output("could not retrieve " + item["link"], "err")
    else:
        data = req.json()
        doc = html.fromstring(f'<!doctype html><html><head><title>{item["az"]}</title></head><body>{data["head"]}{data["text"]}</body></html>')
        item["text"] = html.tostring(doc, pretty_print=True).decode("utf-8")
        item["filetype"] = "html"
        return item

def mv(item, headers, cookies):
    url = "https://www.landesrecht-mv.de/jportal/wsrest/recherche3/document"
    encoded_docId = quote(item["docId"], safe=':/')

    headers["x-csrf-token"] = item["xcsrft"]
    headers["Cookie"] = 'r3autologin="bsmv"'
    #print(headers)

    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    doc_parts = ["S", "X"]
    result_items = []

    for doc_part in doc_parts:
        #print('In--------------', doc_part)
        headers["Referer"] = "https://www.landesrecht-mv.de/jportal/wsrest/recherche3/document/" + encoded_docId +"/part/" + doc_part
        item["link"] = headers["Referer"]

        body = {"docId":item["docId"],"format":"xsl","keyword":None,"docPart":doc_part,"sourceParams":{"source":"Unknown","category":"Alles"},"searches":[],"clientID":"bsmv","clientVersion":"bsmv - V07_11_01 - 16.10.2023 10:55","r3ID":date+"T"+time+"Z"}

        #print(body)

        if item["wait"]:
            timelib.sleep(1.75)

        try:
            import json
            req = requests.post(url=url, cookies=cookies, headers=headers, data=json.dumps(body))
            #print(req.text)
            req.raise_for_status()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            # Log the exception details for debugging
            #print(f"Response text: {req.text}")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head></head><body>{data["head"]}{data["text"]}</body></html>')
            processed_item = {
                "text": html.tostring(doc, pretty_print=True).decode("utf-8"),
                "link": item["link"],
                "docId": item["docId"],
                "doc_part": doc_part,
                "url": "www.landesrecht-mv.de",
                "filetype": "html"
            }
            result_items.append(processed_item)

    #print(result_items)

    return result_items




def nw(item):
    #print('text', item)
    if (item["wait"] == True): timelib.sleep(0.25)
    try:
        #print(item["link"])
        url = 'https://www.justiz.nrw.de'
        #print(requests.get(url + item["link"], headers=config.HEADERS).text)
        item["text"] = requests.get(url + item["link"], headers=config.HEADERS).text
    except:
        output("could not retrieve " + item["link"], "err")
    else:
        if item["text"][14] == " ": # Herausfiltern von leeren Seiten / bei leeren Seite ist text[14] == " " / schnellere Version
            item["filetype"] = "html"
            #print(item)
            return item
        else:
            output("empty page " + item["link"], "err")


def rp(item, headers, cookies): # spider.headers, spider.cookies
    # item["text"]: Rheinland-Pfalz ist JSON-Post-Response
    url = "https://www.landesrecht.rlp.de/jportal/wsrest/recherche3/document"
    headers["Referer"] = item["link"]
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    doc_parts = ["S", "X"]
    result_items = []
    encoded_docId = quote(item["docId"], safe=':/')

    headers["x-csrf-token"] = item["xcsrft"]
    headers["Cookie"] = 'r3autologin="bsrp"'

    for doc_part in doc_parts:
        # print('In--------------', doc_part)
        headers[
            "Referer"] = "https://www.landesrecht.rlp.de/bsrp/document/" + encoded_docId + "/part/" + doc_part
        item["link"] = headers["Referer"]

        body = {"docId": item["docId"], "format": "xsl", "keyword": None, "docPart": doc_part,
                "sourceParams": {"source": "Unknown", "category": "Alles"}, "searches": [], "clientID": "bsrp",
                "clientVersion": "bsrp - V07_12_00 - 09.11.2023 10:02", "r3ID": date + "T" + time + "Z"}

        # print(body)

        if item["wait"]:
            timelib.sleep(1.75)

        try:
            import json
            req = requests.post(url=url, cookies=cookies, headers=headers, data=json.dumps(body))
            # print(req.text)
            req.raise_for_status()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            # Log the exception details for debugging
            # print(f"Response text: {req.text}")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head></head><body>{data["head"]}{data["text"]}</body></html>')
            processed_item = {
                "text": html.tostring(doc, pretty_print=True).decode("utf-8"),
                "link": item["link"],
                "docId": item["docId"],
                "doc_part": doc_part,
                "url": "www.landesrecht.rlp.de",
                "filetype": "html"
            }
            result_items.append(processed_item)

    # print(result_items)

    return result_items


def sh(item, headers, cookies):
    # item["text"]: Schleswig-Holstein ist JSON-Post-Response
    url = "https://www.gesetze-rechtsprechung.sh.juris.de/jportal/wsrest/recherche3/document"
    headers["Referer"] = item["link"]
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    doc_parts = ["S", "X"]
    result_items = []
    encoded_docId = quote(item["docId"], safe=':/')

    headers["x-csrf-token"] = item["xcsrft"]
    headers["Cookie"] = 'r3autologin="bssh"'

    for doc_part in doc_parts:
        # print('In--------------', doc_part)
        headers[
            "Referer"] = "https://www.gesetze-rechtsprechung.sh.juris.de/bssh/" + encoded_docId + "/part/" + doc_part
        item["link"] = headers["Referer"]

        body = {"docId": item["docId"], "format": "xsl", "keyword": None,
                "docPart": doc_part,
                "sourceParams": {"source": "Unknown", "category": "Alles"}, "searches": [], "clientID": "bssh",
                "clientVersion": "bssh - V07_12_00 - 09.11.2023 10:02", "r3ID": date + "T" + time + "Z"}

        # print(body)

        if item["wait"]:
            timelib.sleep(1.75)

        try:
            import json
            req = requests.post(url=url, cookies=cookies, headers=headers, data=json.dumps(body))
            # print(req.text)
            req.raise_for_status()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            # Log the exception details for debugging
            # print(f"Response text: {req.text}")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head></head><body>{data["head"]}{data["text"]}</body></html>')
            processed_item = {
                "text": html.tostring(doc, pretty_print=True).decode("utf-8"),
                "link": item["link"],
                "docId": item["docId"],
                "doc_part": doc_part,
                "url": "www.gesetze-rechtsprechung.sh.juris.de",
                "filetype": "html"
            }
            result_items.append(processed_item)

    # print(result_items)

    return result_items

def sl(item, headers, cookies): # spider.headers, spider.cookies
    # item["text"]: Saarland ist JSON-Post-Response
    url = "https://recht.saarland.de/jportal/wsrest/recherche3/document"
    headers["Referer"] = item["link"]
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    doc_parts = ["R", "X"]
    result_items = []
    encoded_docId = quote(item["docId"], safe=':/')

    headers["x-csrf-token"] = item["xcsrft"]
    headers["Cookie"] = 'r3autologin="bssl"'

    for doc_part in doc_parts:
        # print('In--------------', doc_part)
        headers[
            "Referer"] = "https://recht.saarland.de/bssl/document/" + encoded_docId + "/part/" + doc_part
        item["link"] = headers["Referer"]

        body = {"docId": item["docId"], "format": "xsl", "keyword": None, "params": {"fixedPart": "true"}, "docPart": doc_part,
                "sourceParams": {"source": "Unknown", "category": "Alles"}, "searches": [], "clientID": "bssl",
                "clientVersion": "bssl - V07_12_00 - 09.11.2023 10:0", "r3ID": date + "T" + time + "Z"}

        # print(body)

        if item["wait"]:
            timelib.sleep(1.75)

        try:
            import json
            req = requests.post(url=url, cookies=cookies, headers=headers, data=json.dumps(body))
            # print(req.text)
            req.raise_for_status()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            # Log the exception details for debugging
            # print(f"Response text: {req.text}")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head></head><body>{data["head"]}{data["text"]}</body></html>')
            processed_item = {
                "text": html.tostring(doc, pretty_print=True).decode("utf-8"),
                "link": item["link"],
                "docId": item["docId"],
                "doc_part": doc_part,
                "url": "recht.saarland.de",
                "filetype": "html"
            }
            result_items.append(processed_item)

    # print(result_items)

    return result_items

def sn(item, headers): # spider.headers
    if "body" in item: # AG/LG/OLG-Subportal
        url = "https://www.justiz.sachsen.de/esamosplus/pages/treffer.aspx"
        headers["Referer"] = "Referer: https://www.justiz.sachsen.de/esamosplus/pages/suchen.aspx"
        if (item["wait"] == True): timelib.sleep(1)
        try:
            item["req"] = requests.post(url=url, headers=headers, data=item["body"])
        except:
            output("could not retrieve " + item["az"], "err")
        else:
            return item
    elif "link" in item: # OVG-Subportal
        if (item["wait"] == True): timelib.sleep(1)
        try:
            # Zwischengeschaltete Seite, von der aus erst der Filelink kopiert werden muss
            tree = html.fromstring(requests.get(item["link"]).text)
        except:
            output("could not retrieve " + item["link"], "err")
        else:
            item["link"] = "https://www.justiz.sachsen.de/ovgentschweb/" + tree.xpath("//a[@target='_blank']/@href")[0]
            return item

def st(item, headers, cookies):
    # item["text"]: Sachsen-Anhalt ist JSON-Post-Response
    url = "https://www.landesrecht.sachsen-anhalt.de/jportal/wsrest/recherche3/document"
    headers["Referer"] = item["link"]
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    body = '{"docId":"%s","format":"xsl","keyword":null,"docPart":"L","sourceParams":{"source":"TL","position":1,"sort":"date","category":"Rechtsprechung"},"searches":[],"clientID":"bsst","clientVersion":"bsst - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (item["docId"], date, time)
    if (item["wait"] == True): timelib.sleep(1.75)
    try:
        req = requests.post(url=url, cookies=cookies, headers=headers, data=body)
    except:
        output("could not retrieve " + item["link"], "err")
    else:
        data = req.json()
        doc = html.fromstring(f'<!doctype html><html><head><title>{item["az"]}</title></head><body>{data["head"]}{data["text"]}</body></html>')
        item["text"] = html.tostring(doc, pretty_print=True).decode("utf-8")
        item["filetype"] = "html"
        return item

def th(item, headers, cookies): # spider.headers, spider.cookies
    # item["text"]: Thüringen ist JSON-Post-Response
    url = "https://landesrecht.thueringen.de/jportal/wsrest/recherche3/document"
    headers["Referer"] = item["link"]
    date = str(datetime.date.today())
    time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
    body = '{"docId":"%s","format":"xsl","keyword":null,"docPart":"L","sourceParams":{"source":"TL","position":1,"sort":"date","category":"Rechtsprechung"},"searches":[],"clientID":"bsth","clientVersion":"bsth - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (item["docId"], date, time)
    if (item["wait"] == True): timelib.sleep(1.75)
    try:
        req = requests.post(url=url, cookies=cookies, headers=headers, data=body)
    except:
        output("could not retrieve " + item["link"], "err")
    else:
        data = req.json()
        doc = html.fromstring(f'<!doctype html><html><head><title>{item["az"]}</title></head><body>{data["head"]}{data["text"]}</body></html>')
        item["text"] = html.tostring(doc, pretty_print=True).decode("utf-8")
        item["filetype"] = "html"
        return item

def ni(item):
    if (item["wait"] == True): timelib.sleep(1)
    try:

        response = requests.get(item["link"], headers=config.HEADERS)
        #print(response)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find h2 elements with specific text
            desired_texts = ["Bibliographie", "Tenor: ", "Gründe", "Entscheidungsgründe", "Tatbestand", "Gründe:", "Entscheidungsgründe:"]
            h2_elements = [h2 for h2 in soup.find_all("h2") if h2.get_text() in desired_texts]
            # Extract text from found h2 elements

            desired_h2_elements = [h2 for h2 in soup.find_all("h2") if h2.get_text() in desired_texts]

            # Extract content beneath the desired h2 elements
            main_text = ""
            desired_heading = "Gründe"
            for h2 in desired_h2_elements:
                content = ""
                content += str(h2)
                para_number = 1
                for sibling in h2.find_next_siblings():
                    if sibling.name == "h2":  # Stop if another h2 element is encountered
                        break
                    #print('h2', sibling.get_text())
                    if h2.get_text() == "Gründe" or h2.get_text() == "Gründe:" or h2.get_text() == "Entscheidungsgründe" or h2.get_text() == "Entscheidungsgründe:" or h2.get_text() == "Tatbestand":
                        #print('sic',sibling.name)
                        if sibling.name == "p":
                            modified_text = "Randnummer" + str(para_number) + " " + str(sibling)
                            # Remove paragraphs with 2 or 3 characters
                            if len(sibling.get_text(strip=True)) >= 3:
                                content += modified_text
                                para_number += 1
                        elif sibling.name == "div":
                            # Check if the div contains a p element
                            p_elements = sibling.find_all("p")
                            if p_elements:
                                for p in p_elements:
                                    # Check the length of text in the paragraph
                                    if len(p.get_text(strip=True)) >= 3:
                                        modified_text = "Randnummer" + str(para_number) + " " + str(p)
                                        content += modified_text
                                        para_number += 1
                    elif h2.get_text() == "Bibliographie":
                        if sibling.name == "dl":
                            # Process the <dl> structure to maintain 'key: value' format
                            dts = sibling.find_all("dt")
                            dds = sibling.find_all("dd")
                            for dt, dd in zip(dts, dds):
                                key = dt.get_text(": ", strip=True)
                                value = dd.get_text(strip=True)

                                modified_text = f"{key}: {value}<br>"
                                content += modified_text + " "  # Add 'key: value' pairs to content
                    else:

                        content += str(sibling)  # Retain HTML structure
                main_text += content

                # Create a new BeautifulSoup object with the extracted content
            new_soup = BeautifulSoup(main_text, 'html.parser')

            item["text"] = new_soup.prettify()



    except:
        output("could not retrieve " + item["link"], "err")
    else:
        # Herausfiltern von leeren Seiten / bei leeren Seite ist text[1] == "!" / schnellere Version
        item["filetype"] = "html"
        return item