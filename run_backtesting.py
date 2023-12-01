from aquiles_backtest import AquilesBacktest
from datetime import date, datetime
from ib_insync import BarData
import os
import glob


target = sorted(glob.glob('./data/AMD_*-*-*'))
file = open("./results/results.csv", "w")
file_columns = [
  'date',
  'amount_win',
  'amount_lose',
  'wins',
  'loses'
]
header = "%s%s" %(','.join(file_columns), '\n')
file.write(header)

for fn in target:
    filename = fn.split('/')[-1]
    day = filename.split('_')[-1]
    if day != '2019-01-02':
        aquiles = AquilesBacktest('AMD', day)
        aquiles.run_backtesting()
        line = "%s,%s,%s,%s,%s\n" %(aquiles.day, aquiles.amount_win, aquiles.amount_lose, aquiles.wins, aquiles.loses)
        file.write(line)

file.close
