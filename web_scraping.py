import requests
from bs4 import BeautifulSoup
import re
import csv
import time
from concurrent.futures import ThreadPoolExecutor




def cal_page(url):
    r = requests.get(url) 
    main = BeautifulSoup(r.text, 'html.parser')

    sorry_page = main.find('div', class_="dui-container sorry _centered")
    _item_num_info = main.find('div', class_="dui-breadcrumb")

    if sorry_page != None:
        sorry_mg = re.findall('<p>(.*?)</p>', str(sorry_page))
        sorry_mg = sorry_mg[0]
        print(sorry_mg)

        page = 0
        item_sum_num = 0
    
    else:
        try:
            item_num_info = re.findall('class="count _medium">(.*?)</span>', str(_item_num_info))

            item_num = re.findall('〜(.*?)件',str(item_num_info))
            item_sum_num = re.findall('（(.*?)件',str(item_num_info))
            item_sum_num = item_sum_num[0].replace(",","")

            p = divmod(int(item_sum_num),int(item_num[0]))

            if p[1]==0:
                page = p[0]
            else:
                page = p[0] + 1
            return page , int(item_sum_num)

        except IndexError as e:
            page = 0
            item_sum_num = 0

    return page , int(item_sum_num)   


def scraping(url):
    r = requests.get(url) 
    main = BeautifulSoup(r.text, 'html.parser')

    items_url = list(main.find_all('div', class_="dui-card searchresultitem"))

    items_list = []

    for i in range(len(items_url)):
        item_url = items_url[i]
        img_url = item_url.find('img', class_="_verticallyaligned")

        _item_img = re.findall('src=".*?"',str(img_url))

        _item_name = re.findall('data-item-name=".*?"',str(item_url))
        _item_price = re.findall('data-price=".*?"',str(item_url))
        _item_url = re.findall('data-item-url=".*?"',str(item_url))

        item_name = re.findall('\"(.*)\"',_item_name[0])
        item_price = re.findall('\"(.*)\"',_item_price[0])
        item_url = re.findall('\"(.*)\"',_item_url[0])
        item_img = re.findall('\"(.*)\"',_item_img[0])

        item_list = [item_url[0],item_name[0],item_price[0],item_img[0]]
        
        items_list.append(item_list)

    
    return items_list

startTime = time.time()

#ファイル初期化----------------------------------------------
column_list = ["商品URL","商品名","商品価格","商品画像URL"]

path = "/Users/arakitomohito/desktop/python/scraping/"

csv_path = path + "scraping.csv"

with open(csv_path,"w",encoding = "shift-jis") as f:
    writer = csv.writer(f)
    writer.writerow(column_list)
#----------------------------------------------------------



#検索結果の最高の値段を調べる-----------------------------------
min = 100000
page = None

while page != 0:
    original_url = 'https://search.rakuten.co.jp/search/mall/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9/?min={}'.format(min)
    page = cal_page(original_url)[0]

    if page != 0:
        min = min * 10
    
limit_price = min
#----------------------------------------------------------

min = 100000
range_price = 1000000
max = 1000000

#ページ数から検索結果アイテム数のmax値を決める--------------------
original_url = 'https://search.rakuten.co.jp/search/mall/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9/?min={}&max={}'.format(min,max)

df = cal_page(original_url)

page = df[0]
max_item_num = df[1]
scrapied_item_num = 0
#----------------------------------------------------------


while min < limit_price:
    #print("{}/{}のデータを取得しました。".format(scrapied_item_num , max_item_num))
    range_price = 1000000
    if page > 150:
        while page > 150:
            range_price = range_price//2
            max = min + range_price
            original_url = 'https://search.rakuten.co.jp/search/mall/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9/?min={}&max={}'.format(min,max)
            page = cal_page(original_url)[0]
        print("最小値{}、最大値{}のページ数{}のURL情報を取得しました。".format(min,max,page))
        print("------")

    elif 0 < page <= 150:
        print("最小値{}、最大値{}のページ数{}のURL情報を取得しました。".format(min,max,page))
        print("------")

    elif page == 0:
        pass

    scrapied_item_num = scrapied_item_num + df[1]

    print(scrapied_item_num)

    #スクレイピングするためのURL
    if not page == 0:
        with ThreadPoolExecutor(max_workers=10, thread_name_prefix="thread") as executor:
            futures = []
            for i in range(1,page+1):
                print("{}ページ目の情報を取得します。".format(i))
                lists_url = 'https://search.rakuten.co.jp/search/mall/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9/?min={}&max={}&p={}'.format(min,max,i)

                futures.append(executor.submit(scraping, lists_url))

        for _result in futures:
            for result in _result.result():
                with open(csv_path,"a",encoding="shift_jis",errors='ignore') as f:
                    writer = csv.writer(f)
                    writer.writerow(result)

    min = max
    max = min + range_price
    original_url = 'https://search.rakuten.co.jp/search/mall/%E3%83%AD%E3%83%AC%E3%83%83%E3%82%AF%E3%82%B9/?min={}&max={}'.format(min,max)


    df = cal_page(original_url)
    page = df[0]
    #print("{}/{}のデータを取得しました。".format(scrapied_item_num , max_item_num))

    if min >= limit_price:
        print("完了しました")
        break


print("end")

endTime = time.time()
runTime = endTime - startTime
print (f'Time:{runTime}[sec]')



