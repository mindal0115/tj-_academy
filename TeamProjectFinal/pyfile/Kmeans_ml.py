
import numpy as np 
import pandas as pd 
import random
import os 
from sklearn.cluster import KMeans
from pyfile.connect2db import * 
conn,cursor = create_con()

words = pd.read_csv('./data/게시글_뉴스_단어분류결과.csv',engine='python',encoding='utf-8')
words_dict = {
    
}
for category in words['분류'].unique():
    w = words.loc[words['분류'] == category,'단어'].values.tolist()
    words_dict[category] = w

def create_df_frame(model):
    df2 = pd.read_excel('./data/cafes/{}_카페_1.xlsx'.format(model))[['특징','등록지역','성별','연령대']].drop_duplicates()
    # merge 하기 위한 데이터프레임 
    df4 = df2[['등록지역','성별','연령대']].copy()
    df4.reset_index(inplace=True,drop=True)
    return df4

def kmeans_ml(model):
    df4 = create_df_frame(model)
    for category in words_dict.keys():
        df3 = pd.read_excel('./data/cafes/{}_카페_1.xlsx'.format(model))[['특징','등록지역','성별','연령대']].drop_duplicates()
        df3.reset_index(drop=True,inplace=True)
        for i in range(5):
            cafe = pd.read_excel('./data/cafes/{0}_카페_{1}.xlsx'.format(model,str(i+1)),parse_dates=['p_date'])
            cafe['Months'] = cafe['p_date'].dt.strftime('%Y-%m')

            df = cafe.copy()
            # 게시글에 카테고리 단어가 포함되어있으면 True
            df['단어포함여부'] = df['tbody'].str.contains('|'.join(words_dict[category]))

            # True 값들을 월별로 집계
            # df_corrf1 생성 
            df_corrf1 = df.query('Months >= "2018-01"').\
            groupby(['특징','Months']).\
            agg({'단어포함여부':np.sum,'p_view':np.mean}).\
            pivot_table(index='Months',columns='특징').fillna(0)['p_view']

            df1 = cafe[['특징','등록지역','성별','연령대']].drop_duplicates()
            # 코나 판매량을 월별로 집계 
            kona_sale = pd.read_sql('select * from qm3_total;',conn)
            kona_sale['day']=1
            kona_sale.rename(columns={'등록년':'year','등록월':'month'},inplace=True)
            kona_sale['Months'] = pd.to_datetime(kona_sale[['year','month','day']]).dt.strftime('%Y-%m')

            df2 = kona_sale[['Months','자료건수','등록지역','성별','연령대']]
            df_sales = pd.merge(df2,df1,on=['등록지역','성별','연령대'])

            # df_corrf2 생성 
            df_corrf2 =df_sales.\
            groupby(['특징','Months']).\
            agg({'자료건수':np.sum}).\
            pivot_table(index='Months',columns='특징').fillna(0)['자료건수']

            # 두 데이터 프레임간 열별 상관계수를 구함
            corr_tble = df_corrf1.corrwith(df_corrf2).reset_index()

            df3 = pd.merge(df3,corr_tble,on='특징')

        # 머신러닝을 위한 테이블 수정 
        df3.columns = ['특징','등록지역','성별','연령대','사이트1','사이트2','사이트3','사이트4','사이트5']
        df_for_ml = df3[['사이트1','사이트2','사이트3','사이트4','사이트5']].copy()
        for col in df_for_ml.columns:
            df_for_ml.loc[:,col] = df_for_ml.loc[:,col].apply(lambda x : 0 if x<=0 else x)
        df_for_ml.fillna(0,inplace=True)

        # 머신러닝 
        X = df_for_ml.copy() 
        kmeans = KMeans(n_clusters=3).fit(X)
        lbl = kmeans.labels_
        df_for_ml[category] = lbl

        # 값을 구분하는 기준
        cl = kmeans.__dict__['cluster_centers_'].mean(axis=1)
        cl = cl.tolist()
        most_interest = cl.index(max(cl))
        no_interest = cl.index(min(cl)) 

        lst = [0,1,2]
        lst.remove(most_interest)
        lst.remove(no_interest)
        interest= lst[0]


        df_for_ml[category] = df_for_ml[category].apply(lambda x : '많음' if x == most_interest else x)
        df_for_ml[category] = df_for_ml[category].apply(lambda x : '적음' if x == no_interest else x)
        df_for_ml[category] = df_for_ml[category].apply(lambda x : '보통' if x == interest else x)

        df4 = pd.merge(df4,df_for_ml[[category]],left_index=True,right_index=True,how='outer')
    return df4