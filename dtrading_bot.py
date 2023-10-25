from ib_insync import *

ib = IB()

# use this instead for IB Gateway
# ib.connect('127.0.0.1', 7497, clientId=1)

# us this for TWS (Workstation)
ib.connect('127.0.0.1', 7497, clientId=1)

stock = Stock('AMD', 'SMART', 'USD')


bars = ib.reqHistoricalData(
    stock, endDateTime='', durationStr='18 D',
    barSizeSetting='2 mins',
    whatToShow='TRADES',
    useRTH=True,
    timeout=0,
    keepUpToDate=False)

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

    delta = round(bar.close - bar.open, 2)
    delta_20_200 = sma20 - sma200


    # All the parametros releated a strengh were setted looking a 100 USD price
    # is important make relative those values by percentage
    acceptable_sma20_price_distance = 0.35
    acceptable_sma20_sm200_distance = 0.35
    acceptable_delta = 0.30
    acceptable_volume = 200000
    # breakpoint()

    # TODO
    # Validate distance between SMA20 and SMA200, it shouldn't be greater than 0.5
    #

    stopLoss = bar.high if delta < 0 else bar.low
    # stopLoss = bar.close + 0.5 if delta < 0 else bar.close - 0.5
    takeProfit = bar.close - 1.1 if delta < 0 else bar.close + 1.1
    ticksToLose = abs(bar.close - stopLoss)
    ticksToWin = abs(bar.close - takeProfit)
    if (abs(delta) >= acceptable_delta and
        abs(bar.open - sma20) <= acceptable_sma20_price_distance and
        bar.volume >= acceptable_volume and ticksToLose <= 0.5 and
        abs(delta_20_200) <= acceptable_sma20_sm200_distance and
        activeOrder == None):

        orderType = 'Sell' if delta < 0 else 'Buy'
        order = {
            "orderType": orderType,
            "shares": 900,
            "price": bar.close,
            "stopLoss": stopLoss,
            "takeProfit": takeProfit,
            "ticksToLose": ticksToLose,
            "ticksToWin": ticksToWin
        }
        activeOrder = order
        print("TRIGGER ORDER | date " + str(bar.date) + " bar.open " + str(bar.open) + " bar.close " + str(bar.close) + " delta " + str(delta) + " sma20 " + str(sma20))
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

    next_bar += 1

print("Loses: " + str(loses))
print("Profits: " + str(profits))
print('NET: '+ str(profits - loses))
print("Loses Count: " + str(losesCount))
print("Profits Count: " + str(profitsCount))
# print('Effective: ' + str(profitsCount / (profitsCount + losesCount)))
print("net: " + str(profits - loses) + " loses: " + str(losesCount) + " profits " + str(profitsCount))
