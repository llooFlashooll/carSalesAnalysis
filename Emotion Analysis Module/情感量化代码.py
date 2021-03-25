# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 14:40:50 2019

@author: Lovecraft.Qiu
"""
#加载百度AI平台--------------------------------------------------------------------------------------------------------------------------
from aip import AipNlp 
APP_ID = '17846093'                             #登录账号
API_KEY = 'uASrIE7Dlx7kG7zekm4AQBKG'            #平台密匙
SECRET_KEY = '46FcvZsoZWVistqXqeypXPxWiu8zOj9s' #登录密码
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

#加载词典--------------------------------------------------------------------------------------------------------------------------------
import pandas as pd
def readExcelFile(filename): 
    data = pd.DataFrame(pd.read_excel(filename))
    return data
positive_adj=list(readExcelFile(r'.\adj.xlsx')['positive_adj'])     #正向情感形容词词典
negative_adj=list(readExcelFile(r'.\adj.xlsx')['negative_adj'])     #负面情感形容词词典
negative_adv=list(readExcelFile(r'.\否定adv.xlsx')['negative_adv']) #否定副词词典
degree_adv1=list(readExcelFile(r'.\程度adv.xlsx')['extreme'])       #极端程度副词词典
degree_adv2=list(readExcelFile(r'.\程度adv.xlsx')['very'])          #非常程度副词词典
degree_adv3=list(readExcelFile(r'.\程度adv.xlsx')['kindof'])        #有点程度副词词典
degree_adv4=list(readExcelFile(r'.\程度adv.xlsx')['alittlebit'])    #略微程度副词词典
positive_v=list(readExcelFile(r'.\verb.xlsx')['positive'])          #正向情感动词词典
negative_v=list(readExcelFile(r'.\verb.xlsx')['negative'])          #负面情感动词词典

 
#评分函数--------------------------------------------------------------------------------------------------------------------------------
def adv(word,mark,a,b,c,d,e,av):#mark为评论的情感计分值，a,b,c,d,e分别为五类副词的权重分值，av为储存未找到的副词的list
    if word in degree_adv1: 
        mark+=a
        print('adv:',word)
    elif word in degree_adv2:
        mark+=b
        print('adv:',word)
    elif word in degree_adv3:
        mark+=c
        print('adv:',word)
    elif word in degree_adv4: 
        mark+=d
        print('adv:',word)
    elif word in negative_adv: 
        mark+=e
        print('adv:',word)
    else:
        print('未找到adv:',word)#输出未找到的副词
        av.append(word)
    return mark
def getscore(dt,v,adj,av):#dt为依存句法分析结果，v为储存未找到的动词的list，adj为储存未找到的形容词的list，av为储存未找到的副词的list
    mark=0
    for i in range(len(dt['items'])):
        #adv+adj得分：
        if dt['items'][i]['postag']=='a':
            if dt['items'][i]['word'] in positive_adj:
                print('adj+:',dt['items'][i]['word']) 
                if (dt['items'][i-1]['deprel']=='ADV') and (dt['items'][i-1]['postag']=='d'):#adj.左侧词为副词且为左依赖关系
                    mark=adv(dt['items'][i-1]['word'],mark,2,1.2,0.8,0.3,-1,av)
                else:
                    mark+=1
            elif dt['items'][i]['word'] in negative_adj:
                print('adj-:',dt['items'][i]['word'])
                if(dt['items'][i-1]['deprel']=='ADV')and(dt['items'][i-1]['postag']=='d'):#adj.左侧词为副词且为左依赖关系
                    mark=adv(dt['items'][i-1]['word'],mark,-2,-1.2,-0.8,-0.3,1,av)
                else:
                    mark-=1
            else:
                print('未找到adj.:',dt['items'][i]['word'])#输出未找到的形容词
                adj.append(dt['items'][i]['word'])
        #adv.+v.&adv.+adv.+v.得分
        if dt['items'][i]['postag']=='v':
            if dt['items'][i]['word'] in positive_v:
                print('v+:',dt['items'][i]['word'])
                if dt['items'][i-1]['deprel']=='ADV' and dt['items'][i-1]['postag']=='d':#动词左侧词为副词且为左依赖关系
                    if dt['items'][i-1]['word'] in degree_adv1: 
                        mark+=2
                    elif dt['items'][i-1]['word'] in degree_adv2: 
                        mark+=1.2
                    elif dt['items'][i-1]['word'] in degree_adv3:
                        mark+=0.8
                    elif dt['items'][i-1]['word'] in degree_adv4: 
                        mark+=0.3
                    elif dt['items'][i-1]['word'] in negative_adv: 
                        if dt['items'][i-2]['deprel']=='ADV' and dt['items'][i-2]['postag']=='d':#动词左侧词为副词且为左依赖关系
                            mark=adv(dt['items'][i-2]['word'],mark,-2,-1.2,-0.8,-0.3,1,av)
                        else:
                            mark-=1
                else:
                    mark+=1   
            elif dt['items'][i]['word'] in negative_v:
                print('v-:',dt['items'][i]['word'])
                if dt['items'][i-1]['deprel']=='ADV' and dt['items'][i-1]['postag']=='d':#adj.左侧词为副词且为左依赖关系
                    mark=adv(dt['items'][i-1]['word'],mark,-2,-1.2,-0.8,-0.3,1,av)
                else:
                    mark-=1
            else:
                print('未找到v.:',dt['items'][i]['word'])#输出未找到的动词
                v.append(dt['items'][i]['word'])
    return mark

# 加载评论--------------------------------------------------------------------------------------------------------------------------------
Comments=readExcelFile(r'.\第二批评论\途观.xlsx')
vehicle=Comments['车型']
Commenttime_=list(Comments['评论时间'])
Commenttime=[]
for time in Commenttime_:
    Commenttime.append(str(time))#将EXCEL时间日期格式转换为字符串

#创建评分结果EXCEL文件---------------------------------------------------------------------------------------------------------------------
import xlwt  
class WriteExcel():
    def __init__(self,path):
        self.path=path
        self.file=xlwt.Workbook() 
        self.table = self.file.add_sheet('Sheet 1',cell_overwrite_ok=True)
    def writerow(self,rownum,startcolumn,s):#写行函数
        for i in range(len(s)):
            self.table.write(rownum-1,i+startcolumn-1,s[i])
        self.file.save(self.path)
    def writecolumn(self,columnnum,startrow,s):#写列函数
        for i in range(len(s)):
            self.table.write(i+startrow-1,columnnum-1,s[i])
        self.file.save(self.path)
 
File=WriteExcel(r'.\情感量化结果\途观.xls')
row0=['车型','评论时间','空间','动力','操控','能耗','舒适性','外观','内饰','性价比']
File.writerow(1,1,row0)
File.writecolumn(1,2,vehicle)
File.writecolumn(2,2,Commenttime)


#依存句法分析及计算评分，并将结果写入Excel文件------------------------------------------------------------------------------------------------
import time
columnnum=3                                                  #初始化写EXCEL时的起始列
adj=[] #字典里未找到的形容词
v=[] #字典里未找到的动词
av=[] #字典里未找到的副词
keywords=['空间','动力','操控','能耗','舒适性','外观','内饰','性价比']
for keyword in keywords:                                     #按指标关键词读取各条评论
    print(keyword,':')
    comment=Comments[keyword]
    score=[]                                                 #用于放置该关键词下的每条评论的分值
    for i in range(len(comment))
        time.sleep(1)                                        #暂停1秒避免百度平台调用频率超限额
        dt = client.depParser(comment[i])
        if 'error_code' not in dt:                           #若平台的引用没有发生错误
            if dt['items'][0]['word']=='无':                 #无评论条目
                print('第',i+1,'条：No comments')
                score.append('None')
            else:
                print('第',i+1,'条评论:',comment[i])         #输出该评论
                print(dt)                                    #输出依存句法分析结果
                score.append(getscore(dt,v,adj,av))
        else:
            score.append('平台调用失败')
    print('得分:',score)
    File.writecolumn(columnnum,2,score)
    columnnum+=1                                             #挪到EXCEL下一列
print('未找到的动词:',v)
print('未找到的形容词:',adj)
print('未找到的副词:',av)
Filenotfound=WriteExcel(r'.\未找到的词.xls')
row0=['v','adj','adv']
Filenotfound.writerow(1,1,row0)
Filenotfound.writecolumn(1,2,v)
Filenotfound.writecolumn(2,2,adj)
Filenotfound.writecolumn(3,2,av)