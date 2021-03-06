#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import os
#import urllib'
import urllib2
import csv
import time

from pyquery import PyQuery as pq

def download_roothtml():
    root_url = "http://www.qylbbs4.com/thread/81/"
    response = requests.request("GET", root_url)
    fo = open("./root/root.html", "wb")
    fo.write(response.text)
    fo.close()

def get_root_info():
    download_roothtml()
    doc = pq(filename='./root/root.html')
    lis = doc(".pages_next").prev().html()
    page_num = lis.replace("...","")
    #print page_num
    data = {}
    data['page_num'] = page_num
    return data



#print get_root_info()

def craw_page(page):

    page_url = "http://www.qylbbs4.com/thread/81/"+str(page)
    response = requests.request("GET", page_url)
    fo = open("./page/"+str(page)+".html", "wb")
    fo.write(response.text)
    fo.close()

    doc = pq(filename="./page/"+str(page)+".html")
    trs = doc("#J_posts_list tr")


    for tr in trs.items():

        tr_title = tr(".common")(".title").text()
        links = tr(".common")(".title")("a").items()
        link_url = ""
        for link in links:
            if "read" in link.attr("href"):
                link_url = link.attr("href")
        #print tr_title
        #print link_url

        inp = {}
        inp['title'] = tr_title
        inp['url'] = link_url

        try:
            craw_article(inp)
        except:
            print "--"




def craw_article(inp):

    title = inp['title']
    url = inp['url']

    print url.split("/")[-1]+"------ article:" + url + "------" + title

    with open("./dict.csv", 'ab') as myFile:
        myWriter = csv.writer(myFile)
        myWriter.writerow([url.split("/")[-1],title])

    response = requests.request("GET", url)

    article_path = "./article/" + url.split("/")[-1] + ".html"
    fo = open(article_path, "wb")
    fo.write(response.text)
    fo.close()

    doc = pq(filename=article_path)
    imgs = doc(".editor_content")(".J_post_img")

    img_id = 1
    for img in imgs.items():

        iurl = img.attr("src")
        save_img(iurl,str(img_id),"./img/"+url.split("/")[-1])
        img_id += 1



'''
def save_img(img_url,file_name,file_path='./book/img'):
    #保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    try:
        if not os.path.exists(file_path):
            print '文件夹',file_path,'不存在，重新建立'
            #os.mkdir(file_path)
            os.makedirs(file_path)
        #获得图片后缀
        file_suffix = os.path.splitext(img_url)[1]
        #拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path,os.sep,file_name,file_suffix)
       #下载图片，并保存到文件夹中
        urllib.urlretrieve(img_url,filename=filename)
    except IOError as e:
        print '文件操作失败',e
    except Exception as e:
        print '错误 ：',e
      
'''
def save_img(img_url,file_name,file_path='./book/img'):

    try:
        if not os.path.exists(file_path):
            #print '文件夹', file_path, '不存在，重新建立'
            # os.mkdir(file_path)
            os.makedirs(file_path)
        # 获得图片后缀
        file_suffix = os.path.splitext(img_url)[1]
        # 拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path, os.sep, file_name, file_suffix)
        # 下载图片，并保存到文件夹中
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/35.0.1916.114 Safari/537.36',
            'Cookie': 'AspxAutoDetectCookieSupport=1'
        }
        request = urllib2.Request(img_url, None, header)
        response = urllib2.urlopen(request,timeout=20)
        with open(filename, "wb") as f:
            f.write(response.read())
    except IOError as e:
        print '文件操作失败', e
    except Exception as e:
        print '错误 ：', e


def craw(start,end):
    pn = get_root_info()['page_num']
    print "pagenum:"+str(pn)
    for i in range(start,end+1):
        print "-----------   page:"+str(i)+"   -----------"
        craw_page(i)


# 最开始要调用下面这个函数
#craw(int(sys.argv[1]),int(sys.argv[2]))

def craw_page_daily(page):
    page_url = "http://www.qylbbs4.com/thread/81/" + str(page)
    response = requests.request("GET", page_url)
    fo = open("./page/" + str(page) + ".html", "wb")
    fo.write(response.text)
    fo.close()

    doc = pq(filename="./page/" + str(page) + ".html")

    trs = doc("#J_posts_list tr")

    start = 0
    if (page == 1):
        for tr in trs.items():
            #print tr.text()
            if tr.text() == "普通主题":
                break
            start += 1

    if (page == 1):
        print "start :" + str(start)

    cnt = 0
    flag  = 0 
    for tr in trs.items():
        if flag == 5:
            return 1
        if cnt <= start:
            cnt += 1
            continue
        tr_title = tr(".common")(".title").text()
        links = tr(".common")(".title")("a").items()
        link_url = ""
        for link in links:
            if "read" in link.attr("href"):
                link_url = link.attr("href")
        # print tr_title
        # print link_url

        inp = {}
        inp['title'] = tr_title
        inp['url'] = link_url

        if os.path.exists("./img/"+link_url.split("/")[-1]):
            print link_url.split("/")[-1] + " has been crawed."
            #return 1
	    flag += 1
            cnt += 1
            continue
	#if flag == 5

        try:
            craw_article(inp)
        except:
            print "--"
        cnt += 1

    return 0


def craw_daily():

    while(1):
        download_roothtml()
        root_data = get_root_info()
        page_num = root_data['page_num']
        
        flag = 0
        for i in range(1, int(page_num) + 1):
            print "-----------   page:" + str(i) + "   -----------"
            flag = craw_page_daily(i)
            if flag == 1:
                print "we don't craw and have a rest."
                flag = 0
  		break

        time.sleep(30*60) # sleep 30min

craw_daily()














