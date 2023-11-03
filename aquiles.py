from ib_insync import *
from back_testing import BackTesting

class AquilesBot(IB, BackTesting):
    """docstring for AquilesBot"""
    def __init__(self, stock):
        super(AquilesBot, self).__init__()
        self.stock = Stock(stock, 'SMART', 'USD')
        self.active_order = None
        self.wins = 0
        self.loses = 0
        self.amount_win = 0
        self.amount_lose = 0

    def init_data(self):
        self.connect('127.0.0.1', 4002, clientId=1)
        self.bars = self.reqHistoricalData(
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

    def set_currents(self, index=-2):
        self.current_bar = self.bars[index]
        # self.current_bar_index = self.bars.index(self.current_bar)
        self.current_bar_index = index
        self.bar_context = self.build_bar_context()

    def echo_currents(self):
        print("Current Bar[%s] %s" %(self.current_bar_index, self.current_bar))
        print('Bar Context: %s' %(self.bar_context))

    def on_bar_update(self, bars, has_new_bar):
        if has_new_bar:
            self.current_bar = bars[-2]
            self.current_bar_index = self.bars.index(self.current_bar)
            self.bar_context = self.build_bar_context()
            self.process_bar()

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

    def process_bar(self):
        if (self.current_bar_index >= 195 and
            self.active_order == None and
            self.meet_conditions()):
            self.active_order = self.bar_context

        elif self.active_order != None:
            self.analyze_active_order()

    def trigger_order():
        orders = self.bracketOrder(
            self.bar_context['order_type'],
            self.bar_context['shares'],
            self.bar_context['price'],
            self.bar_context['take_profit'],
            self.bar_context['stop_lose']
        )
        for order in orders:
            self.placeOrder(self.stock, order)

    def meet_conditions(self):
        acceptable_sma20_price_distance = 0.35
        acceptable_sma20_sm200_distance = 0.35
        acceptable_delta = 0.30
        acceptable_volume = 200000

        sma20 = self.bar_context['sma20']
        sma200 = self.bar_context['sma200']

        return (abs(self.bar_context['delta']) >= acceptable_delta and
                abs(self.current_bar.open - sma20) <= acceptable_sma20_price_distance and
                self.current_bar.volume >= acceptable_volume and
                self.bar_context['ticks_to_lose'] <= 0.5 and
                abs(self.bar_context['delta_20_200']) <= acceptable_sma20_sm200_distance)

    def build_bar_context(self):
        bar = self.current_bar
        sma20 = self.calculate_sma(periods=19)
        sma200 = self.calculate_sma(periods=195)
        delta = round(bar.close - bar.open, 2)
        delta_20_200 = round(sma20 - sma200, 2)

        order_type = 'SELL' if delta < 0 else 'BUY'
        stop_lose = bar.high if delta < 0 else bar.low
        take_profit = bar.close - 1.1 if delta < 0 else bar.close + 1.1
        ticks_to_lose = round(abs(bar.close - stop_lose), 2)
        ticks_to_win = round(abs(bar.close - take_profit), 2)

        return {
            "sma20": sma20,
            "sma200": sma200,
            "delta": delta,
            "delta_20_200": delta_20_200,
            "order_type": order_type,
            "shares": 900,
            'date': str(bar.date),
            "price": bar.close,
            "stop_lose": stop_lose,
            "take_profit": take_profit,
            "ticks_to_lose": ticks_to_lose,
            "ticks_to_win": ticks_to_win
        }
