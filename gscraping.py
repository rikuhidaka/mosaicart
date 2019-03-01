#coding: utf-8

import os
from six.moves import urllib
import bs4

def main(keyword,id,hoge):
    #検索キーワード
    if not os.path.exists("./" + id + "/data"):
        os.mkdir("./" + id + "/data")
    
    urlKeyword = urllib.parse.quote(keyword)
    url = 'https://www.google.com/search?hl=jp&q=' + urlKeyword + '&btnG=Google+Search&tbs=0&safe=off&tbm=isch'
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",}
    request = urllib.request.Request(url=url, headers=headers)
    page = urllib.request.urlopen(request)
    
    html = page.read().decode('utf-8')
    html = bs4.BeautifulSoup(html, "html.parser")
    elems = html.select('.rg_meta.notranslate')
    counter = 0
    c = 0
    for ele in elems:
        ele = ele.contents[0].replace('"','').split(',')
        eledict = dict()
        for e in ele:
            num = e.find(':')
            eledict[e[0:num]] = e[num+1:]
        imageURL = eledict['ou']
        
        pal = '.jpg'
        if '.jpg' in imageURL:
            pal = '.jpg'
        elif '.JPG' in imageURL:
            pal = '.jpg'
        elif '.png' in imageURL:
            pal = '.png'
        elif '.gif' in imageURL:
            pal = '.gif'
        elif '.jpeg' in imageURL:
            pal = '.jpeg'
        else:
            pal = '.jpg'

        c += 1
        hoge[id] = round(float(c)/float(len(elems)),2)
        print(hoge[id])
 

#保存場所の設定
        try:
            img = urllib.request.urlopen(imageURL)
            localfile = open('./' + id + '/data/'+keyword+str(counter)+pal, 'wb')
            localfile.write(img.read())
            img.close()
            localfile.close()
            counter += 1

        except UnicodeEncodeError:
            continue
        except urllib.error.HTTPError:
            continue
        except urllib.error.URLError:
            continue
if __name__ == "__main__":
    main("hoge","static",{"static":0.0})

