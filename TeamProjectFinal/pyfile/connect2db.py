import pandas as pd  
import numpy as np  
import sqlite3 

def create_con():
    conn = sqlite3.connect('./data/TeamProjectFinal.db') 
    cursor = conn.cursor()
    return conn,cursor


def create_post_list_table(conn,cursor):
    cursor.execute('''
    create table cafe_post_list_naver_test(
        board_number int,
        article varchar(500),
        p_nick varchar(50),
        p_date date,
        p_view int
    );''')
    conn.commit()