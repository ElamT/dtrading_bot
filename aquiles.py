from ib_insync import *
from datetime import datetime

class AquilesBot():
  """docstring for AquilesBot"""
  def __init__(self, stock):
    super(AquilesBot, self).__init__()
    self.stock = Stock(stock, 'SMART', 'USD')
    self.active_order = None
    self.max_daily_lose = -300

  def connect(self):
    self.ib = IB()
    self.ib.connect('127.0.0.1', 4001, clientId=1)
    print('Connected %s' %(self.ib))

  def calculate_sma(self, periods=''):
    index = self.current_bar_index
    if index >= periods:
        target = self.bars[index - periods : index + 1]
        sma = 0
        for x in target:
            sma += x.close
        return round(sma / len(target), 2)
    else:
        raise Exception('Index is less than len of bars')

  def time_condition(self):
    current_time = datetime.strptime(self.bar_context['date'], '%Y-%m-%d %H:%M:%S%z')
    accepatable_time = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    return current_time <= accepatable_time

  def increment_condition(self):
    acceptable_delta = 0.40 / 100
    return abs(self.bar_context['delta'] / self.current_bar.open) >= acceptable_delta

  def volume_condition(self):
    acceptable_volume = 150000 # or 200k is the same efect
    return self.current_bar.volume >= acceptable_volume

  def risk_ratio_condition(self):
    return self.bar_context['ticks_to_lose'] / self.bar_context['ticks_to_win'] <= 0.5

  def sma_conditions(self):
    order_type = self.bar_context['order_type']
    sma20 = self.bar_context['sma20']
    current_price = self.bar_context['price']

    if order_type == 'BUY':
      return current_price >= sma20
    else:
      return current_price <= sma20

  def acceptable_datetime(self):
    time = datetime.strptime(self.progress_bar.date, '%Y-%m-%d %H:%M:%S%z')
    from_time = time.replace(hour=9, minute=32)
    until_time = time.replace(hour=15, minute=50)

    return from_time <= time <= until_time

  def meet_conditions(self):
    return (self.increment_condition() and
            self.volume_condition() and
            self.risk_ratio_condition() and
            self.sma_conditions())

  def process_bar(self, bars, has_new_bar, backtesting=False):
    if has_new_bar:
        self.progress_bar = bars[-1]
        self.current_bar = bars[-2]
        self.current_bar_index = self.bars.index(self.current_bar)
        self.bar_context = self.build_bar_context()

        if backtesting and self.active_order != None:
          self.analyze_active_order()

        if self.acceptable_datetime():
          self.bar_context['trade_conditions'] = self.meet_conditions()
          self.bar_context['portfolio_conditions'] = len(self.active_portfolio()) == 0
          self.bar_context['daily_pnl_conditions'] = self.realized_pnl() > self.max_daily_lose

          print(self.bar_context)
          if (self.bar_context['trade_conditions'] and
              self.bar_context['portfolio_conditions'] and
              self.bar_context['daily_pnl_conditions']):

            self.trigger_order()

  def build_bar_context(self):
    bar = self.current_bar
    sma20 = self.calculate_sma(periods=19)
    delta = round(bar.close - bar.open, 2)
    delta_win = (1.1 / 100.0) * bar.open
    delta_lose = delta_win / 2
    order_type = 'SELL' if delta < 0 else 'BUY'
    stop_lose = bar.close + delta_lose if delta < 0 else bar.close - delta_lose
    take_profit = bar.close - delta_win if delta < 0 else bar.close + delta_win
    ticks_to_lose = round(abs(bar.close - stop_lose), 2)
    ticks_to_win = round(abs(bar.close - take_profit), 2)

    shares = round(30000 / bar.open * 2)

    return {
        "sma20": sma20,
        "delta": delta,
        "order_type": order_type,
        "shares": shares,
        'date': str(bar.date),
        "price": bar.close,
        "stop_lose": round(stop_lose, 2),
        "take_profit": round(take_profit, 2),
        "ticks_to_lose": ticks_to_lose,
        "ticks_to_win": ticks_to_win,
        "volume": bar.volume
    }
