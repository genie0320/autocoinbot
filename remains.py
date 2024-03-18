import os
import _trash.myhelper as myhelper
from dotenv import load_dotenv
import pyupbit
from datetime import datetime as dt
from datetime import timedelta
import myutil

load_dotenv()

access_key = os.getenv("UPBIT_OPEN_API_ACCESS_KEY")
secret_key = os.getenv("UPBIT_OPEN_API_SECRET_KEY")
upbit = pyupbit.Upbit(access_key, secret_key)
my_balance = upbit.get_balances()

def put_limit(upbit, my_balance):
    print('매수/매도쌍을 검수합니다. ')

    put_report = []
    ask = {}
    for coin in my_balance:
        buy_price = float(coin['avg_buy_price'])
        locked = float(coin['locked'])
        target_price = pyupbit.get_tick_size(buy_price * (1.0 + 0.005))

        if float(coin['avg_buy_price']) > 0:
            ticker = 'KRW-'+coin['currency']
            balance = float(coin['balance'])
            # print(type(ticker), type(balance))

            remain_order = upbit.get_order(ticker)
            remain_balance = 0.0
            for order in remain_order:

                # print(order)
                for i in order.keys():
                    remain_balance += float(order['volume'])
            
            diff = balance - remain_balance
            if not diff == 0:
                amount = balance - locked
                ask = upbit.sell_limit_order(ticker, target_price, amount)

            put_report.append(ask)

    return put_report

if __name__ == '__main__':

    upbit = pyupbit.Upbit(access_key, secret_key)
    my_balance = upbit.get_balances()
    my_coin = len(my_balance)-1

    put_report = put_limit(upbit, my_balance)
    
    if len(put_report) > 0:
        try:
            for rep in put_report:
                print(f"지정가매도 {rep['market']} : {rep['uuid']}")
        except Exception as e:
            print('Exception put_limit():', '이미 매도쌍이 존재합니다.',e)
    else:
        print(f"매수/매도쌍이 온전합니다.")