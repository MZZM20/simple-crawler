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
        try:    
            site = src[0][0] +'/'
            page = src[0][1] 
        except:
            print('所给书籍网址格式错误。')
            Stop_flag = True
            return
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}  #获得响应头
        try:
            response = requests.get(self.Website, headers=headers)
        except:
            Stop_flag = True
            print('连接服务器失败。请检查网络是否连接或所给网站可否访问。')
            return
        response.encoding = Code
        if not re.search('gb[k2]',response.text,re.I):
            Code = 'utf-8'
        oldresponse = None
        MaxReConnection = 15
        PageTurningMode = False
        while not Stop_flag:
            print(self.Website)
            while MaxReConnection:
                try:
                    MaxReConnection -= 1
                    response = requests.get(self.Website, headers=headers, timeout = 2)
                    if response.status_code == 404 and not PageTurningMode:
                        page = Intelligentpageturning(oldresponse)
                        PageTurningMode = True
                        self.Website = site + page + '.html'
                        continue
                    if response.status_code == 404 and PageTurningMode:
                        Stop_flag = True
                        return
                except:
                    if Stop_flag :
                        return
                    print('连接超时。正在尝试重连……')
                else:
                    MaxReConnection = 15
                    break
            else:
                print('该网站可能屏蔽掉本机IP，请下次从中断处继续下载。')
                
            response.encoding = Code
            Responses.append(response)
            download += 1
            oldresponse = response
            print("第 %d 页------------------------------已经爬取完成。"%(download))
            try:
                page = int(page)
            except:
                page = Intelligentpageturning(response)
                PageTurningMode = True
            else:
                page = str(page + 1)
                PageTurningMode = False
            if site + page + '.html' == self.Website:
                print("书籍已爬取完毕。")
                Stop_flag = True
            else:
                self.Website = site + page + '.html'
        
class Thread_Extract(threading.Thread):
    
    def __init__(self,Path):
        threading.Thread.__init__(self)
        self.Path = Path
        
    def run(self):
        global Code,download,Stop_flag,Responses
        while not download and Stop_flag==False :
            time.sleep(0.25)
        
        f = open(self.Path, 'a+', encoding=Code)
        
        Extract = 0
        while not Stop_flag or Responses:
            if not Responses:
                time.sleep(0.1)
                continue

            response = Responses[0]
            try:
                chapter=re.search(r'<h1.*?>(?P<content>.*)</h1>',response.text,re.I).groupdict()['content']    #抓取章节标题
                words = []
                words.append((None,chapter))
                words.extend(re.findall(r'(&nbsp;|<br />)+(.*?)(<br />|&amp;)',response.text,re.S))   #抓取章节内容
            except :
                pass
            for word in words:
                try:
                    f.write('    ' + word[1] +'\n')     #写入每页内容
                except :
                    pass
            f.write('\n\n')
            del Responses[0]
            Extract += 1
            print("第 %d 页******************************已经写入完成。"%(Extract))
        
        f.close()   #关闭文件


def Intelligentpageturning(response):
    global Stop_flag
    try:
        page = re.search(r'href(.*/|=")(?P<content>.*?)\.html".*?下一(页|章|回)',response.text,re.I).groupdict()['content']   #抓取下一页信息
    except :
        print("检索到当前页面无下一页链接，书籍可能已经爬取完毕。")
        Stop_flag = True
        return None
    return page



if __name__ == '__main__':     #主函数开始
    
    if sys.argv.__len__()>2:		#若参数个数大于2
        website = sys.argv[1]
        Path = sys.argv[2]
    else:
        print('未给出参数（书籍第一页的网址、书籍在本地保存的地址),程序退出。')
        sys.exit(0)
    
    src = re.findall(r'^(.*)\.txt',Path)
    if not src:
        print('所给书籍保存地址格式错误。')
        sys.exit(0)
    t1 = Thread_Download(website)
    t2 = Thread_Extract(Path)
    
    start = time.time()
    t1.start()
    t2.start()
    
    t2.join()
    cost = time.time() - start
    size = os.path.getsize(Path)/1024
    print('This book has been crawled.Its size is %.2f KB .It takes %.1f seconds.Your download speed is %.2f KB/s .'%(size,cost,size/cost))

