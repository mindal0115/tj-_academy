from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re
import pymysql

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< naver 뉴스 검색시 리스트 크롤링하는 프로그램 > _select사용
- 크롤링 해오는 것 : 링크,제목,신문사,날짜,내용요약본
- 날짜,내용요약본  -> 정제 작업 필요
- 리스트 -> 딕셔너리 -> df -> 엑셀로 저장 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
source_text = []
date_text = []
contents_text = []
result = []

# 엑셀로 저장하기 위한 변수
RESULT_PATH = './data/news/' # 저장할 경로
now = datetime.now() # 파일이름 현 시간으로 저장하기

# 날짜 정제화 함수
def date_cleansing(test):
    try:
        pattern = '\d+.(\d+).(\d+)' # 정규표현식
                
        r = re.compile(pattern)
        match = r.search(test).group(0)
        date_text.append(match)
                
    except AttributeError:
        pattern = '\w* (\d\w*)' #정규표현식
                
        r = re.compile(pattern)
        match = r.search(test).group(1)
        date_text.append(match)
        
# 본문 요약 정제화
def contents_cleansing(contents):
    first_cleasing_contents = re.sub('<dl>.*?</a></div></dd><dd>', '', str(contents)).strip() # 앞에 필요없는 부분 제거
    second_cleansing_sontents = re.sub('<ul class="relation_lst">.*?</dd>', '',first_cleasing_contents).strip() # 뒤에 필요없는 부분 제거
    third_cleansing_contents = re.sub('<.+?>', '',second_cleansing_sontents).strip()
    contents_text.append(third_cleansing_contents)

def crawler(maxpage, query, sort, s_date, e_date):
    
    s_from = s_date.replace('.','')
    e_to = e_date.replace('.','')
    page = 1
    maxpage_t = (int(maxpage)-1)*10+1
    
    while page <= maxpage_t:
        url = 'https://search.naver.com/search.naver?where=news&query='+query+'&sort='+sort+'&ds='+s_date+'&de='+e_date+'&nso=so%3Ar%2Cp%3Afrom'+s_from+'to'+e_to+'%2Ca%3A&start='+str(page)
        
        response = requests.get(url)
        html =response.text
        
        # BeautifulSoup의 인자값 지정
        soup = BeautifulSoup(html, 'html.parser')
        
        # 태크에서 제목 추출
        atags = soup.select('._sp_each_title') # 클래스명으로 가졍로 경우 .을 뒤에 클래스명 기입
        for atag in atags:
            title_text.append(atag.text) # 제목추출
        
        # 신문사 추출
        source_lists = soup.select('._sp_each_source')
        for source_list in source_lists:
            source_text.append(source_list.text) # 신문사
            
        # 날짜 추출
        date_lists = soup.select('.txt_inline')
        for date_list in date_lists:
            test = date_list.text
            date_cleansing(test) # 날짜 정제 함수사용
            
            
        # 본문요약본
        contents_lists = soup.select('ul.type01 dl') # 본문 요약 부분에는 id나 class명이 없어 그 위의 'ul.type01 dl'으로 통째로 가져와 정규표현식으로 필요한 부분만 추출
        for contents_list in contents_lists:
            contents_cleansing(contents_list) #본문 요약 정제화

        # 모든 리스트를 딕셔너리 형태로 저장
        result = {'date':date_text, 'title':title_text, 'source':source_text, 'contents':contents_text}
        print(page)
        
        df = pd.DataFrame(result)
        page += 10
        
    # 새로 만들 파일이름 지정
    outputFileName = '%s-%s-%s  %s시 %s분 %s초 merging.xlsx' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    df.to_excel(RESULT_PATH+outputFileName,sheet_name='sheet1')

def main():
    info_main = input('='*50+'\n'+'입력 형식에 맞게 입력해주세요.'+'\n'+'시작하시려면 Enter를 눌러주세요.'+'\n'+'='*50)
    
    maxpage = input('최대 크롤링할 페이지 수 입력하시오: ')
    query = input('검색어 입력: ')
    sort = input('뉴스 검색 방식 입력(관련도순=0, 최신순=1, 오래된순=2): ')
    s_date = input('시작날짜 입력(YYYY.MM.DD): ')
    e_date = input('끝날짜 입력(YYYY.MM.DD): ')
    
    crawler(maxpage, query, sort, s_date, e_date)
    print('크롤링이 완료되었습니다.')
