import numpy as np 
import pandas as pd 
import random

car_names = pd.DataFrame({'en':['kona','tivoli','stonic','qm3']},index=['코나','티볼리','스토닉','QM3'])

def create_cafe_member(model,car_name,conn,cursor):
    cafe_contents = pd.read_sql('select * from cafe_post_contents_naver;',conn,parse_dates=['td_date'])
    cafe_posts = pd.read_sql('select * from cafe_post_list_naver;',conn,parse_dates=['p_date'])
    cafe_posts2 = cafe_posts[['car_name','article_number','p_view','location2']]
    cafe_contents.columns = ['car_name','article_number','p_date','tbody']
    df_contents2 = pd.merge(cafe_contents,cafe_posts2,on=['car_name','article_number'])
    df_contents2.rename(columns={'location2':'등록지역'},inplace=True)

    # 모델명 선택 후 데이터 프레임 불러오기 

    df= pd.read_sql('select * from {}_total;'.format(model),conn)
    # 각 지역, 성별, 연령대별로 판매량이 어떤지 
    df_weight = df.groupby(['등록지역','성별','연령대']).\
    agg({'자료건수':np.sum}).\
    pivot_table(index=['성별','연령대'], columns=['등록지역']).fillna(0)['자료건수']
    # 각 지역별로 판매량 합 구하기
    car_sales_total = df_weight.sum().sum()
    # df_weight.apply(lambda x : x.sum())
    # 지역 기준, 성별, 연령 비율 구하기 
    df_weight_ratio = df_weight.copy() 
    for row in df_weight_ratio.index:
        df_weight_ratio.loc[row,:] = df_weight.loc[row,:]/car_sales_total
    # melt 함수를 이용해서 최종적으로 필요한 데이터프레임 생성 
    vv = df_weight_ratio.columns.tolist()
    df_weight_ratio2 = pd.melt(df_weight_ratio.reset_index(),id_vars=['성별','연령대'],value_vars=vv)
    df_weight_ratio2['모델명'] = model 
    # 각 모델의 지역별, 성별, 연령별 비중을 나타내는 테이블 완성 
    # 각 등록지역의 value를 합하면 100이 됨 


    # 필요한 게시글 목록만 가져오기 
    cafe = df_contents2.query('car_name == "{}"'.format(car_name)).reset_index(drop=True)
    cafe.sort_values('등록지역',inplace=True)
    cafe.reset_index(drop=True,inplace=True)

    cafe['성별'] = np.nan
    cafe['연령대'] = np.nan
    # 각 특징별로 몇명이 필요한지 계산하기 
    df_weight_ratio2['인원수'] = np.nan
    for loc in cafe['등록지역'].unique():
        pop = (cafe['등록지역'] == loc).sum()
        df_weight_ratio2.loc[df_weight_ratio2['등록지역'] == loc,'인원수'] =\
        df_weight_ratio2.query('등록지역 == "{}"'.format(loc))['value'].apply(lambda x: int(pop*(x)))

    df_weight_ratio2['인원수'] = round(df_weight_ratio2['value']*cafe.shape[0],0)
    
    # 각 특징별로 계산된 인원수만큼 난수를 생성하기  
    new_lst = [] 
    for count,val in enumerate(df_weight_ratio2['인원수']):
        new_lst =new_lst + np.repeat(count,val).tolist()

    if len(new_lst) > cafe.shape[0]:
        new_lst = new_lst[abs(cafe.shape[0]-len(new_lst)):]

    new_lst = new_lst + np.repeat(1,cafe.shape[0]-len(new_lst)).tolist()
    random.shuffle(new_lst)
    cafe['특징'] = new_lst
    # 생성된 난수를 기준으로 게시글에 성별, 연령대, 등록지역 부과하기
    for i in cafe.index:
        idx = cafe.loc[i,'특징']
        sfl = df_weight_ratio2.loc[idx,['성별','연령대','등록지역']]
        # age = df_weight_ratio2.loc[idx,'연령대']
        # loc = df_weight_ratio2.loc[idx,'등록지역']
        cafe.loc[i,['성별','연령대','등록지역']] = sfl
    return cafe