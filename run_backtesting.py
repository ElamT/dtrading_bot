from aquiles_backtest import AquilesBacktest
from datetime import date, datetime
from ib_insync import BarData
import os


for x in [2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    a = date(x, 1, 1)
    b = date(x, 12, 31)
    aquiles = AquilesBacktest('AMD')
    aquiles.bars = []

    files = sorted(os.listdir('./data'))
    target = []
    for x in files:
        file_date = datetime.strptime(x.split('_')[-1], '%Y%m%d').date()
        if a <= file_date <= b:
            target.append(x)

    for file in target:
        filename = "./data/%s" %(file)
        # print('Processing %s' %(filename))
        file = open(filename, "r")
        lines = file.readlines()

        for line in lines:
            data = line.strip().split(',')
            bar = BarData()
            # bar.date =  datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S%z')
            bar.date = data[0]
            bar.open = float(data[1])
            bar.high = float(data[2])
            bar.low = float(data[3])
            bar.close = float(data[4])
            bar.volume = float(data[5])
            bar.average = float(data[6])
            bar.barCount = float(data[7])
            aquiles.bars.append(bar)

        file.close

    aquiles.run_backtesting()
    print("======= %s - %s ========" %(a, b))
    print("Loses: " + str(aquiles.amount_lose))
    print("Profits: " + str(aquiles.amount_win))
    print('NET: '+ str(aquiles.amount_win - aquiles.amount_lose))
    print("Loses Count: " + str(aquiles.loses))
    print("Profits Count: " + str(aquiles.wins))
    print("TOTAL TRADES: %s" %(aquiles.loses + aquiles.wins))
    print('TOTAL SHARES: %s' %(aquiles.total_shares))
    print("Effective: %s" %(round(aquiles.wins / (aquiles.wins + aquiles.loses) * 100, 2)))