import os
import glob
from aquiles import AquilesBot
from datetime import datetime, timedelta
from ib_insync import BarData

class AquilesBacktest(AquilesBot):
  """docstring for AquilesBacktest"""
  def __init__(self, stock, day):
    super(AquilesBacktest, self).__init__(stock)
    self.wins = 0
    self.loses = 0
    self.amount_win = 0
    self.amount_lose = 0
    self.total_shares = 0
    self.day = day
    self.bars = []
    self.load_data()

  def load_data(self):
    target = glob.glob('./data/AMD_%s' %(self.day))
    if len(target) > 0:
      previous = datetime.strptime(self.day, '%Y-%m-%d') - timedelta(1)
      while len(target) < 2:
        target += glob.glob('./data/AMD_%s' %(datetime.strftime(previous, '%Y-%m-%d')))
        previous = previous - timedelta(1)

      for filename in sorted(target):
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
              self.bars.append(bar)

          file.close
    else:
      raise "File Not Found"

  def run_backtesting(self):
    index = 195
    for bar in self.bars[index:]:
      self.set_currents(index=index)
      self.process_bar()
      index += 1
    print("======== %s =======" %(self.day))
    print("AMOUNT LOSE: %s" %(self.amount_lose))
    print("AMOUNT WIN: %s" %(self.amount_win))
    print("NET: %s" %(self.amount_win - self.amount_lose))
    print("COUNT LOSE: %s" %(self.loses))
    print("COUNT WIN: %s" %(self.wins))

  def analyze_active_order(self):
      if self.active_order['order_type'] == 'SELL':
          if self.current_bar.high >= self.active_order['stop_lose']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_lose'], 2)
              self.amount_lose += net
              self.loses += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'LOSE'
              self.active_order['net'] = net * -1
              self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
              self.active_order = None

          elif self.current_bar.low <= self.active_order['take_profit']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_win'], 2)
              self.amount_win += net
              self.wins += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'WIN'
              self.active_order['net'] = net
              self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
              self.active_order = None
      else:
          if self.current_bar.low <= self.active_order['stop_lose']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_lose'], 2)
              self.amount_lose += net
              self.loses += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'LOSE'
              self.active_order['net'] = net * -1
              self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
              self.active_order = None

          elif self.current_bar.high >= self.active_order['take_profit']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_win'], 2)
              self.amount_win += net
              self.wins += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'WIN'
              self.active_order['net'] = net
              self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
              self.active_order = None


      if self.active_order != None:
        time = datetime.strptime(self.active_order['date'], '%Y-%m-%d %H:%M:%S%z')
        if time.hour == 15 and time.minute == 50:
          current_price = self.bar_context['price']
          if self.active_order['order_type'] == 'BUY' and current_price >= self.active_order['price']:
            delta = current_price - self.active_order['price']
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_win += net
            self.wins += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'WIN'
            self.active_order['net'] = net
            self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
            self.active_order = None
          elif self.active_order['order_type'] == 'BUY':
            delta = self.active_order['price'] - current_price
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_lose += net
            self.loses += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'LOSE'
            self.active_order['net'] = net * -1
            self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
            self.active_order = None
          elif self.active_order['order_type'] == 'SELL' and current_price <= self.active_order['price']:
            delta = self.active_order['price'] - current_price
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_win += net
            self.wins += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'WIN'
            self.active_order['net'] = net
            self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
            self.active_order = None
          elif self.active_order['order_type'] == 'SELL':
            delta = current_price - self.active_order['price']
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_lose += net
            self.loses += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'LOSE'
            self.active_order['net'] = net * -1
            self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
            self.active_order = None
