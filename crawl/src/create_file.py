# -*- coding: utf-8 -*-
from fileinput import filename
import os
import requests
from io import BytesIO
from .output import output
from zipfile import ZipFile

def info(item):
    #print('item', item)
    if "link" in item:
        output("downloading " + item["link"] + "...")
    return item

def save_as_html(items, spider_name, spider_path, store_docId): # spider.name, spider.path
    processed_items = []
    for item in items:
        info(item)
        #print('yes')
        if (spider_name == "bund"): # Sonderfall Bund und Bayern: *.zip mit *.xml
            #filename = item["court"] + "_" + item["date"] + "_" + item["az"]
            #if store_docId and item.get('docId'):
            #print(item)
            filename = item['docId']
            """try:
                with ZipFile(BytesIO((requests.get(item["link"]).content))) as zip_ref: # Im RAM entpacken
                    for zipinfo in zip_ref.infolist(): # Teilweise auch Bilder in .zip enthalten
                        if (zipinfo.filename.endswith(".xml") and ("manifest" not in zipinfo.filename)):
                            zipinfo.filename = filename
                            #bayportalrsp
                            item["xmlfilename"] = os.path.join(spider_path, spider_name, zipinfo.filename)
                            zip_ref.extract(zipinfo, os.path.join(spider_path, spider_name))"""
            """except:
                output(f"could not create file {filename}", "err")"""

            processed_items.append(item)
        else:
            #if "text" in item and "court" in item and "date" in item and "az" in item and "filetype" in item:
            if "az" in item and item["az"] is not None:
                filename = item["court"] + "_" + item["date"] + "_" + item["az"]

            if item.get('docId') and item.get('doc_part') is not None:
                filename = item["url"] + "_" + item['docId'] + "_" + item["doc_part"]
            else:
                filename = item["url"] + "_" + item['docId']
            filename += "." + item["filetype"]
            filepath = os.path.join(spider_path, spider_name, filename)
            #enc = "utf-8" if spider_name != "by" else "ascii"
            enc = "utf-8"
            try:
                with open(filepath, "w", encoding=enc) as f:
                    f.write(item["text"])
            except:
                output(f"could not create file {filepath}", "err")
            else:
                processed_items.append(item)
    return processed_items

def save_as_pdf(items, spider_name, spider_path): # spider.name, spider.path
    processed_items = []
    for item in items:
        #print(item)
        info(item)
        content = ""
        if "link" in item and not "body" in item: # Bremen / Sachsen (OVG)
            try:
                content = requests.get(url=item["link"]).content
            except:
                output("could not retrieve " + item["link"], "err")
        elif "body" in item: # Sachsen (AG/LG/OLG)
            content = item["body"]
        #if content and "court" in item and "date" in item and "az" in item:
            #filename = item["court"] + "_" + item["date"] + "_" + item["az"] + ".pdf"
        if item:
            filename = item["url"] + "_" + item['docId']
            filepath = os.path.join(spider_path, spider_name, filename)
            try:
                with open(filepath, "wb") as f:
                    f.write(content)
            except:
                output(f"could not create file {filepath}", "err")
            else:
                processed_items.append(item)


        else:
            output("missing information " + item["link"], "err")
        return processed_items
