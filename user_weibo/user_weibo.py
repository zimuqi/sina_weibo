#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import re
import random
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyquery import PyQuery as pq

"""
这个是获取用户微博数据的文件
"""
driver = webdriver.Firefox()

def createHeader():

    # 多准备点cookies，打开微博的不同页面，吧header里面的cookies复制下来，保存在数组里面
    # 生成不同cookie的请求头信息
    cookies=["SINAGLOBAL=816412848058.1812.1488170163030; _s_tentry=cuiqingcai.com; Apache=1669383924491.2322.1497337670137; ULV=1497337670148:48:8:1:1669383924491.2322.1497337670137:1496891050966; login_sid_t=cf6d0625affae542899e82a32b1378e4; YF-Ugrow-G0=5b31332af1361e117ff29bb32e4d8439; YF-V5-G0=a906819fa00f96cf7912e89aa1628751; SSOLoginState=1497338069; YF-Page-G0=aabeaa17d9557111c805fb15a9959531; SCF=ApERVTSSX2avxuI40xfTwlcitHVQoA-yrvoJ-VETmD2jkrSGO6CsgSsoJCwnpmB_QHXx0UcKDrOAdMVthz3QSJY.; SUHB=0d4_Nt9PLYj_cU; ALF=1528970035; SUB=_2AkMuHXjHf8NxqwJRmP4XzW7nbIh2zw_EieKYQYkcJRMxHRl-yT83qn0HtRDLnrw-H1Mbsl7lRLIJo2VaOP1Yuw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWxWw_emU05ZPWGIa6mP1zQ; WBStorage=5ea47215d42b077f|undefined; UOR=,,www.baidu.com","SINAGLOBAL=816412848058.1812.1488170163030; _s_tentry=cuiqingcai.com; Apache=1669383924491.2322.1497337670137; ULV=1497337670148:48:8:1:1669383924491.2322.1497337670137:1496891050966; login_sid_t=cf6d0625affae542899e82a32b1378e4; YF-Ugrow-G0=5b31332af1361e117ff29bb32e4d8439; YF-V5-G0=a906819fa00f96cf7912e89aa1628751; SSOLoginState=1497338069; YF-Page-G0=aabeaa17d9557111c805fb15a9959531; SCF=ApERVTSSX2avxuI40xfTwlcitHVQoA-yrvoJ-VETmD2jkrSGO6CsgSsoJCwnpmB_QHXx0UcKDrOAdMVthz3QSJY.; SUHB=0d4_Nt9PLYj_cU; ALF=1528970035; SUB=_2AkMuHXjHf8NxqwJRmP4XzW7nbIh2zw_EieKYQYkcJRMxHRl-yT83qn0HtRDLnrw-H1Mbsl7lRLIJo2VaOP1Yuw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWxWw_emU05ZPWGIa6mP1zQ; UOR=,,www.baidu.com; WBStorage=5ea47215d42b077f|undefined"]

    case=random.randint(0,len(cookies)-1)
    headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Host':'weibo.com',
        'Cookie':cookies[case]
    }

    return headers

def getUserWeibo(url):
    """
    抓取微博数据的函数
    :return:
    """
    conn = sqlite3.connect('data/user.db')
    cursor=conn.cursor()

    print u"开始》》》》》》"

    headers=createHeader()
   
    driver.get(url)
    doc = pq(driver.page_source)
    username=doc("h1.username").text()
    # 滚动条到底部函数
    def getPageData(doc,username):
        js = "window.scrollTo(0,document.body.scrollHeight)"
        result=[]
        url=""
        if doc(".W_pages"): 
            if doc('.W_pages .next'):
                doc = pq(driver.page_source)
                # 获取页面
                for wb in doc(".WB_detail").items():
                    item={
                        "username":username,
                        "time":wb(".S_txt2").eq(1).text(),
                        "from":wb(".S_txt2").eq(2).text(),
                        "content":wb(".WB_text").text()
                    }
                    
                    result.append(item)
                     
                url="http://weibo.com{}".format(doc('.W_pages .next').attr("href"))
                # return getUserWeibo(url)
            else:
                driver.execute_script(js)
                doc = pq(driver.page_source)
        else:
            driver.execute_script(js)
            doc = pq(driver.page_source)
            return getPageData(doc,username)

        return result,url


    res=getPageData(doc,username)

    print json.dumps(res)

    fo=open("data/weibo.txt","a+")
    for item in res[0]:
        fo.write("微博名:{}\n发布时间:{}    来源:{}\n微博内容:{}\n\n".format(item["username"].encode("utf-8"),item["time"].encode("utf-8"),item["from"].encode("utf-8"),item["content"].encode("utf-8")))
    fo.close()

    if res[1]:
        return getUserWeibo(res[1])


if __name__ == '__main__':
    url="http://weibo.com/u/1742566624?refer_flag=0000015010_&from=feed&loc=nickname"
    getUserWeibo(url)
    