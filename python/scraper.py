from bs4 import BeautifulSoup
import json
import requests

url_storage = []
url = ''
r  = requests.get(url)
data = r.text
soup = BeautifulSoup(data)
with open('data.txt', 'w') as outfile:
    for link in soup.find_all('a'):
        l = link.get('href')
        if l != None:
            if l.startswith('/forums'):
                url_storage.append(l)
    json.dump(url_storage, outfile)  
