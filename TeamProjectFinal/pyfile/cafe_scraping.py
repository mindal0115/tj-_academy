import pandas as pd 
import numpy as np
# 웹 스크래핑에 필요한 패키지  
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time 

your_id = '' 
your_pwd = '' 

def login_to_naver(your_id,your_pwd):
    user = your_id 
    pwd = your_pwd
    driver = webdriver.Chrome('./data/chromedriver.exe')
    driver.implicitly_wait(10) # 10초대기

    url = 'https://nid.naver.com/nidlogin.login'
    driver.get(url)

    driver.execute_script("document.getElementsByName('id')[0].value=\'" + user + "\'")
    driver.execute_script("document.getElementsByName('pw')[0].value=\'" + pwd + "\'")
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
    time.sleep(2)
    return driver

def get_to_cafe(driver,cafe_url,menu):
    driver.get(cafe_url)
    driver.implicitly_wait(10) 
    driver.find_element_by_xpath(menu).click()
    time.sleep(5)
    frame = driver.find_element_by_id('cafe_main')
    driver.switch_to.frame(frame)

def scrap_post(driver,conn,cursor):
    page_btns = driver.find_elements_by_css_selector('div.prev-next > a')
    if page_btns[0].text != '이전': 
        n = 0 
    else: 
        n = 1
    for page in range(n,n+10):
        page_btns = driver.find_elements_by_css_selector('div.prev-next > a')
        page_btns[page].click()
        time.sleep(0.5)
        
        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        
        board_table = soup.select('div.article-board')[-1]
        board_numbers = board_table.select('table > tbody  td.td_article > div.board-number')
        board_lists = board_table.select('table > tbody  td.td_article > div.board-list')
        board_td_names = board_table.select('table > tbody  td.td_name')
        board_td_dates = board_table.select('table > tbody  td.td_date')
        board_td_views = board_table.select('table > tbody  td.td_view')
        
        # 게시글 목록 수집 
        for i in range(15):
            board_number = board_numbers[i].get_text()
            article = board_lists[i].a.get_text().strip()
            p_nick = board_td_names[i].a.get_text()
            p_date = board_td_dates[i].get_text()
            if len(p_date) < 8: p_date = '2019.07.05.'
            p_view = board_td_views[i].get_text()

            row = [board_number,article,p_nick,p_date,p_view]
            try:
                cursor.execute('''
                insert into cafe_post_list_naver_test values(?,?,?,?,?)
                ''',row)
                conn.commit()
            except:
                continue

    # 다음 10페이지로 
    page_btns = driver.find_elements_by_css_selector('div.prev-next > a')
    page_btns[-1].click()

    print('게시글 목록이 cafe_post_list_naver_test 에 저장되었습니다')

