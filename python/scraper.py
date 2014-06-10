from bs4 import BeautifulSoup
import json
import requests

url_storage = []
url = ''
while url != '':
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    for link in soup.find_all('a'):
        l = link.get('href')
        if l != None:
            if l.startswith('/forums'):
                l = junct_prepnd + l
                url_storage[l] = url_storage.get(l, 'place_holder_text')
            elif l.find('page') > -1:
                page_link[l] = page_link.get(l, 0) + 1
    for i, j in page_link.iteritems():
        if j < 10
            page_link[i] = page_link.get(i) + 8
            url = i
            print url
            break
        else:
            url = ''
with open('data.txt', 'w') as outfile:
    json.dump(url_storage, outfile)

for k, l in url_storage.iteritems():
    if l == 'place_holder_text':
        m = ''
        r  = requests.get(k)
        data = r.text
        soup = BeautifulSoup(data)
        for div in soup.find_all('div', { 'class' :'msgtxt'}):
            for c in div.contents:
                m += unicode(c)
            print c
            url_storage[k] = m
with open('posts.txt', 'w') as outfile:
    json.dump(url_storage, outfile)
