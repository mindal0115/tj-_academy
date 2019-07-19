from bs4 import BeautifulSoup
from urllib.request import urlopen  
from selenium import webdriver 

import os 
import pyperclip
import numpy as np
import pandas as pd
import re 
import time

def correct_sentence(df2):
    contents = df2['tbody'].str.strip()
    contents = contents.apply(lambda x : re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\\"\'|\(\)\[\]\<\>`\'…》\xa0]|ㅋ|ㅎ|ㅠ|ㅜ', '',x))
    driver = webdriver.Chrome('./data/chromedriver.exe')
    after_sentence = [] 
    s_time = time.time()
    for sentence in contents[0:20]:
        if len(sentence) < 1000:
            try:
                driver.get('https://alldic.daum.net/grammar_checker.do')
                driver.find_element_by_css_selector('div.tf_grammar > textarea.tf_spell').\
                send_keys(sentence)
                driver.find_element_by_css_selector('div.btn_examine').click()
                # 맞춤법
                driver.find_element_by_css_selector('div.btn_examine > a#btnCopy').click()

                after_sentence.append(pyperclip.paste())

                time.sleep(0.05)
            except:
                after_sentence.append(sentence)
    e_time = time.time()
    print(e_time-s_time,'초')
    return after_sentence