
#%%
# 파이썬 내장
import os
import time
from datetime import datetime as dt
from datetime import timedelta
import pickle
import json
import logging

# 외부 모듈
import pyupbit
import pandas as pd

# 내부 모듈
import myutil, mydatahandler, mystrategy
import myorder as orders

from dotenv import load_dotenv

load_dotenv()

# access_key = os.getenv("UPBIT_OPEN_API_ACCESS_KEY")
# secret_key = os.getenv("UPBIT_OPEN_API_SECRET_KEY")
# upbit = pyupbit.Upbit(access_key, secret_key)

#%%
@myutil.time_check
def main() -> None:
    day_kr = myutil.get_now('full')
    time_kr = myutil.get_now('time')
    time_utc = myutil.get_utc_now('time')

    # ------------ 매일 오전 9시 넘어 1회 진행됨 ----------------
    if time_kr > '09:00' and time_kr < '09:17':
        print(f'----------------{day_kr} / {time_utc} ---------------------------')
        
        # 시황데이터 업데이트
        tickers:list = pyupbit.get_tickers('KRW')
        tickers = tickers[:5]
        today_coin_len = mydatahandler.get_ready(tickers, 'day')
        logging.info(f'오늘의 원화거래대상은 {today_coin_len}개입니다.')

        coins_of_day:list = mystrategy.select_target_coins(tickers, 'day')
        logging.info(f'오늘의 대상코인 : {coins_of_day}')    

    # # ------------ 15분마다 2,17,32,47 분에 진행 ----------------
    # 데이터를 업데이트 하고,
    print(f'----------------{time_kr} / {time_utc} ---------------------------')   
    
    mydatahandler.get_ready(tickers, 'minute15')
    coins_of_min15:list = mystrategy.select_target_coins(tickers, 'minute15')
    logging.info(f'{time_kr}의 대상코인 : {coins_of_min15}')    
    
    coins_to_buy = list(set(coins_of_min15).intersection(coins_of_day))
    

    # 걸려있는 예약 관리를 하고,
    # remains = myfunc.check_remain(upbit)
    # print('Remain orders :', remains) 


    # # 계좌 체크를 하고 > 현금을 만든다음
    my_coin = orders.sell()
    # cash = float(my_balance[0]['balance'])
    # print('Coins I have :', my_coin) 


    # # 남은 현금이 있다면 buy 진행.
    # if cash-5100 > 5100 and coins_to_buy:
    #     buy_report = myfunc.buy_order(upbit, coins_to_buy)
    #     print('buy_report :', len(buy_report), '개의 코인을 구매했습니다.') 
    # else:
    #     if not coins_to_buy:
    #         print('구매대상 코인이 없습니다. ')
    #     else:
    #         print('현금잔고가 부족하여 거래를 진행하지 않습니다. ')

    # 마지막으로 계좌정보를 다시 한번 쓰기

#%%
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, 
        # format = '%(asctime)s %(levelname)s %(message)s',
        format = "[%(filename)1s %(funcName)s() ] %(message)s",
        datefmt= '%Y-%m-%d %H:%M:%S',
        filename="autocoinbot.log", 
        filemode="a", 
        encoding='utf-8'
        )

    main()

#%%
