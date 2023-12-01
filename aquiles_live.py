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
    self.bars.updateEvent += self.process_bar

  def realized_pnl(self):
    pnl = None
    values = self.ib.accountValues()
    for value in values:
      if value.tag == 'RealizedPnL' and value.currency == 'USD':
        pnl = value
        break
    return float(pnl.value)

  def active_portfolio(self):
    return self.ib.portfolio()

  def close_all(self):
    pass
    # open_orders = self.ib.reqAllOpenOrders()

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
