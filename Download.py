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
Responses =[]
Code = 'gbk'
    
class Thread_Download(threading.Thread):
    
    def __init__(self,website):
        threading.Thread.__init__(self)
        self.Website = website
        
    def run(self):
        global Code,download,Stop_flag,Responses
        src = re.findall(r'^(.*)/(.*)\.html',self.Website)
        site = src[0][0] +'/'
        page = src[0][1] 
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}  #获得响应头
        response = requests.get(self.Website, headers=headers)
        response.encoding = Code
        if not re.search('gb[k2]',response.text,re.I):
            Code = 'utf-8'
        oldresponse = None
        while not Stop_flag:
            print(self.Website)
            while True:
                try:
                    response = requests.get(self.Website, headers=headers, timeout = 2)
                except:
                    try:
                        page = re.search(r'href(.*/|=")(?P<content>.*?)\.html".*?下一(页|章|回)',oldresponse.text,re.I).groupdict()['content']   #抓取下一页信息
                    except :
                        print("this book is over !")
                        Stop_flag = True
                        return     
                    if len(page) > 10 :
                        print("抱歉，目前暂不支持对该网站的解码，无法自动翻页。")
                        Stop_flag = True
                        return
                    self.Website = site + page + '.html'
                else:
                    break
            response.encoding = Code
            Responses.append(response)
            download += 1
            oldresponse = response
            print("第 %d 页------------------------------已经爬取完成。"%(download))
            try:
                page = int(page)
            except:
                page = re.search(r'href(.*/|=")(?P<content>.*?)\.html".*?下一(页|章|回)',response.text,re.I).groupdict()['content']
            else:
                page = str(page + 1)
            self.Website = site + page + '.html'
        
class Thread_Extract(threading.Thread):
    
    def __init__(self,Path):
        threading.Thread.__init__(self)
        self.Path = Path
        
    def run(self):
        global Code,download,Stop_flag,Responses
        while not download and Stop_flag==False :
            time.sleep(0.8)
        
        f = open(self.Path, 'a+', encoding=Code)
        
        Extract = 0
        while not Stop_flag or Responses:
            if not Responses and not Stop_flag:
                time.sleep(0.5)
                continue

            response = Responses[0]
            try:
                chapter=re.search(r'<h1.*>(?P<content>.*)</h1>',response.text,re.I).groupdict()['content']    #抓取章节标题
                words = []
                words.append(chapter)
                words.extend(re.findall(r'&nbsp;&nbsp;&nbsp;&nbsp;(?P<content>.*?)[<\n]',response.text))   #抓取章节内容
            except :
                pass
            for word in words:
                try:
                    f.write('    ' + word +'\n\n')     #写入每页内容，这里我喜欢两句之间空一行，可以自行更换
                except :
                    pass
            f.write('\n\n')
            del Responses[0]
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
    print('This book has been crawled.Its size is %.2f KB .It takes %.1f seconds.Your download speed is %.2f KB/s .'%(size,cost,size/cost))

