class BackTesting(object):
  """docstring for BackTesting"""
  def __init__(self):
    super(BackTesting, self).__init__()

  def run_backtesting(self):
    index = 195
    for bar in self.bars[index:]:
      self.set_currents(index=index)
      self.process_bar()
      index += 1

  def analyze_active_order(self):
      if self.active_order['order_type'] == 'SELL':
          if self.current_bar.high >= self.active_order['stop_lose']:
              self.amount_lose += self.active_order['shares'] * self.active_order['ticks_to_lose']
              self.loses += 1
              self.active_order['status'] = 'LOSE'
              self.active_order['NET'] = self.amount_win - self.amount_lose
              print(self.active_order)
              self.active_order = None

          elif self.current_bar.low <= self.active_order['take_profit']:
              self.amount_win += self.active_order['shares'] * self.active_order['ticks_to_win']
              self.wins += 1
              self.active_order['status'] = 'WIN'
              self.active_order['NET'] = self.amount_win - self.amount_lose
              print(self.active_order)
              self.active_order = None
      else:
          if self.current_bar.low <= self.active_order['stop_lose']:
              self.amount_lose += self.active_order['shares'] * self.active_order['ticks_to_lose']
              self.loses += 1
              self.active_order['status'] = 'LOSE'
              self.active_order['NET'] = self.amount_win - self.amount_lose
              print(self.active_order)
              self.active_order = None

          elif self.current_bar.high >= self.active_order['take_profit']:
              self.amount_win += self.active_order['shares'] * self.active_order['ticks_to_win']
              self.wins += 1
              self.active_order['status'] = 'WIN'
              self.active_order['NET'] = self.amount_win - self.amount_lose
              print(self.active_order)
              self.active_order = None
