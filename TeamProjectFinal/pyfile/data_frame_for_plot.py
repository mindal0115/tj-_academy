import pandas as pd 
import numpy as np  

def merge_year_month(car_total):
    co_total = car_total[['차명','등록년','등록월','연령대','성별','자료건수']].copy()
    co_total['등록월'] = car_total['등록월'].apply(lambda x : '0'+str(x) if x < 10 else str(x))
    co_total['Months'] = co_total['등록년'].map(str)+'-'+co_total['등록월'].map(str)
    co_total = co_total.groupby(['차명','연령대','성별','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_total = co_total.groupby(['연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    return co_total,cs_total

def create_plot_data(car_total):
    co_total,cs_total = merge_year_month(car_total)
    cs_20=cs_total[cs_total['연령대'].isin(['20대'])].reset_index(drop=True)
    cs_30=cs_total[cs_total['연령대'].isin(['30대'])].reset_index(drop=True)
    cs_40=cs_total[cs_total['연령대'].isin(['40대'])].reset_index(drop=True)
    cs_50=cs_total[cs_total['연령대'].isin(['50대'])].reset_index(drop=True)
    # 합침
    cs_df20 = pd.concat([cs_20,cs_20,cs_20,cs_20]).reset_index(drop=True)
    cs_df30 = pd.concat([cs_30,cs_30,cs_30,cs_30]).reset_index(drop=True)
    cs_df40 = pd.concat([cs_40,cs_40,cs_40,cs_40]).reset_index(drop=True)
    cs_df50 = pd.concat([cs_50,cs_50,cs_50,cs_50]).reset_index(drop=True)

    # 전체차량 20대 남여
    cs_m20=co_total[co_total['연령대'].isin(['20대']) & co_total['성별'].isin(['남자'])].reset_index(drop=True)
    cs_f20=co_total[co_total['연령대'].isin(['20대']) & co_total['성별'].isin(['여자'])].reset_index(drop=True)

    # 전체차량 30대 남여
    cs_m30=co_total[co_total['연령대'].isin(['30대']) & co_total['성별'].isin(['남자'])].reset_index(drop=True)
    cs_f30=co_total[co_total['연령대'].isin(['30대']) & co_total['성별'].isin(['여자'])].reset_index(drop=True)
    
    # 전체차량 40대 남여
    cs_m40=co_total[co_total['연령대'].isin(['40대']) & co_total['성별'].isin(['남자'])].reset_index(drop=True)
    cs_f40=co_total[co_total['연령대'].isin(['40대']) & co_total['성별'].isin(['여자'])].reset_index(drop=True)

    # 전체차량 50대 남여
    cs_m50=co_total[co_total['연령대'].isin(['50대']) & co_total['성별'].isin(['남자'])].reset_index(drop=True)
    cs_f50=co_total[co_total['연령대'].isin(['50대']) & co_total['성별'].isin(['여자'])].reset_index(drop=True)

    # 각차량 20대 남자비율
    cs_m20b=cs_m20.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_m20b['비율'] = round(cs_m20['자료건수'] / cs_df20['자료건수'], 3)*100
    # 각차량 30대 남자비율
    cs_m30b=cs_m30.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_m30b['비율'] = round(cs_m30['자료건수'] / cs_df30['자료건수'], 3)*100
    # 각차량 40대 남자비율
    cs_m40b=cs_m40.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_m40b['비율'] = round(cs_m40['자료건수'] / cs_df40['자료건수'], 3)*100
    # 각차량 50대 남자비율
    cs_m50b=cs_m50.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_m50b['비율'] = round(cs_m50['자료건수'] / cs_df50['자료건수'], 3)*100

    # 각차량 20대 여자비율
    cs_f20b=cs_f20.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_f20b['비율'] = round(cs_f20['자료건수'] / cs_df20['자료건수'], 3)*100
    # 각차량 30대여자비율
    cs_f30b=cs_f30.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_f30b['비율'] = round(cs_f30['자료건수'] / cs_df30['자료건수'], 3)*100
    # 각차량 40대 여자비율
    cs_f40b=cs_f40.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_f40b['비율'] = round(cs_f40['자료건수'] / cs_df40['자료건수'], 3)*100
    # 각차량 50대 여자비율
    cs_f50b=cs_f50.groupby(['차명','연령대','Months']).agg({'자료건수':np.sum}).reset_index()
    cs_f50b['비율'] = round(cs_f50['자료건수'] / cs_df50['자료건수'], 3)*100

    # 각차량 20-50대 남자비율 df합치기
    cs_dftotal = pd.concat([cs_m20b,cs_m30b,cs_m40b,cs_m50b]).reset_index(drop=True)
    # 각차량 20-50대 여자비율 df합치기
    f_dftotal = pd.concat([cs_f20b,cs_f30b,cs_f40b,cs_f50b]).reset_index(drop=True)

    return cs_dftotal,f_dftotal
