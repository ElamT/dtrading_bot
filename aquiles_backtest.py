from aquiles import AquilesBot

class AquilesBacktest(AquilesBot):
  """docstring for AquilesBacktest"""
  def __init__(self, stock):
    super(AquilesBacktest, self).__init__(stock)
    self.wins = 0
    self.loses = 0
    self.amount_win = 0
    self.amount_lose = 0
    self.total_shares = 0


  def run_backtesting(self, year):
    index = 195
    self.file_results = file = open("./results/%s_%s.csv" %(self.stock.symbol, year), "w")
    self.file_columns = [
      'date',
      'order_type',
      'volume',
      'price',
      'shares',
      'stop_lose',
      'take_profit',
      'net',
      'net_acum'
    ]
    header = "%s%s" %(','.join(self.file_columns), '\n')
    self.file_results.write(header)
    for bar in self.bars[index:]:
      self.set_currents(index=index)
      self.process_bar()
      index += 1

  def write_operation(self):
    line = ""
    for key in self.file_columns:
      line += "%s," %(str(self.active_order[key]))

    line+= "\n"
    # breakpoint()
    self.file_results.write(line)

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
              self.write_operation()
              self.active_order = None

          elif self.current_bar.low <= self.active_order['take_profit']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_win'], 2)
              self.amount_win += net
              self.wins += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'WIN'
              self.active_order['net'] = net
              self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
              self.write_operation()
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
              self.write_operation()
              self.active_order = None

          elif self.current_bar.high >= self.active_order['take_profit']:
              net = round(self.active_order['shares'] * self.active_order['ticks_to_win'], 2)
              self.amount_win += net
              self.wins += 1
              self.total_shares += self.active_order['shares'] * 2
              self.active_order['status'] = 'WIN'
              self.active_order['net'] = net
              self.active_order['net_acum'] = round(self.amount_win - self.amount_lose, 2)
              self.write_operation()
              self.active_order = None
