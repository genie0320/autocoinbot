# 파이썬 내장
from datetime import datetime as dt
from datetime import timedelta
import os
import time
import pytz
import json
import pickle

# 외부 모듈
# import requests
import pyupbit
import pandas as pd

# 자체 모듈
import myutil
import myIndex


# ------------ 지표체크 관련 ----------------------
def ma_check(df) -> bool:
    '''
    MA지표가 정배열하고 있는가.
    '''
    res = False
    # MA 판단
    ma_short = df['ma_short'].iloc[-1]
    ma_long = df['ma_long'].iloc[-1]
    ma_200 = df['ma_200'].iloc[-1]
    close = df['close'].iloc[-1]
    
    if close > ma_short and ma_short > ma_long and ma_long > ma_200:
    # if close >= ma_short and ma_short >= ma_long and ma_long >= ma_200:
        res = True
    
    return res


def macd_check(df) -> bool:
    '''
    MACD지표가 0 이상이며, 시그널선보다 위인가.
    '''
    res = False
    macd = df['macd'].iloc[-1]
    macd_signal = df['macd_signal'].iloc[-1]
    macd_osc = df['macd_osc'].iloc[-1]
    macd_osc_prev = df['macd_osc'].iloc[-2]
    last_10_values = df['macd_osc'].tail(3)
    sum_osc = sum(1 for value in last_10_values if value >= 0) > 3
    
    if macd > macd_signal and macd_osc > 0 and macd_osc > macd_osc_prev:
    # if macd > macd_signal and macd_osc > macd_osc_prev:
        res = True
    # elif macd > macd_signal and macd_osc > 0 and sum_osc:      
    #     res = True

    return res


def price_check(df) -> bool:
    '''
    가격이 상승중인가.
    '''
    res = False

    close_prev = df['close'].iloc[-2]
    close = df['close'].iloc[-1]

    if close > close_prev:
        res = True

    return res


def rsi_check(df) -> bool:
    '''
    RSI지표가 50 이상이며, 시그널선보다 위인가.
    '''
    res = False   

    rsi = df['rsi'].iloc[-1]
    rsi_prev = df['rsi'].iloc[-1]
    rsi_signal = df['rsi_signal'].iloc[-1]
    
    # if rsi > rsi_signal and rsi > rsi_prev and rsi > 50:
    if rsi > rsi_signal:
        if rsi > 50 and rsi >= rsi_prev:
            res = True
            
    return res


# ------------ 코인데이터 업데이트 관련 ----------------------
def get_all_data(df, new_file_path:str) -> pd.DataFrame:
    '''
    시장데이터를 받아, 지표관련 계산결과를 돌려준다.
    '''
    # df = pd.read_pickle(file_path)

    df['ma_short'] = myIndex.SMA(df['close'], 12)
    df['ma_long'] = myIndex.SMA(df['close'], 26)
    df['ma_200'] = myIndex.SMA(df['close'], 200)
    _rsi = myIndex.RSI(df['close'], 14, 9)
    df = pd.concat([df, _rsi], axis=1)
    _macd = myIndex.MACD(df['close'], 12, 26, 9)
    df = pd.concat([df, _macd], axis=1)

    df.to_pickle(new_file_path)

    return df


# @myutil.time_check
def update_data(ticker:str, interval:str, file_path:str) -> pd.DataFrame:
    '''
    주어진 interval에 대한 ohlcv데이터를 업데이트한다. 
    '''
    if os.path.exists(file_path):
        _df = pd.read_pickle(file_path)
        df = pyupbit.get_ohlcv(ticker, interval = interval)
        df = pd.concat([_df, df], axis=0)
        df = df.drop_duplicates(keep='last')
        # print(f'{ticker} 파일을 업데이트합니다.')
    else:
        df = pyupbit.get_ohlcv(ticker, interval = interval)                

    df.to_pickle(file_path)
    return df


def update_ticker_data(interval:str) -> None:
    '''
    최신업데이트된 시장데이터와 지표관련계산결과를 받아
    파일로 저장한다. 
    '''
    tickers:list = pyupbit.get_tickers('KRW')

    for ticker in tickers:
        time.sleep(0.2)
        file_path = f'data/{ticker}_{interval}.pickle'
        new_file_path = f'data_result/{ticker}_{interval}.pickle'
        df = update_data(ticker, interval, file_path)
        get_all_data(df, new_file_path)


def get_target_coins(interval:str) -> list:
    '''
    될성부른 코인을 선별한다.
    '''
    tickers:list = pyupbit.get_tickers('KRW')
    target_coins = []      

    for ticker in tickers:
        new_file_path = f'data_result/{ticker}_{interval}.pickle'

        df = pd.read_pickle(new_file_path)

        if ma_check(df):
            if macd_check(df):
                if rsi_check(df):
                    if price_check(df):
                        target_coins.append(ticker)
                            
    with open(f'target_coins_{interval}.txt', 'w') as f:
        json.dump(target_coins, f)

    return target_coins

def sort_coins(target_coins:list, interval:str) -> list:
    '''
    선별된 코인을 '직전 5개 거래량'기준으로 sort 한다.
    '''
    with open(f'target_coins_{interval}.txt', 'r') as f:
        target_coins = json.load(f)

    sorted_coins = {}
    for coin in target_coins:
        df = pd.read_pickle(f'data_result/{coin}_{interval}.pickle')['value']
        values = round(df.iloc[-1] + df.iloc[-2] + df.iloc[-3] + df.iloc[-4] + df.iloc[-5])
        sorted_coins[coin] = values

    sorted_dict = dict(sorted(sorted_coins.items(), key=lambda x: x[1], reverse=True))
    sorted_list = list(sorted_dict)
    
    # result = [element for element in new_list if old_list.index(element) > new_list.index(element)]
    
    with open(f'sorted_coins_{interval}.txt', 'w') as f:
        json.dump(sorted_list, f)

    return sorted_list


# --------------- 이하 계좌 및 주문관련  -------------------

def check_remain(upbit) -> list:
    '''
    미체결주문정리
    '''
    remains:list = []

    _tickers:list = pyupbit.get_tickers('KRW')
    now = myutil.get_time()

    for ticker in _tickers:
        remain_order = upbit.get_order(ticker)

        if len(remain_order):
            for order in remain_order:
                uuid = order['uuid']
                side = order['side']
                _time = dt.fromisoformat(order['created_at'])
                limit_ask = _time + timedelta(minutes=2400) # 팔겠다.
                limit_bid = _time + timedelta(minutes=29) # 사겠다.
                print(f'{side} {ticker} 예약조회 - {uuid}')

                if side == 'ask' and limit_ask < now:
                    print(upbit.cancel_order(order['uuid']))
                elif side == 'bid' and limit_bid < now:
                    print(upbit.cancel_order(order['uuid']))
                else:
                    remains.append(ticker)    
    return remains


def sell_order(upbit, my_balance) -> list:
    my_coin:list = []

    try:
        # 보유코인 관리
        for i in range(len(my_balance)):
            ticker = f"KRW-{my_balance[i]['currency']}"
            avg_buy_price = float(my_balance[i]['avg_buy_price'])
            balance = float(my_balance[i]['balance'])
            cut_line = avg_buy_price* (1.0 - 0.015)
            earn_line = avg_buy_price* (1.0 + 0.025)    

            # 구매가가 있다면 ( == 현금잔고가 아님 )
            if avg_buy_price:
                current_price = pyupbit.get_current_price(ticker)
                if current_price < cut_line or current_price > earn_line:
                    # upbit.sell_market_order(ticker, balance)
                    rate = myutil.moving_rate(avg_buy_price,current_price)
                    print(f'{ticker} 매각. 수익률 : {rate:,.2f}')
                else:
                    my_coin.append(ticker)
            else:
                cash = balance
                locked = float(my_balance[i]['locked'])
                print(f'보유현금 : {cash:,.2f}, 예약중 : {locked:,.2f}')

    except Exception as e:
        print('Exception cut_loss():', e)

    return my_coin


def buy_order(upbit, tickers:list) -> list:
    buy_report = []

    try:
        for ticker in tickers:
            # 코인을 구매하고,
            # cash = upbit.get_balance('KRW')
            cash = 5100
            current_price = pyupbit.get_current_price(ticker)
            volume = current_price / cash
            bid = upbit.buy_market_order(ticker, cash)
            time.sleep(5)

            # 익절 지정가를 걸어두기
            put_order = upbit.get_order(ticker, state="done")
            buy_price = float(put_order[0]['avg_buy_price'])
            ask_price = pyupbit.get_tick_size(buy_price * (1.0 + 0.07))
            ask = upbit.sell_limit_order(ticker, ask_price, volume)

            buy_report.append(bid)
            buy_report.append(ask)

        with open('buy_report.txt', 'a') as f:
            json.dump(buy_report, f)

    except Exception as e:
        print('Exception From order() - ', e)

    return buy_report

'''

# --------------- 이하 사용하지 않는 함수 -------------------
# @myutil.time_check
def expand_data(ticker:str, interval:str, n:int, file_path:str) -> None:
    ''
    # 지표계산을 위한 데이터가 너무 적은 경우,
    # file_path의 데이터를 읽어와서 이전 데이터를 덧붙여 주어진 갯수만큼의 데이터셋을 구성한다.
    ''
    st_day = dt.datetime.now()

    try:
        calls = 0
        if interval == 'minute15':
            cnt = int(200 // (1440/15))
        elif interval == 'minute60':
            cnt = int(200 // (1440/60))
        elif interval == 'day':
            cnt = int(199 // (1440/1440))
        
        while len(ohlcv) < n and calls < 10:
            calls += 1
            day_delta = (st_day - dt.timedelta(days=cnt))
            st_day = day_delta
            _ohlcv = pyupbit.get_ohlcv(ticker, interval = interval, to = day_delta.strftime('%Y-%m-%d'))
            ohlcv = pd.concat([_ohlcv, ohlcv], axis=0)
            ohlcv = ohlcv.drop_duplicates()
            # print(f'{ticker},{len(ohlcv)}개의 데이터를 수집했습니다.')

            time.sleep(0.5)

        ohlcv.to_pickle(file_path)    

    except Exception as e:
        print('Exception : ', e)
'''