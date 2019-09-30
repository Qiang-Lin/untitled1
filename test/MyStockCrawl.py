import re
import requests
from bs4 import BeautifulSoup
import traceback
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['stock']
collection1 = db['stock_info']


def getHTMLText(url, code='utf-8'):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ""


def getStockList(lst, stockURL):
    mcount = 0
    html = getHTMLText(stockURL, 'GB2312')
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
    for i in a:
        if mcount < 200:
            try:
                mcount = mcount + 1
                href = i.attrs['href']
                lst.append(re.findall(r"[s][hz]\d{6}", href)[0])
            except:
                continue


def getStockInfo(lst, stockURL, fpath):
    count = 0
    for stock in lst:
        url = stockURL + stock + ".html"
        html = getHTMLText(url)
        try:
            if html == "":
                continue
            infoDict = {}
            soup = BeautifulSoup(html, 'html.parser')
            stockInfo = soup.find('div', attrs={'class': 'stock-bets'})
            name = stockInfo.find_all(attrs={'class': 'bets-name'})[0]
            infoDict.update({'股票名称': name.text.split()[0]})
            keyList = stockInfo.find_all('dt')
            valueList = stockInfo.find_all('dd')
            for i in range(len(keyList)):
                key = keyList[i].text
                val = valueList[i].text
                infoDict[key] = val
            saveToDatabase(infoDict)
            with open(fpath, 'a', encoding='utf-8') as f:
                f.write(str(infoDict) + '\n')
                count = count + 1
                print('\r当前速度:{:.2f}%'.format(count * 100 / len(lst)), end='')
        except:
            count = count + 1
            print('\r当前速度:{:.2f}%'.format(count * 100 / len(lst)), end='')
            continue


def saveToDatabase(infoDict):
    saveStockInfo(infoDict)


def saveStockInfo(infoDict):
    collection1.insert_one(infoDict)


def main():
    stock_list_url = 'http://quote.eastmoney.com/stock_list.html'
    stock_info_url = 'https://gupiao.baidu.com/stock/'
    output_file = 'D://BaiduStockInfo.txt'
    slist = []
    getStockList(slist, stock_list_url)
    getStockInfo(slist, stock_info_url, output_file)


main()
