from aquiles import AquilesBot

class AquilesLive(AquilesBot):
  """docstring for AquilesLive"""
  def __init__(self, stock):
    super(AquilesLive, self).__init__(stock)
    self.connect()
    self.bars = self.ib.reqHistoricalData(
          self.stock,
          endDateTime='',
          durationStr='2 D',
          barSizeSetting='2 mins',
          whatToShow='TRADES',
          useRTH=True,
          timeout=0,
          keepUpToDate=True
      )
    self.bars.updateEvent += self.on_bar_update
    self.set_currents()

  def on_bar_update(self, bars, has_new_bar):
    if has_new_bar:
        self.current_bar = bars[-2]
        self.current_bar_index = self.bars.index(self.current_bar)
        self.bar_context = self.build_bar_context()
        self.trigger_order()
        print(self.bar_context)
        # self.process_bar()

  def trigger_order(self):
    orders = self.ib.bracketOrder(
      self.bar_context['order_type'],
      self.bar_context['shares'],
      self.bar_context['price'],
      self.bar_context['take_profit'],
      self.bar_context['stop_lose']
    )
    for order in orders:
        self.ib.placeOrder(self.stock, order)