# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 19:35:50 2019

@author: lenovo
"""

import requests
import re
import os
import time
import sys
import threading


Stop_flag = False
download = 0
Words =[]
Code = 'gbk'
    
class Thread_Download(threading.Thread):
    
    def __init__(self,website):
        threading.Thread.__init__(self)
        self.Website = website
        
    def run(self):
        global Code,download,Stop_flag,Words
        src = re.findall(r'^(.*)/(.*)\.html',self.Website)
        site = src[0][0] +'/'
        page = src[0][1] + '.html'
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}  #获得响应头
        response = requests.get(self.Website, headers=headers)
        response.encoding = Code
        if not re.findall('gbk',response.text):
            Code = 'utf-8'
        
        while not Stop_flag:
            print(self.Website)
            response = requests.get(self.Website, headers=headers)
            response.encoding = Code
            try:
                chapter=re.search(r'<h1.*>(?P<content>.*)</h1>',response.text,re.I).groupdict()['content']    #抓取章节标题
                words = []
                words.append(chapter)
                words.extend(re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(?P<content>.*?)[<\n]',response.text))   #抓取章节内容
            except :
                print("maybe this book is over .")        #可能是爬完了，也可能是出错了，总之，此时须退出
                Stop_flag = True
                return
            Words.append(words)
            download += 1
            print("第 %d 页------------------------------已经爬取完成。"%(download))
            try:
                page = re.search(r'(章节列表|章节目录|目录).*?<[/a-z;&> ]*?href([^\n下]*/|=")(?P<content>.*?)">下',response.text,re.I|re.S).groupdict()['content']   #抓取下一页信息
            except :
                print("this book is over !")
                Stop_flag = True
                return
            if site + page == self.Website:
                Stop_flag = True
            else:
                self.Website = site + page
        
class Thread_Extract(threading.Thread):
    
    def __init__(self,Path):
        threading.Thread.__init__(self)
        self.Path = Path
        
    def run(self):
        global Code,download,Stop_flag,Words
        while not download and Stop_flag==False :
            pass
        
        f = open(self.Path, 'a+', encoding=Code)
        
        Extract = 0
        while not Stop_flag or Words:
            if not Words and not Stop_flag:
                time.sleep(0.5)
                continue
            for word in Words[0]:
                try:
                    f.write('    ' + word +'\n\n')     #写入每页内容，这里我喜欢两句之间空一行，可以自行更换
                except :
                    pass
            f.write('\n\n')
            del Words[0]
            Extract += 1
            print("第 %d 页******************************已经写入完成。"%(Extract))
        
        f.close()   #关闭文件


if __name__ == '__main__':     #主函数开始
    
    if sys.argv.__len__()>2:		#若参数个数大于2
        website = sys.argv[1]
        Path = sys.argv[2]
    else:
        print('未给出参数（书籍第一页的网址、书籍在本地保存的地址),程序退出。')
        sys.exit(0)
    
    src = re.findall(r'^(.*)\\(.*)\.txt',Path)
    if src and not os.path.exists(src[0][0]):
        os.makedirs(src[0][0])
    
    t1 = Thread_Download(website)
    t2 = Thread_Extract(Path)
    
    start = time.time()
    t1.start()
    t2.start()
    
    t2.join()
    cost = time.time() - start
    size = os.path.getsize(Path)/1000
    print('This book has been crawled,whose size is %.2f KB .It takes %.1f seconds.Your download speed is %.2f KB/s .'%(size,cost,size/cost))

