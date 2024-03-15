
#%%
# 파이썬 내장
import os
import time
from datetime import datetime as dt
from datetime import timedelta
import pickle
import json

# 외부 모듈
import pyupbit
import pandas as pd

# 내부 모듈
import myutil
import myfunc

from dotenv import load_dotenv

load_dotenv()

access_key = os.getenv("UPBIT_OPEN_API_ACCESS_KEY")
secret_key = os.getenv("UPBIT_OPEN_API_SECRET_KEY")
upbit = pyupbit.Upbit(access_key, secret_key)
       
#%%

@myutil.time_check
def main() -> None:
    time_utc = dt.now().strftime('%H:%M')
    day_kr = myutil.get_time('ch').strftime('%Y-%m-%d %H:%M')
    time_kr = myutil.get_time('ch').strftime('%H:%M')

    # ------------ 매일 오전 9시 넘어 1회 진행됨 ----------------
    if time_kr > '09:00' and time_kr < '09:17':
        print(f'----------------{day_kr} / {time_utc} ---------------------------')
        myfunc.update_ticker_data('day')
        target_coins_day:list = myfunc.get_target_coins('day')
        print('Coins of day :', target_coins_day)
        myfunc.sort_coins(target_coins_day, 'day')

    # ------------ 15분마다 2,17,32,47 분에 진행 ----------------
    # 데이터를 업데이트 하고,
    print(f'----------------{time_kr} / {time_utc} ---------------------------')
    myfunc.update_ticker_data('minute15')
    target_coins_min:list = myfunc.get_target_coins('minute15')
    print('Coins of 15min :', target_coins_min)
    coin_mins:list = myfunc.sort_coins(target_coins_min, 'minute15')

    with open(f'sorted_coins_day.txt', 'r') as f:
        days_coin = json.load(f)

    coins_to_buy = list(set(coin_mins).intersection(days_coin))
    print('Coins for BUY :', coins_to_buy)


    # 걸려있는 예약 관리를 하고,
    remains = myfunc.check_remain(upbit)
    print('Remain orders :', remains) 


    # 계좌 체크를 하고 > 현금을 만든다음
    my_balance = upbit.get_balances()
    cash = float(my_balance[0]['balance'])
    my_coin = myfunc.sell_order(upbit, my_balance)
    print('Coins I have :', my_coin) 


    # 남은 현금이 있다면 buy 진행.
    if cash-5100 > 5100 and coins_to_buy:
        buy_report = myfunc.buy_order(upbit, coins_to_buy)
        print('buy_report :', len(buy_report), '개의 코인을 구매했습니다.') 
    else:
        if not coins_to_buy:
            print('구매대상 코인이 없습니다. ')
        else:
            print('현금잔고가 부족하여 거래를 진행하지 않습니다. ')

    # 마지막으로 계좌정보를 다시 한번 쓰기

#%%
if __name__ == '__main__':
    main()

#%%
