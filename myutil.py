#%%
import time
import pytz
from datetime import datetime
import pickle
import os
import pandas as pd
import yaml

def calc_price(price:float, rate:float):
    '''
    가격계산. rate를 -로 주면 손절가격계산됨.
    ''' 
    return price * (1+rate/100)

def moving_rate(prev_price:float, current_price:float) -> float:
    return round((current_price - prev_price) / prev_price * 100, 3)

def time_check(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"함수 {func.__name__}의 실행 시간: {end_time - start_time} 초")
        return result
    return wrapper


def get_now(type:str = ''):
    KST = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(KST)

    if type == 'full':
        res = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    elif type =='time':
        res = now_kst.strftime("%H:%M")
    else:
        res = now_kst

    return res

def get_utc_now(type:str = ''):
    UTC = pytz.timezone('utc')
    now_utc = datetime.now(UTC)
    if type == 'full':
        res = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    elif type =='time':
        res = now_utc.strftime("%H:%M")        
    else:
        res = now_utc

    return res

def save_pkl(file_path:str, type:str) -> None:
    '''
    파일을 생성한다.
    '''
    if not os.path.exists(file_path):
        if type == 'pickle':
            df = pd.DataFrame()
            df.to_pickle(file_path)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')

def save_yml(file_path, **datas):
    '''
    yaml 파일을 생성한다.
    
    - file_path : yaml 파일의 경로
    - datas : yaml 파일에 저장할 데이터(dictionary)
    '''
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            placeholder = dict()
            yaml.safe_dump(placeholder, f, allow_unicode=True, default_flow_style=False)

    with open(file_path, 'r') as f:
        _data = yaml.safe_load(f)

    for k, v in datas.items():
        _data[k] = v
        
    with open(file_path, 'w') as f:
        print('저장한다.')
        yaml.safe_dump(_data, f, allow_unicode=True, default_flow_style=False)

# %%
