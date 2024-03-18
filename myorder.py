

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
            put_order = upbit.get_order(ticker, state="wait")
            buy_price = float(put_order[0]['avg_buy_price'])
            # ask_price = pyupbit.get_tick_size(buy_price * (1.0 + 0.07))
            # ask = upbit.sell_limit_order(ticker, ask_price, volume)

            buy_report.append(bid)
            buy_report.append(ask)

        with open('buy_report.txt', 'a') as f:
            json.dump(buy_report, f)

    except Exception as e:
        print('Exception From order() - ', e)

    return buy_report