import json
import os
import re
import sys
import time
from bs4 import BeautifulSoup as BSoup
from urllib.parse import quote_plus as quote, unquote_plus as unquote
from requests import get
from pydotmap import DotMap
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


chromedriver_autoinstaller.install()
options = Options()
options.add_argument("log-level=3")
options.add_argument("--headless")
loop = 1
true_rage = 0
jumlah_file = 0

range_data = int(input("Masukkan jumlah data yang diinginkan: "))
if range_data > 10:
    loop = round(range_data / 10)
    true_rage = range_data
    range_data = 10
else:
    true_rage = range_data


query = quote(input("Masukkan pencarian: "))
serch_name = query
LIST = []
json_data_list = []
#driver = Chrome(options=options)

def mulai_scrape():
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://id.pinterest.com/search/pins/?q={query}")
    WebDriverWait(driver, 30).until(
        ec.presence_of_element_located((By.XPATH, "//div[@class='gridCentered']"))
    )
    ambil_data(driver)

def ext_scrap():
    extracted_urls, keyword = start_scraping(query, {})
    for i in extracted_urls:
        get_source(i, {})
    result1 = save_image_url()
    return result1

def ambil_data(driver):
    global jumlah_file
    WebDriverWait(driver, 10).until(
        ec.presence_of_all_elements_located((By.XPATH, "//div[@class='Yl- MIw Hb7']"))
    )
    soup = BSoup(driver.page_source, "html.parser")
    a = soup.find_all("a")
    final_source = []
    for href in a:
        if hasattr(href, "href") and hasattr(href, "img"):
            pin_id: str = href["href"] or ""
            pin_id = re.search(r"/pin/(\d+)/", pin_id).group(1) if pin_id.startswith("/pin/") else ""
            img = href.img or {"src": ""}
            img = img["src"]
            if pin_id and img:
                final_source.append({"pin_id": pin_id, "img": img})
    results = [{"id": i["pin_id"], "name_category": unquote(serch_name).replace(" ", "_"), "title": unquote(serch_name), "image": i["img"]} for i in final_source]
    data = ext_scrap()
    final_result = data+results
    if len(final_result) >= 1:
        print(f"Collectiong data .... {len(final_result)}")
        jumlah_file += len(final_result)
        for x in final_result:
            LIST.append(x)
        driver.quit()

def get_pinterest_links(body):
        searched_urls = []
        html = BSoup(body, 'html.parser')
        links = html.select('#main > div > div > div > a')
        for link in links:
            link = link.get('href')
            link = re.sub(r'/url\?q=', '', link)
            if link[0] != "/" and "pinterest" in link:
                searched_urls.append(link)

        return searched_urls

def get_source(url, proxies):
        try:
            res = get(url, proxies=proxies)
        except Exception as e:
            return
        html = BSoup(res.text, 'html.parser')
        json_data = html.find_all("script", attrs={"id": "__PWS_DATA__"})
        for a in json_data:
            json_data_list.append(a.string)

def save_image_url():
        url_list = [i for i in json_data_list if i.strip()]
        if not len(url_list):
            return url_list
        url_list = []
        for js in json_data_list:
            try:
                data = DotMap(json.loads(js))
                urls = []
                for pin in data.props.initialReduxState.pins:
                    if isinstance(data.props.initialReduxState.pins[pin].images.get("orig"), list):
                        for i in data.props.initialReduxState.pins[pin].images.get("orig"):
                            urls.append({"pin_id": pin, "img":i.get("url")})
                    else:
                        urls.append({"pin_id": pin, "img":data.props.initialReduxState.pins[pin].images.get("orig").get("url")})

                
                results = [{"id": i["pin_id"], "name_category": unquote(serch_name).replace(" ", "_"), "title": unquote(serch_name), "image": i["img"]} for i in urls]

            except Exception as e:
                continue
        
        return results

def start_scraping(key=None, proxies={}):
        assert key != None, "Please provide keyword for searching images"
        keyword = key + " pinterest"
        keyword = keyword.replace("+", "%20")
        url = f'http://www.google.co.in/search?hl=en&q={keyword}'
        res = get(url, proxies=proxies)
        searched_urls = get_pinterest_links(res.content)

        return searched_urls, key.replace(" ", "_")

        


def Compail():
    with open("result.json", "w") as file:
        file.write(json.dumps(LIST, indent=4))
        file.close()
        sys.exit("Scraping selesai")

EJEKULASI = False
COUNT = 0
ERROR = ''
for x in range(loop):
    COUNT += 1
    try:
        mulai_scrape()
        if jumlah_file >=true_rage:
            break
    except Exception as e:
        ERROR = e
        EJEKULASI = True
        continue
    query = serch_name
    query = query+str(COUNT)
    time.sleep(2)

if EJEKULASI == True:
    print(f"Terjadi error: {ERROR}")
print(f"Compailing {len(LIST)} data into Json File.")
Compail()
