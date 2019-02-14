
# coding: UTF-8
import requests
import re
import uuid
from bs4 import BeautifulSoup

url = "https://search.nifty.com/imagesearch/search?select=1&chartype=&q=%s&xargs=2&img.fmt=all&img.imtype=color&img.filteradult=no&img.type=all&img.dimensions=large&start=%s&num=20"
keyword = ""
pages = [1,20,40,60,80,100]

for p in pages:
        r = requests.get(url%(keyword,p))
        soup = BeautifulSoup(r.text,'lxml')
        imgs = soup.find_all('img',src=re.compile('^https://msp.c.yimg.jp/yjimage'))
        for img in imgs:
                r = requests.get(img['src'])
                with open(str('./data/')+str(uuid.uuid4())+str('.jpeg'),'wb') as file:
                        file.write(r.content)
                        
print("finish")