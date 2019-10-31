# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 21:24:01 2019

@author: lenovo
"""

import requests
import re
import os
import time


def Get_content(site,page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}  #获得响应头
    url = site + page
        response = requests.get(url, headers=headers, verify=False)   #将verify设置为false,会有warning,但是可以避免可能出现的SSLConnectionError
    response.encoding = "gbk"   #此编码格式与你所要爬取的网站的网页源码格式有关，一般是"gbk"（即"gbk2312")、"utf-8"
    
    chapter = None
    words = None
    Next = None
    try:
        chapter=re.search(r'<h1>(?P<content>.*)</h1>',response.text,re.I).groupdict()['content']    #抓取章节标题
        words = re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(?P<content>.*?)[<br />|\n]',response.text)    #抓取章节内容
    except Exception as e:
        print("maybe this book is over .",e)        #有时抓取出错，可能是爬完了，也可能是出错了，总之，此时须退出
        return None
    try:
        Next = re.search(r'<A href="(?P<content>.*)"><img src="http://www.shencou.com/logo/x.gif" alt="下一章"',response.text,re.I).groupdict()['content']
    except Exception as e:
        print("this book is over !",e)
    # 设置小说文件储存位置，如果不存在在该文件夹,则生成该文件夹
    src = r'E:\Python files\爬虫书籍'
    if not os.path.exists(src):
 		  os.makedirs(src)
    filename = '约会大作战.txt'
    # 打开文件夹并且将编码设置成gbk
    f = open(src + '\\' + filename, 'a+', encoding='gbk')

    f.write(chapter + '\n\n')  # 写入章节标题
    for word in words:
        try:
            f.write("    " + word +'\n\n')     #写入章节内容，这里我喜欢两句之间空一行，可以自行更换
        except :
            pass
    f.write('\n\n')
    f.close()   #关闭文件

    return Next


if __name__ == '__main__':     #主函数开始
     
    site = 'http://www.shencou.com/read/0/106/'   #网站上书籍的首页
    page = '4790.html'   #页数，预设第一页
    tem_page = 1
    
    while page:      
        page = Get_content(site,page)  #每次写入一页后，更新下一页
        print(time.asctime(time.localtime()),"the first %d page"%(tem_page))  #显示目前状态
        tem_page += 1
 #       time.sleep(0.1)        #延迟响应0.1秒防止浏览过快被封ip
