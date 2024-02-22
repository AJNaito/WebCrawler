import requests
import threading
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

def ScalpData(url):
    response = requests.get(url)
    data = threading.local()

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
            print (len(threading.enumerate()))

            # ## get information from the current url
            # response = requests.get(curUrl)    # initial URLS

            # # parse raw HTML data
            # parsed = Parser(response.content, 'html.parser')

            # # get the embedded links and add to the urls to explore
            # links = parsed.select('a[href]')
            # for link in links:
            #     nextURL = link['href']
                
            #     ## only grab explicit links
            #     if re.match("^https://scrapeme.live/shop/.+", nextURL) and not nextURL in visited and nextURL not in urls:
            #         urls.append(nextURL)

            # # data extraction
            # productName = parsed.select_one(".product_title")
            # price = parsed.select_one(".price")
            # image = parsed.select_one(".wp-post-image")

            # if (productName and price and image):
            #     product = {}
            #     product["URL"] = curUrl
            #     product["Name"] = productName.string
            #     product["Price"] = price.text
            #     product["Image"] = image["src"]
            #     products.append(product)

            # count += 1
            # print(count)

    #write to csv
    with open("Test-Products-Threading.csv", 'w', newline='') as csvfile:
        writerCSV = csv.DictWriter(csvfile, fieldnames=["URL", "Name", "Price", "Image"])
        writerCSV.writeheader()
        for product in products:
            writerCSV.writerow(product)

if __name__=="__main__":
    main()    