import os
import time
import pickle
import logging

import pandas as pd
import pyupbit
import yaml

import myindex as idx
import myutil as util


# @myutil.time_check
def update_ohlcv(ticker:str, interval:str, file_path:str) -> pd.DataFrame:
    '''
    주어진 interval에 대한 ohlcv데이터를 업데이트한다. 
    '''
    if os.path.exists(file_path):
        _df = pd.read_pickle(file_path)
        df = pyupbit.get_ohlcv(ticker, interval = interval)
        df = pd.concat([_df, df], axis=0)
        df = df.drop_duplicates(keep='last')
    else:
        df = pyupbit.get_ohlcv(ticker, interval = interval)                

    df.to_pickle(file_path)
    return df


def update_idx(df, new_file_path:str) -> pd.DataFrame:
    '''
    시장데이터를 받아, 지표관련 계산결과를 붙여서 돌려준다.
    '''
    # df = pd.read_pickle(file_path)

    df['ma_short'] = idx.SMA(df['close'], 12)
    df['ma_long'] = idx.SMA(df['close'], 26)
    df['ma_200'] = idx.SMA(df['close'], 200)
    _rsi = idx.RSI(df['close'], 14, 9)
    df = pd.concat([df, _rsi], axis=1)
    _macd = idx.MACD(df['close'], 12, 26, 9)
    df = pd.concat([df, _macd], axis=1)

    df.to_pickle(new_file_path)

    return df



def get_ready(tickers, interval:str) -> int:
    '''
    ticker를 확인하고 각 데이터 업데이트를 실행한다.
    '''
    for ticker in tickers:
        time.sleep(0.2)
        file_path = f'data/ohlcv/{ticker}_{interval}.pickle'
        new_file_path = f'data/index/{ticker}_{interval}.pickle'
            
        _df = update_ohlcv(ticker, interval, file_path)
        df = update_idx(_df, new_file_path)

    return len(tickers)





# if __name__ == '__main__':
#     tickers:list = pyupbit.get_tickers('KRW')
#     update_ticker_data(tickers, 'day')