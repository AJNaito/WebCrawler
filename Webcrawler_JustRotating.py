import requests
import threading
import time
import random as rand
import csv
import re
from bs4 import BeautifulSoup as Parser
from threading import Thread

# Simple Webcrawler that extracts/scraps relevant data starting from the initial website
# Added threading to improve throughput

## initialize lock
urlLock = threading.Lock()
productLock = threading.Lock()

# initial URLS
urls = {"https://scrapeme.live/shop/"}
visited = []

#target data
products = []

# User Agents
UserAgents = [
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
]

def ScalpData(url):
    data = threading.local()
    data.Header = { "User-Agent": rand.choice(UserAgents) }



    response = requests.get(url, headers=data.Header)

    data.parsed = Parser(response.content, 'html.parser')
    links = data.parsed.select('a[href]')

    urlLock.acquire()
    try:
        for link in links:
            nextURL = link['href']

            if re.match("^https://scrapeme.live/shop/.+", nextURL) and nextURL not in visited and nextURL not in urls:
                urls.add(nextURL)
    finally:
        urlLock.release()
    
    data.productName = data.parsed.select_one(".product_title")
    data.price = data.parsed.select_one(".price")
    data.image = data.parsed.select_one(".wp-post-image")

    if (data.productName and data.price and data.image):
        data.product = {}
        data.product["URL"] = url
        data.product["Name"] = data.productName.string
        data.product["Price"] = data.price.text
        data.product["Image"] = data.image["src"]

        productLock.acquire()
        products.append(data.product)
        productLock.release()

def main():
    ## Keep going until subdomains are all searched and until all threads have finished
    while len(urls) != 0 or len(threading.enumerate()) > 1:
        ## Make a new thread if less than 5 currently active and valid URLs to pull
        if (len(threading.enumerate()) <= 5 and len(urls) > 0):
            ## get the current url 
            urlLock.acquire()
            curUrl = urls.pop()
            visited.append(curUrl)
            urlLock.release()

            ## Create new Thread
            Thread(target=ScalpData, name = threading.current_thread(), args=[curUrl], daemon = True).start()
            print(len(threading.enumerate()))
            time.sleep(0.5) ## Avoid overloading server

    #write to csv
    with open("Test-Products-GeneralTest.csv", 'w', newline='') as csvfile:
        writerCSV = csv.DictWriter(csvfile, fieldnames=["URL", "Name", "Price", "Image"])
        writerCSV.writeheader()
        for product in products:
            writerCSV.writerow(product)

if __name__=="__main__":
    main()    