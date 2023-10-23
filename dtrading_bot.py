from ib_insync import *

ib = IB()

# use this instead for IB Gateway
# ib.connect('127.0.0.1', 7497, clientId=1)

# us this for TWS (Workstation)
ib.connect('127.0.0.1', 7497, clientId=1)

stock = Stock('AMD', 'SMART', 'USD')


bars = ib.reqHistoricalData(
    stock, endDateTime='', durationStr='60 D',
    barSizeSetting='2 mins', whatToShow='TRADES', useRTH=True)

activeOrder = None
next_bar = 195
profits = 0
loses = 0
profitsCount = 0
losesCount = 0
for bar in bars[next_bar:]:
    sma20  = 0
    target = bars[next_bar - 19: next_bar + 1]
    for x in target:
        sma20 += x.close
    sma20 = round(sma20 / len(target), 2)

    sma200 = 0
    target = bars[next_bar - 195: next_bar + 1]
    # breakpoint()
    for x in target:
        sma200 += x.close
    sma200 = round(sma200 / len(target), 2)

    p_open = bar.open
    p_close = bar.close
    volume = bar.volume
    delta = round(p_close - p_open, 2)
    delta_20_200 = sma20 - sma200

    acceptable_sma20_price_distance = 0.35
    acceptable_sma20_sm200_distance = 0.35
    acceptable_delta = 0.30
    acceptable_volumen = 200000
    # breakpoint()

    # TODO
    # Validate distance between SMA20 and SMA200, it shouldn't be greater than 0.5
    #

    stopLoss = bar.high if delta < 0 else bar.low
    takeProfit = p_close - 1.1 if delta < 0 else p_close + 1.1
    ticksToLose = abs(p_close - stopLoss)
    ticksToWin = abs(p_close - takeProfit)
    if (abs(delta) >= acceptable_delta and
        abs(p_open - sma20) <= acceptable_sma20_price_distance and
        volume >= acceptable_volumen and ticksToLose <= 0.5 and
        abs(delta_20_200) <= acceptable_sma20_sm200_distance and
        activeOrder == None):

        orderType = 'Sell' if delta < 0 else 'Buy'
        order = {
            "orderType": orderType,
            "shares": 600,
            "price": p_close,
            "stopLoss": stopLoss,
            "takeProfit": takeProfit,
            "ticksToLose": ticksToLose,
            "ticksToWin": ticksToWin
        }
        activeOrder = order
        print("TRIGGER ORDER | date " + str(bar.date) + " p_open " + str(p_open) + " p_close " + str(p_close) + " delta " + str(delta) + " sma20 " + str(sma20))
        print(order)
    elif activeOrder != None:
        if activeOrder['orderType'] == 'Sell':
            if bar.high >= activeOrder['stopLoss']:
                loses += activeOrder['shares'] * activeOrder['ticksToLose']
                losesCount += 1
                activeOrder = None
            elif bar.low <= activeOrder['takeProfit']:
                profitsCount += 1
                profits += activeOrder['shares'] * activeOrder['ticksToWin']
                activeOrder = None
        else:
            if bar.low <= activeOrder['stopLoss']:
                loses += activeOrder['shares'] * activeOrder['ticksToLose']
                losesCount += 1
                activeOrder = None
            elif bar.high >= activeOrder['takeProfit']:
                profits += activeOrder['shares'] * activeOrder['ticksToWin']
                profitsCount += 1
                activeOrder = None

    # print("date " + str(bar.date) + " | "+ str(next_bar) + " close " + str(bar.close) + " volume " + str(bar.volume))
    next_bar += 1

print("Loses: " + str(loses))
print("Profits: " + str(profits))
print('NET: '+ str(profits - loses))
print("Loses Count: " + str(losesCount))
print("Profits Count: " + str(profitsCount))
print('Effective: ' + str(profitsCount / (profitsCount + losesCount)))
