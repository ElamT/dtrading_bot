from aquiles import AquilesBot
from datetime import date, datetime
from dateutil.rrule import rrule, DAILY
from ib_insync import BarData


a = date(2023, 10, 31)
b = date(2023, 10, 31)

aquiles = AquilesBot('AMD')

for dt in rrule(DAILY, dtstart=a, until=b):
    date = dt.strftime("%Y%m%d")
    file = open("./data/%s_%s" %(aquiles.stock.symbol, date), "r")
    lines = file.readlines()
    for line in lines:
        data = line.strip().split(',')
        bar = BarData()
        # bar.date =  datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S%z')
        bar.date = data[0]
        bar.open = data[1]
        bar.high = data[2]
        bar.low = data[3]
        bar.close = data[4]
        bar.volume = data[5]
        bar.average = data[6]
        bar.barCount = data[7]
        print(bar)
    file.close
