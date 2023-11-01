from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
stock = Stock('AMD', 'SMART', 'USD')

bars = ib.reqHistoricalData(
    stock, endDateTime='', durationStr='3 D',
    barSizeSetting='2 mins', whatToShow='TRADES',
    useRTH=True, timeout=0, keepUpToDate=True)

active_order = None
acceptable_sma20_price_distance = 0.35
acceptable_sma20_sm200_distance = 0.35
acceptable_delta = 0.30
acceptable_volume = 200000
index = 195

amount_lose, amount_win, loses, wins = 0, 0, 0, 0

def calculate_sma(index='',bars_numbers=''):
    target = bars[index - bars_numbers: index + 1]
    sma = 0
    for x in target:
        sma += x.close
    return round(sma / len(target), 2)


def meet_conditions(index='', bar=''):
    sma20 = calculate_sma(index=index, bars_numbers=19)
    sma200 = calculate_sma(index=index, bars_numbers=195)
    print('SMA20: ' + str(sma20) + ' SMA200: ' + str(sma200))
    delta = round(bar.close - bar.open, 2)
    delta_20_200 = sma20 - sma200

    stop_lose = bar.high if delta < 0 else bar.low
    take_profit = bar.close - 1.1 if delta < 0 else bar.close + 1.1
    ticks_to_lose = abs(bar.close - stop_lose)
    ticks_to_win = abs(bar.close - take_profit)

    return (abs(delta) >= acceptable_delta and
            abs(bar.open - sma20) <= acceptable_sma20_price_distance and
            bar.volume >= acceptable_volume and ticks_to_lose <= 0.5 and
            abs(delta_20_200) <= acceptable_sma20_sm200_distance and
            active_order == None)

def analyze_active_order():
    global active_order, amount_lose, amount_win, loses, wins

    ticks_to_lose = abs(active_order['price'] - active_order['stop_lose'])
    ticks_to_win = abs(active_order['price'] - active_order['take_profit'])

    if active_order['order_type'] == 'SELL':
        if bar.high >= active_order['stop_lose']:
            amount_lose += active_order['shares'] * ticks_to_lose
            loses += 1
            active_order = None
        elif bar.low <= active_order['take_profit']:
            wins += 1
            amount_win += active_order['shares'] * ticks_to_win
            active_order = None
    else:
        if bar.low <= active_order['stop_lose']:
            amount_lose += active_order['shares'] * ticks_to_lose
            loses += 1
            active_order = None
        elif bar.high >= active_order['take_profit']:
            amount_win += active_order['shares'] * ticks_to_win
            wins += 1
            active_order = None


def process_bar(bar):
    global active_order

    if active_order != None:
        analyze_active_order()

    # index = bars.index(bar) + 1
    if index >= 195 and meet_conditions(index=index, bar=bar):
        sma20 = calculate_sma(index=index, bars_numbers=19)
        sma200 = calculate_sma(index=index, bars_numbers=195)
        delta = round(bar.close - bar.open, 2)
        delta_20_200 = sma20 - sma200

        order_type = 'SELL' if delta < 0 else 'BUY'
        stop_lose = bar.high if delta < 0 else bar.low
        take_profit = bar.close - 1.1 if delta < 0 else bar.close + 1.1
        order = {
            "order_type": order_type,
            "shares": 900,
            "price": bar.close,
            "stop_lose": stop_lose,
            'take_profit': take_profit,
        }
        active_order = order
        order = ib.bracketOrder(order_type, 600, bar.close, take_profit, stop_lose)

        for ord in order:
            print("Order: "+ str(ord))
            ib.placeOrder(stock, ord)

        print("TRIGGER ORDER | date " + str(bar.date) + " bar.open " + str(bar.open) + " bar.close " + str(bar.close) + " delta " + str(delta) + " sma20 " + str(sma20))
        print(order)


def onBarUpdate(bar, hasNewBar):
    global index
    new_bar = bar[-2]
    if hasNewBar:
        print('New Bar: ' + str(new_bar))
        process_bar(new_bar)
        index += 1

bars.updateEvent += onBarUpdate

for bar in bars[index: len(bars)-1]:
    print(bar)
    process_bar(bar)
    index += 1


print("Loses: " + str(amount_lose))
print("Profits: " + str(amount_win))
print('NET: '+ str(amount_win - amount_lose))
print("Loses Count: " + str(loses))
print("Profits Count: " + str(wins))

active_order = None

ib.run()
