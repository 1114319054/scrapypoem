from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve
from random import randint
import re
import csv
import os
import socket
import time

baseUrl="http://so.gushiwen.org"
poemNum=0
mingjuNum=0
authorNum=0
timeout=20
socket.setdefaulttimeout(timeout)
sleep_download_time=20

def getPoem(poemUrl):
    html=safeopen(poemUrl)
    bsObj=BeautifulSoup(html,"html.parser")
    poem=bsObj.find("div",{"id":"cont"})
    title=bsObj.find("h1")
    types=bsObj.find("div",{"class":"shisonconttag"}).findAll("a",href=re.compile("^(/type)"))
    author=bsObj.find("a",href=re.compile("^(/author_)"))
    if poem:
        words=poem.get_text().replace(u'\xa0',u' ')
    if author:
        author=author.get_text().replace(u'\xa0',u' ')
    if title:
        title=title.get_text().replace(u'\xa0',u' ')
    if types:
        for i in range(len(types)):
            types[i]=types[i].get_text().replace(u'\xa0',u' ')
    csvRow=[title,author,words]
    for t in types:
        csvRow.append(t)
    try:
        poemWriter.writerow(csvRow)
        global poemNum
        poemNum=poemNum+1
    except Exception as e:
        print(e)

def getAuthor(authorUrl):
    html=safeopen(authorUrl)
    bsObj=BeautifulSoup(html,"html.parser")
    name=bsObj.find("h1")
    if name:
        name=name.get_text().replace(u'\xa0',u' ')
    intro=bsObj.find("div",{"class":"shileft"}).find("div",{"class":"son2"})
    if intro:
        intro=intro.get_text().replace(u'\xa0',u' ')
    csvRow=[name,intro]
    try:
        authorWriter.writerow(csvRow)
        global authorNum
        authorNum=authorNum+1
    except Exception as e:
        print(e)
    finally:
        img=bsObj.find("div",{"class":"shileft"}).find("div",{"class":"son2"}).find("img")
        if img:
            imgLocation=img.attrs['src']
            imgName=img.attrs['alt']
            urlretrieve(imgLocation,"authPic/"+imgName+".jpg")

def getMingju(mingjuUrl):
    global authorList
    global poemList
    global newauthor
    html=safeopen(mingjuUrl)
    bsObj=BeautifulSoup(html,"html.parser")
    word=bsObj.find("h1")
    if word:
        word=word.get_text().replace(u'\xa0',u' ')
    intro=bsObj.find("a",href=re.compile("^(/view_)"))
    if intro:
        poem=intro.get_text().replace(u'\xa0',u' ')
        intro=intro.attrs["href"]
        if intro+"\n" not in poemList:
            poemFile.write(intro+"\n")
            poemList.append(intro+"\n")
            getPoem(intro)
    aut=bsObj.find("div",{"class":"shileft"}).find("div",{"class":"son2"}).find("a",href=re.compile("^(/author_)"))
    author=""
    if aut:
        author=aut.get_text().replace(u'\xa0',u' ')
        aut=aut.attrs["href"]
        if aut+"\n" not in authorList:
            authorFile.write(aut+"\n")
            authorList.append(aut+"\n")
            getAuthor(aut)
    print(word)
    csvRow=[word,author,poem]
    try:
        mingjuWriter.writerow(csvRow)
        global mingjuNum
        mingjuNum=mingjuNum+1
    except Exception as e:
        print(e)

def getLink(linkUrl):
    global mingjuList
    global linkList
    html=safeopen(linkUrl)
    bsObj=BeautifulSoup(html,"html.parser")
    mingjus=bsObj.findAll("a",href=re.compile("^(/mingju/ju_)"))
    if len(mingjus)>0:
        for eachmingju in mingjus:
            mingju=eachmingju.attrs['href']
            if mingju+"\n" not in mingjuList:
                mingjuFile.write(mingju+"\n")
                mingjuList.append(mingju+"\n")
                getMingju(mingju)
    links=bsObj.findAll("a",href=re.compile("^(/mingju/Default)"))
    links2=bsObj.findAll("a",href=re.compile("^(Default)"))
    if len(links)>0:
        for eachlink in links:
            if len(linkList)>size:
                break
            link=eachlink.attrs['href']
            if link+"\n" not in linkList:
                linkFile.write(link+"\n")
                linkList.append(link+"\n")
                getLink(link)
    if len(links2)>0:
        for eachlink in links2:
            if len(linkList)>size:
                break
            link="/mingju/"+eachlink.attrs['href']
            if link+"\n" not in linkList:
                linkFile.write(link+"\n")
                linkList.append(link+"\n")
                getLink(link)
    

def safeopen(Url):
    try:
        html=urlopen(baseUrl+Url)
    except Exception as e:
        print(e)
        global poemFile
        global mingjuFile
        global authorFile
        global poemFile2
        global mingjuFile2
        global authorFile2
        global linkFile
        global sleep_download_time
        global authorList
        global poemList
        global mingjuList
        global linkList
        global poemWriter
        global mingjuWriter
        global authorWriter
        poemFile.close()
        authorFile.close()
        mingjuFile.close()
        linkFile.close()
        poemFile2.close()
        authorFile2.close()
        mingjuFile2.close()
        time.sleep(sleep_download_time)
        mingjuFile=open("list/mingjuList.txt","a+")
        mingjuFile.seek(0)
        mingjuList=mingjuFile.readlines()
        authorFile=open("list/authorList.txt","a+")
        authorFile.seek(0)
        authorList=authorFile.readlines()
        poemFile=open("list/poemList.txt","a+")
        poemFile.seek(0)
        poemList=poemFile.readlines()
        linkFile=open("list/linkList.txt","a+")
        linkFile.seek(0)
        linkList=linkFile.readlines()
        poemFile2=open("csv/poems.csv","a+",newline='',encoding="gbk",errors='ignore')
        poemWriter=csv.writer(poemFile2)
        authorFile2=open("csv/authors.csv","a+",newline='',encoding="gbk",errors='ignore')
        authorWriter=csv.writer(authorFile2)
        mingjuFile2=open("csv/mingjus.csv","a+",newline='',encoding="gbk",errors='ignore')
        mingjuWriter=csv.writer(mingjuFile2)
        html=urlopen(baseUrl+Url)
    return html

if not os.path.exists("list"):
    os.makedirs("list")
if not os.path.exists("csv"):
    os.makedirs("csv")
mingjuFile=open("list/mingjuList.txt","a+")
mingjuFile.seek(0)
mingjuList=mingjuFile.readlines()
authorFile=open("list/authorList.txt","a+")
authorFile.seek(0)
authorList=authorFile.readlines()
poemFile=open("list/poemList.txt","a+")
poemFile.seek(0)
poemList=poemFile.readlines()
linkFile=open("list/linkList.txt","a+")
linkFile.seek(0)
linkList=linkFile.readlines()
print(len(linkList))
size=len(linkList)+100
print(size)
poemFile2=open("csv/poems.csv","a+",newline='',encoding="gbk",errors='ignore')
poemWriter=csv.writer(poemFile2)
authorFile2=open("csv/authors.csv","a+",newline='',encoding="gbk",errors='ignore')
authorWriter=csv.writer(authorFile2)
mingjuFile2=open("csv/mingjus.csv","a+",newline='',encoding="gbk",errors='ignore')
mingjuWriter=csv.writer(mingjuFile2)
try:
    if not os.path.exists("authPic"):
        os.makedirs("authPic")
    if linkList:
        links=[link.replace("/n","") for link in linkList]
        for link in links:
            getLink(link)
    else:
        getLink("/mingju/")
except Exception as e:
    print(e)
finally:
    poemFile.close()
    authorFile.close()
    mingjuFile.close()
    linkFile.close()
    poemFile2.close()
    authorFile2.close()
    mingjuFile2.close()
    print("input "+str(mingjuNum)+" mingjus, total get "+str(len(mingjuList)))
    print("input "+str(authorNum)+" authors, total get "+str(len(authorList)))
    print("input "+str(poemNum)+" poems, total get "+str(len(poemList)))
