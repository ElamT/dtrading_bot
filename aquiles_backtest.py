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

  def realized_pnl(self):
    return self.amount_lose * -1

  def trigger_order(self):
    self.active_order = self.bar_context

  def active_portfolio(self):
    if self.active_order != None:
      return [self.active_order]
    else:
      return []

  def close_all(self):
    pass

  def load_data(self):
    previous_day = datetime.strptime(self.day, '%Y-%m-%d') - timedelta(1)
    target = []

    while len(target) < 1:
      target = glob.glob('./data/AMD_%s' %(datetime.strftime(previous_day, '%Y-%m-%d')))
      previous_day = previous_day - timedelta(1)

    file = open(target[0], "r")
    lines = file.readlines()

    for line in lines:
      bar = self.line_to_bar(line)
      self.bars.append(bar)

    file.close

  def line_to_bar(self, line):
    data = line.strip().split(',')
    bar = BarData()
    bar.date = data[0]
    bar.open = float(data[1])
    bar.high = float(data[2])
    bar.low = float(data[3])
    bar.close = float(data[4])
    bar.volume = float(data[5])
    bar.average = float(data[6])
    bar.barCount = float(data[7])
    return bar

  def run_backtesting(self):
    target = glob.glob('./data/AMD_%s' %(self.day))

    if len(target) > 0:
      filename = target[0]
      file = open(filename, "r")
      lines = file.readlines()

      for line in lines:
        bar = self.line_to_bar(line)
        self.bars.append(bar)
        self.process_bar(self.bars, True, backtesting=True)

  def analyze_active_order(self):
      if self.active_order['order_type'] == 'SELL':
          if self.current_bar.high >= self.active_order['stop_lose']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_lose'], 2)
              self.amount_lose += net
              self.loses += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'LOSE'
              self.active_order['net'] = net * -1
              self.active_order = None

          elif self.current_bar.low <= self.active_order['take_profit']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_win'], 2)
              self.amount_win += net
              self.wins += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'WIN'
              self.active_order['net'] = net
              self.active_order = None
      else:
          if self.current_bar.low <= self.active_order['stop_lose']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_lose'], 2)
              self.amount_lose += net
              self.loses += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'LOSE'
              self.active_order['net'] = net * -1
              self.active_order = None

          elif self.current_bar.high >= self.active_order['take_profit']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_win'], 2)
              self.amount_win += net
              self.wins += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'WIN'
              self.active_order['net'] = net
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
            self.active_order = None
          elif self.active_order['order_type'] == 'BUY':
            delta = self.active_order['price'] - current_price
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_lose += net
            self.loses += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'LOSE'
            self.active_order['net'] = net * -1
            self.active_order = None
          elif self.active_order['order_type'] == 'SELL' and current_price <= self.active_order['price']:
            delta = self.active_order['price'] - current_price
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_win += net
            self.wins += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'WIN'
            self.active_order['net'] = net
            self.active_order = None
          elif self.active_order['order_type'] == 'SELL':
            delta = current_price - self.active_order['price']
            net = round(self.active_order['shares'] * delta, 2)
            self.amount_lose += net
            self.loses += 1
            self.total_shares += self.active_order['shares'] * 2
            self.active_order['status'] = 'LOSE'
            self.active_order['net'] = net * -1
            self.active_order = None
