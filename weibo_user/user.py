#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import re
import random
import sqlite3
import time
import threading

"""
这个是比较暴力一点的方法去枚举用户，没有去重。
"""


def createUrlHeader(i):

    # 多准备点cookies，打开微博的不同页面，吧header里面的cookies复制下来，保存在数组里面
    cookies=["SINAGLOBAL=816412848058.1812.1488170163030; _s_tentry=cuiqingcai.com; Apache=1669383924491.2322.1497337670137; ULV=1497337670148:48:8:1:1669383924491.2322.1497337670137:1496891050966; login_sid_t=cf6d0625affae542899e82a32b1378e4; YF-Ugrow-G0=5b31332af1361e117ff29bb32e4d8439; YF-V5-G0=a906819fa00f96cf7912e89aa1628751; SSOLoginState=1497338069; YF-Page-G0=aabeaa17d9557111c805fb15a9959531; SCF=ApERVTSSX2avxuI40xfTwlcitHVQoA-yrvoJ-VETmD2jkrSGO6CsgSsoJCwnpmB_QHXx0UcKDrOAdMVthz3QSJY.; SUHB=0d4_Nt9PLYj_cU; ALF=1528970035; SUB=_2AkMuHXjHf8NxqwJRmP4XzW7nbIh2zw_EieKYQYkcJRMxHRl-yT83qn0HtRDLnrw-H1Mbsl7lRLIJo2VaOP1Yuw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWxWw_emU05ZPWGIa6mP1zQ; WBStorage=5ea47215d42b077f|undefined; UOR=,,www.baidu.com","SINAGLOBAL=816412848058.1812.1488170163030; _s_tentry=cuiqingcai.com; Apache=1669383924491.2322.1497337670137; ULV=1497337670148:48:8:1:1669383924491.2322.1497337670137:1496891050966; login_sid_t=cf6d0625affae542899e82a32b1378e4; YF-Ugrow-G0=5b31332af1361e117ff29bb32e4d8439; YF-V5-G0=a906819fa00f96cf7912e89aa1628751; SSOLoginState=1497338069; YF-Page-G0=aabeaa17d9557111c805fb15a9959531; SCF=ApERVTSSX2avxuI40xfTwlcitHVQoA-yrvoJ-VETmD2jkrSGO6CsgSsoJCwnpmB_QHXx0UcKDrOAdMVthz3QSJY.; SUHB=0d4_Nt9PLYj_cU; ALF=1528970035; SUB=_2AkMuHXjHf8NxqwJRmP4XzW7nbIh2zw_EieKYQYkcJRMxHRl-yT83qn0HtRDLnrw-H1Mbsl7lRLIJo2VaOP1Yuw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWxWw_emU05ZPWGIa6mP1zQ; UOR=,,www.baidu.com; WBStorage=5ea47215d42b077f|undefined"]

    # 生成不同cookie的请求头信息
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
    url="http://weibo.com/u/{}".format(i)
    return url,headers

def resolvePage(*args):
    """
    抓取数据的函数
    :param args: 用户ID的取值范围[start,end]
    :return:
    """
    conn = sqlite3.connect('data/user.db')
    cursor=conn.cursor()
    if args:
        start=args[0]
        end=args[1]
    else:
        # 默认范围
        start = 1000000000
        end = 9000000000

    print start,end

    for rank in range(1,1000000):
        try:
            id=random.randint(start,end)
            info=list(createUrlHeader(id))
            # info[0]="http://weibo.com/u/5454806466?from=feed&loc=nickname&is_hot=1"
            req=requests.get(info[0],headers=info[1])

            if req.content.find("$CONFIG")==-1:
                print u"页面不存在"
                pass
            else:
                print u"页面存在"
                # reg1=re.compile('class=\\"username\\">(.*?)<')
                reg1=re.compile('"username\\\\">(.*?)<.{2}h1>')
                reg2=re.compile('"W_f\d{2}.*?(\d+)<./strong')
                reg3=re.compile('&tag=.*?">(.*?)<./a>')

                name=re.findall(reg1,req.content)
                num=re.findall(reg2,req.content)
                tag=re.findall(reg3,req.content)

                if name and num:
                    sql=""
                    item={
                        "uid":id,
                        "name":name[0],
                        "foucs":num[0],
                        "fan":num[1],
                        "weibo_num":num[2]
                    }
                    if tag:
                        str=[]
                        for each in tag:
                            str.append(each)
                        tags="、".join(str)
                        item["tag"]=tags

                        sql = "INSERT INTO user (`uid`,`name`,`focus`,`fans`,`weibo_num`,`tag`) VALUES ('{}','{}','{}','{}','{}','{}')".format(item["uid"], item["name"], item["foucs"], item["fan"], item["weibo_num"],item["tag"])
                    else:
                        sql="INSERT INTO user (`uid`,`name`,`focus`,`fans`,`weibo_num`) VALUES ('{}','{}','{}','{}','{}')".format(item["uid"],item["name"],item["foucs"],item["fan"],item["weibo_num"])

                    print item
                    cursor.execute(sql)
                    conn.commit()
                    time.sleep(1)
        except:
            print u"页面不存在",rank
    conn.close()

if __name__ == '__main__':
    resolvePage()
    # resolvePage(1000000000,2000000000)   # 单线程爬取
    # resolvePage(2000000001,3000000000)   # 单线程爬取
    # resolvePage(3000000001,4000000000)   # 单线程爬取
    # resolvePage(4000000001,5000000000)   # 单线程爬取
    # resolvePage(5000000001,6000000000)   # 单线程爬取
    # resolvePage(6000000001,7000000000)   # 单线程爬取
    # resolvePage(7000000001,8000000000)   # 单线程爬取
    # resolvePage(8000000001,9999999999)   # 单线程爬取
    # def multithreading(threadingNum):
    #     """
    #     多线程爬取
    #     :param threadingNum: 线程数
    #     :return:
    #     """
    #     threads = []
    #     rang = 9999999999   #用户ID的最大值
    #     sp = int(rang/(threadingNum))   #每个线程用户的间隔
    #
    #     for index in range(1,threadingNum+1):
    #         start=index*sp
    #         end=start+sp
    #         spider= threading.Thread(target=resolvePage, args=(start,end,))
    #         threads.append(spider)
    #     i=1
    #     for t in threads:
    #         t.setDaemon(True);
    #         t.start()
    #         print u"线程",i,u"启动"
    #         i+=1
    #
    #
    # multithreading(2)