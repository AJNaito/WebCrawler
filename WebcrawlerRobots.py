import requests
import threading
import csv
import time
import random
import re
from bs4 import BeautifulSoup as Parser
from threading import Thread

# Simple Webcrawler that extracts/scraps relevant data starting from the initial website
# Added threading to improve throughput
# Checks for a robot.txt and updates not allowed sites for scraping

## initialize lock
urlLock = threading.Lock()
productLock = threading.Lock()

# initial URLS
urls = {"https://scrapeme.live/shop/"}
visited = []

#target data
products = []

#Headers for CSV
Headers = []

#Data classes in HTML
Classes = []

# Data for rotating User Agents
UserAgents = [
    ## Simulates different browsers and different devices
    "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.", 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36", 
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'"
]

Allowed = []

def ScalpData(url, website, Headers, Classes):
    data = threading.local()
    data.headers = {"User-Agent": random.choice(UserAgents)}

    ## Sleep so that we don't overload webserver (so we don't get blocked)
    time.sleep(0.5)

    response = requests.get(url, data.headers)

    data.parsed = Parser(response.content, 'html.parser')
    links = data.parsed.select('a[href]')

    urlLock.acquire()
    try:
        for link in links:
            nextURL = link['href']

            if re.match(website, nextURL) and nextURL not in visited and nextURL not in urls:
                urls.add(nextURL)
    finally:
        urlLock.release()
    
    ## Get the scraped data
    data.data = []
    for Type in Classes:
        data.data.append(data.parsed.select_one(Type))

    ##Extract the data
    data.product = {}
    data.product["URL"] = url
    for i in range(len(Headers)):
        if (not data.data[i]):
            
            return
        try:
            data.product[Headers[i]] = data.data[i].text
            continue
        except:
            del data.product[Headers[i]]
        try: 
            data.product[Headers[i]] = data.data[i].string
            continue
        except:
            del data.product[Headers[i]]
        try:
            data.product[Headers[i]] = data.data[i]["src"]
        except:
            data.product = {}

    if len(data.product) == len(Headers) + 1:
        productLock.acquire()
        products.append(data.product)
        productLock.release()

def AllowedSite(URL) -> bool:
    for site in Allowed:
        if site in URL:
            return False
    
    return True

def Parse_Robots(robotsURL, Allowed):
    print(robotsURL)
    robots = requests.get(robotsURL, stream=True)
    if (robots):
        for line in robots.iter_lines(decode_unicode=True):
            line = str(line)
            print(line)
            if (re.match("(Allow):", line)):
                Allowed.append(line.split(':', maxsplit= 1)[1])

def main():
    websites = input("Input Initial Browsers to search, separated by a comma\n")
    websites = websites.split(",")
    
    # Headers_ = input("Input Data Headers, separated by a comma. URLs are automatically collected\n")
    # Headers = Headers_.split(",")

    # print(len(Headers))
    # print("Input Expected HTML Classes individually. Should be the same as data headers")
    # while len(Classes) != len(Headers):
    #     Classes.append(input())

    for website in websites:
        curSite = re.search("www\..+\.(com|edu|gov)", website)
        print(curSite)
        #Check if website has /robots.txt file
        if curSite:

            Allowed.clear()
            visited.clear()
            Parse_Robots(curSite.string + "/robots.txt", Allowed)
            print(Allowed)

        urls.add(website)
            
    #     ## Keep going until subdomains are all searched and until all threads have finished
    #     while len(urls) != 0 or len(threading.enumerate()) > 1:
    #             ## Make a new thread if less than 5 currently active and valid URLs to pull
    #         if (len(threading.enumerate()) <= 5 and len(urls) > 0):
    #             ## get the current url 
    #             urlLock.acquire()
    #             curUrl = urls.pop()
                    
    #             ## If not an allowed site, continue with other URLS
    #             if (not AllowedSite(curUrl)):
    #                 urlLock.release()
    #                 continue

    #             visited.append(curUrl)
    #             urlLock.release()

    #             ## Create new Thread
    #             Thread(target=ScalpData, name = threading.current_thread(), args=[curUrl, website, Headers, Classes], daemon = True).start()
                
    #             productLock.acquire()
    #             print(len(products))
    #             productLock.release()
        

            
            
    # #write to csv
    # with open("Test-Products-Threading.csv", 'w', newline='') as csvfile:
    #     writerCSV = csv.DictWriter(csvfile, fieldnames=Headers)
    #     writerCSV.writeheader()
    #     for product in products:
    #         writerCSV.writerow(product)

if __name__=="__main__":
    main()    