from aquiles import AquilesBot
from datetime import datetime

class AquilesLive(AquilesBot):
  """docstring for AquilesLive"""
  def __init__(self, stock):
    super(AquilesLive, self).__init__(stock)
    self.connect()
    self.bars = self.ib.reqHistoricalData(
          self.stock,
          endDateTime='',
          durationStr='3 D',
          barSizeSetting='2 mins',
          whatToShow='TRADES',
          useRTH=True,
          timeout=0,
          keepUpToDate=True
      )
    self.bars.updateEvent += self.on_bar_update
    self.set_currents()

  def realized_pnl(self):
    pnl = None
    values = self.ib.accountValues()
    for value in values:
      if value.tag == 'RealizedPnL' and value.currency == 'USD':
        pnl = value
        break
    return float(pnl.value)

  def max_daily_lose(self):
    # Maximun stop lose by day 300USD approx 1%
    return -300

  def acceptable_datetime(self):
    return True

  def close_all(self):
    pass
    # open_orders = self.ib.reqAllOpenOrders()

  def on_bar_update(self, bars, has_new_bar):
    if has_new_bar:
        self.current_bar = bars[-2]
        self.current_bar_index = self.bars.index(self.current_bar)
        self.bar_context = self.build_bar_context()

        if not self.acceptable_datetime():
          self.close_all()
        else:
          portfolio = self.ib.portfolio()
          self.bar_context['trade_conditions'] = self.meet_conditions()
          self.bar_context['portfolio_conditions'] = len(portfolio) == 0
          self.bar_context['daily_pnl_conditions'] = self.realized_pnl() > self.max_daily_lose()

          print(self.bar_context)
          if (self.current_bar_index >= 195 and
              self.bar_context['trade_conditions'] and
              self.bar_context['portfolio_conditions'] and
              self.bar_context['daily_pnl_conditions']):
            self.trigger_order()

  def trigger_order(self):
    orders = self.ib.bracketOrder(
      self.bar_context['order_type'],
      self.bar_context['shares'],
      self.bar_context['price'],
      self.bar_context['take_profit'],
      self.bar_context['stop_lose']
    )
    for order in orders:
        today = datetime.today().strftime('%Y%m%d')
        order.tif = 'GTD'
        order.goodTillDate = "%s 15:56:00 %s" %(today, 'America/New_York')
        self.ib.placeOrder(self.stock, order)
