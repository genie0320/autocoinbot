import pandas as pd
import json
import myutil as util
import logging
log = logging.getLogger(__name__)

def _ma_check(df) -> bool:
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


def _macd_check(df) -> bool:
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


def _price_check(df) -> bool:
    '''
    가격이 상승중인가.
    '''
    res = False

    close_prev = df['close'].iloc[-2]
    close = df['close'].iloc[-1]

    if close > close_prev:
        res = True

    return res


def _rsi_check(df) -> bool:
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

def _sort_coins(target_coins:list, interval:str) -> list:
    '''
    선별된 코인을 '직전 5개 거래량'기준으로 sort 한다.
    '''
    sorted_coins = {}
    for coin in target_coins:
        df = pd.read_pickle(f'data/index/{coin}_{interval}.pickle')['value']
        values = round(df.iloc[-1] + df.iloc[-2] + df.iloc[-3] + df.iloc[-4] + df.iloc[-5])
        sorted_coins[coin] = values

    sorted_dict = dict(sorted(sorted_coins.items(), key=lambda x: x[1], reverse=True))
    sorted_list = list(sorted_dict)

    return sorted_list

def select_target_coins(tickers, interval:str) -> list:
    '''
    될성부른 코인을 선별한다.
    '''
    target_coins = []      

    for ticker in tickers:
        new_file_path = f'data/index/{ticker}_{interval}.pickle'

        df = pd.read_pickle(new_file_path)

        if _ma_check(df):
            if _macd_check(df):
                if _rsi_check(df):
                    if _price_check(df):
                        target_coins.append(ticker)

    sorted_coin = _sort_coins(target_coins, interval)

    # with open(f'data/report/sorted_coins_{interval}.txt', 'w') as f:
    #     json.dump(sorted_coin, f)

    util.save_yaml('data/report.yml', **{f'coins_of_{interval}': sorted_coin})
    logging.info(sorted_coin)  
    return sorted_coin