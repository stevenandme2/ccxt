import backtrader as bt
import pandas as pd
import numpy as np

# Load your data
pepe_data = pd.read_csv('OKX_PEPEUSDT_3.csv')
pepe_data['time'] = pd.to_datetime(pepe_data['time'])
pepe_data.set_index('time', inplace=True)

class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('length', 20),
        ('mult', 2.0),
        ('direction', 0),  # 0: all, -1: short, 1: long
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(self.data.close, 
                                                 period=self.params.length, 
                                                 devfactor=self.params.mult)

    def next(self):
        if self.params.direction >= 0 and self.data.close < self.boll.lines.bot:
            if not self.position or self.position.size < 0:
                self.close()  # Close short positions
                self.buy(size=1)
        if self.params.direction <= 0 and self.data.close > self.boll.lines.top:
            if not self.position or self.position.size > 0:
                self.close()  # Close long positions
                self.sell(size=1)

# Function to perform optimization
def run_optimization():
    optimization_results = []
    length_range = range(10, 31, 5)
    mult_range = np.arange(1.5, 3.1, 0.5)
    directions = [0, 1, -1]
    
    for length in length_range:
        for mult in mult_range:
            for direction in directions:
                cerebro = bt.Cerebro()
                cerebro.addstrategy(BollingerBandsStrategy, length=length, mult=mult, direction=direction)
                cerebro.adddata(bt.feeds.PandasData(dataname=pepe_data))
                cerebro.broker.setcash(1000.0)  # Initial cash
                cerebro.run()
                
                net_profit = cerebro.broker.getvalue() - 1000.0
                optimization_results.append((length, mult, direction, net_profit))

    results_df = pd.DataFrame(optimization_results, columns=['Length', 'Multiplier', 'Direction', 'Net Profit'])
    return results_df

# Run optimization and find best parameters
results_df = run_optimization()
best_result = results_df.loc[results_df['Net Profit'].idxmax()]

print("Best Parameters:")
print(best_result)

