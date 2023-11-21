import asyncio
import aiohttp
import os
from bs4 import BeautifulSoup
import datetime
import re
from src import config
from lxml import html

output_directory = "downloaded_pages10"
os.makedirs(output_directory, exist_ok=True)
previous_title = ""
title_counter = 0

async def fetch_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                return text
            else:
                print(f"Failed to fetch {url}. Status code: {response.status}")
                return None

async def get_text(url):
    global previous_title, title_counter
    item = {"link": url}
    text = await fetch_text(url)
    #print(text)
    if text:
        soup = BeautifulSoup(text, 'html.parser')
        # Your existing parsing logic here...
        # Find h2 elements with specific text
        link_element = soup.select_one(
            '#block-voris-nds-documentactionsblock > div > ul > li:nth-of-type(1) > div > div > a')
        element = soup.select_one('#block-voris-nds-documenttocblock > div > details > summary > h2 > span > span > '
                                  'span:nth-of-type(1)')
        current_title = element.get_text(strip=True).rsplit(',', 1)[0]
        #print('prev',previous_title)
        #print('current', current_title)
        if current_title == previous_title:
            title_counter += 1
            item['title'] = f"{current_title}_{title_counter}"
        else:
            title_counter = 0
            item['title'] = f"{current_title}_{title_counter}"
        item["text"]= text

        # Check if the element is found
        #if link_element:
            # Extract the link (href attribute)
            #link = link_element.get('href')
            #print("Link:", link)

            #print("Text Content:", title)

            #item["text"] = await fetch_text('https://voris.wolterskluwer-online.de' + link)
        previous_title = current_title
        #item["title"] = current_title


        """desired_h2_elements = [h2 for h2 in soup.find_all("h2") if h2.get_text() in desired_texts]

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
                # print('h2', sibling.get_text())
                if h2.get_text() == "Gründe" or h2.get_text() == "Gründe:" or h2.get_text() == "Entscheidungsgründe" or h2.get_text() == "Entscheidungsgründe:" or h2.get_text() == "Tatbestand":
                    # print('sic',sibling.name)
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
                            if key == "Gericht":
                                item["court"] = value
                            if key == "Datum":
                                item["date"] = value
                            if key == "Aktenzeichen":
                                item["az"] = value

                            modified_text = f"{key}: {value}<br>"
                            content += modified_text + " "  # Add 'key: value' pairs to content
                else:

                    content += str(sibling)  # Retain HTML structure
            main_text += content

            # Create a new BeautifulSoup object with the extracted content
        new_soup = BeautifulSoup(main_text, 'html.parser')



        # Update item details based on parsing logic
        item["text"] = new_soup.prettify()"""
        item["filetype"] = "html"  # Assuming it's always HTML
        item['url'] = "voris.wolterskluwer-online.de"

        # Return the updated item
        return item
    else:
        print(f"Could not retrieve {url}")
        return None

async def save_as_html(item):
    # Your existing saving logic here...
    await info(item)
    if "text" in item and "filetype" in item:
        filename = item['url'] + '_' + item["title"]

        filename += "." + item["filetype"]
        filepath = os.path.join(output_directory, filename)
        enc = "utf-8"
        try:
            with open(filepath, "w", encoding=enc) as f:
                f.write(item["text"])
        except:
            print(f"could not create file {filepath}", "err")
        else:
            return item
    else:
        print("could not retrieve " + item["link"], "err")


async def info(item):
    # print('item', item)
    if "link" in item:
        print("downloading " + item["link"] + "...")
    return item

async def process_item(item):
    # Your existing item processing logic here...
    item["date"] = item["date"].strip()
    item["date"] = datetime.datetime.strptime(item["date"], "%d.%m.%Y").strftime("%Y%m%d")
    item["az"] = item["az"].strip()
    item["az"] = item["az"].replace("/", "-")
    item["az"] = item["az"].replace(".", "-")
    item["az"] = re.sub(r"\s", "-", item["az"])
    court = item["court"].lower()
    court = court.strip()
    court = re.sub(r"\s", "-", court)
    court = court.translate(config.UMLAUTE)
    item["court"] = court
    return item


async def main():
    tasks = []
    with open('C:/Users/admin/Documents/Practice/webCrawling/crawl/laws_urls.txt', 'r') as file:
        for line in file:
            url = line.strip()
            if 'filter' not in url:
                #print(url)
                item = await get_text(url)
                if item:
                    #item = await process_item(item)
                    await save_as_html(item)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
