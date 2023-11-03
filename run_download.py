from aquiles import AquilesBot
from datetime import date
from dateutil.rrule import rrule, DAILY

a = date(2019, 1, 1)
b = date(2023, 10, 31)


aquiles = AquilesBot('AMD')
aquiles.connect('127.0.0.1', 4002, clientId=1)

for dt in rrule(DAILY, dtstart=a, until=b):
    date = dt.strftime("%Y%m%d")
    datetime = dt.strftime("%Y%m%d 16:00:00")

    schedule = aquiles.reqHistoricalSchedule(aquiles.stock, 1, datetime)
    session = schedule.sessions[0]
    if session.refDate == date:
      bars = aquiles.reqHistoricalData(
          aquiles.stock,
          endDateTime=datetime,
          durationStr='1 D',
          barSizeSetting='2 mins',
          whatToShow='TRADES',
          useRTH=True,
          timeout=0,
          keepUpToDate=False
      )
      file = open("./data/%s_%s" %(aquiles.stock.symbol, date), "w")
      for bar in bars:
        # print(bar)
        file.write(
          "%s,%s,%s,%s,%s,%s,%s,%s\n" %(
          bar.date,
          bar.open,
          bar.high,
          bar.low,
          bar.close,
          bar.volume,
          bar.average,
          bar.barCount)
        )
      print("Processing... %s" %(date))
      file.close
