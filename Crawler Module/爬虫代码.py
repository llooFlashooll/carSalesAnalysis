# -*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import os

infoL1=[]
infoL2=[]
ft1=''
ft2=''
# 从爬取的HTML文件中获取相关分类的得分
def get_score(str1, name):
    str1 = str1.strip('\n')
    str1 = str1.strip(name)
    str1 = str1.strip('\n')
    return str1


# 将页面拆解成多个评论
def get_comments_in_page(soup_x, total_list):
    for comment_list in soup_x.find_all("div", class_='mouthcon'):
        comment_detail = get_details_of_comment(comment_list, spider=spider)


# 获取用户性别
def get_user_gender(spider2, url):
    spider2.get(url + '/info')
    deal_the_page(spider2)
    soup = BeautifulSoup(spider2.page_source)
    gender = soup.find('div', class_='uData')
    if gender:
        list1 = gender.find_all('p')
        gender = ''
        place=''
        birth=''
        for p in list1:
            if '性别' in p.text:
                gender = p.text.replace('\n', '')
            if '所在地' in p.text:
                place = p.text.replace('\n', '')
            if '生日' in p.text:
                birth=p.text.replace('\n', '')
        return [gender,place,birth]


# 将一条评论拆解成多个部分，并存储起来
def get_details_of_comment(comment, spider):
    reviewL=[]
    find_location = comment.find_all("dl", class_='choose-dl')
    for dl in find_location:
        if "购买地点" in dl.text:
            reviewL.append(dl.text.replace('\n', '').replace(' ', '').strip('购买地点'))

        if "油耗" in dl.text:
            text1=dl.text.replace('\n', '').replace(' ', '').strip('油耗')
            if '目前行驶' in text1:
                text1=text1.strip('目前行驶').split('公里')[0]+'公里'
            reviewL.append(text1)
        
        if "购车目的" in dl.text:
            reviewL.append(dl.text.replace('\n', '').strip('购车目的'))

        if "购买车型" in dl.text:
            reviewL.append(dl.text.replace('\n', '').strip('购买车型'))
        
    reviewL.append(comment.find("div", class_='title-name name-width-01').text.replace('\n', '').replace(' ', ''))
    reviewL.append(comment.find("div", class_='name-text').text.replace('\n', '').replace(' ', ''))
    userLink='http:'+ comment.find("div", class_='name-text').p.a['href']

    reviewL.append(userLink)
    userL=get_user_gender(spider, userLink)
    if userL:
        reviewL=reviewL+userL
    try:
        reviewL.append(comment.find("div", class_='text-con').div.text.replace('\n', '').replace(' ', ''))
    except:
        pass
    reviews='\t'.join(reviewL)
    if reviews not in infoL1:
        with open(ft1,'a',encoding='utf-8') as ftw1:
            ftw1.write(reviews+'\n')

    return reviews


# 将页面的所有信息显示出来
def deal_the_page(spider1):
    try:
        spider1.find_element_by_xpath('//div[@class="step01"]/a[@class="close"]')
        spider1.find_element_by_xpath('//div[@class="step01"]/a[@class="close"]').click()
    except:
        pass
    click_list = spider1.find_elements_by_xpath(
        "//div[@class='mouthcon']//a[@class='btn btn-small fn-left js-showmessage']")
    for a in click_list:
        a.click()
        time.sleep(0.5)


# 通过一个车的车辆编码，获取相关的所有评论数据
def get_review_data(car_code, spider):
    spider.get('http://k.autohome.com.cn/' + car_code + '/###')
    #http://k.autohome.com.cn/197/###
    deal_the_page(spider)
    soup = BeautifulSoup(spider.page_source)
    total_comment_list = list()
    get_comments_in_page(soup, total_comment_list)
    loop_count = 1
    for a in range(2, 11):
        url = 'http://k.autohome.com.cn/' + car_code + '/index_' + str(a) + '.html###'
        time.sleep(5)
        spider.get(url)
        deal_the_page(spider)
        soup1 = BeautifulSoup(spider.page_source)
        get_comments_in_page(soup1, total_comment_list)
        loop_count += 1
    return total_comment_list



# 加载 Webdriver
#spider = webdriver.Chrome('C:/Program Files (x86)/Chromedriver/chromedriver.exe')
spider = webdriver.Chrome()
spider.get('http://account.autohome.com.cn/login')
spider.find_element_by_class_name("tab-account").click()
user = spider.find_element_by_id('UserName')
user.send_keys('usernamexxx')
password = spider.find_element_by_id('PassWord')
psswrd='password666'
password.send_keys(psswrd)
# 休眠20秒的时间，以防出现需手动输入验证码的情况。如出现验证码，要在20秒内在浏览器内人工输入
time.sleep(20)
try:
    spider.find_element_by_id("check_submitpassword").click()
    login = spider.find_element_by_css_selector('#SubmitPhoneLogin')
    login.click()
    time.sleep(5)
except:
    pass
# 自己可以更改为自己感兴趣的汽车编号，这里65是宝马5系，197是奔驰E级，仅作测试和参考
car_code_list = ['3977']
# 获取并存储数据，论坛数据会被存储在car_code_luntan.json中，评价数据会被存储在car_code.json中
for car_code in car_code_list:
    print('We are working on car' + car_code)
    ft1=car_code+'购买车型'+'评论.txt'  
    isrun=0
    if not os.path.exists(ft1):
        tits='车型\t购买地点\t油耗值\t性价比\t购车目的\t标题日期\t作者\t用户链接\t性别\t所在地\t生日\t内容'
        with open(ft1,'w',encoding='utf-8') as ftw1:
            ftw1.write(tits+'\n')
        isrun=1
    else:
        size1=os.path.getsize(ft1)
        if size1<300000:
            infoL1=open(ft1,encoding='utf-8').read().split('\n')
            isrun=1
    if isrun==1:
        get_review_data(car_code=car_code, spider=spider)
    
    print('the review data finished.')
   
    
    
    
    
