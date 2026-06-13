import datetime as dt
import pandas as pd
import numpy as np
import calendar
import yfinance as yf
import math
import matplotlib.pyplot as plt

symbol = "^AXJO"

# Fetch historical data
end = dt.date.today().strftime('%Y-%m-%d')
start = '2020-01-02'

stock_data = yf.download(symbol, start=start, end=end)

def parkinson_volatility(stock_data, periods=[20, 60, 120, 180, 240]):
    hl_ratios = np.log(stock_data['High'] / stock_data['Low'])
    parkinson_vol = {}
    for period in periods:
        squared_hlratios = hl_ratios.rolling(window=period).apply(lambda x: (x ** 2).sum())
        parkinson_vol[f'Parkinson_vol_{period}'] = np.sqrt(squared_hlratios / (4 * period * np.log(2)))
    return pd.DataFrame(parkinson_vol)

def ThirdThurs(year, month):
    daysInMonth = calendar.monthrange(year, month)[1]
    date = dt.date(year, month, daysInMonth)
    offset = 4 - date.isoweekday()
    if offset > 0:
        offset -= 7
    date += dt.timedelta(offset)
    return date - dt.timedelta(7)

start_obj = dt.datetime.strptime(start, '%Y-%m-%d')
end_obj = dt.datetime.strptime(end, '%Y-%m-%d')

dates = [ThirdThurs(year, month) for year in range(start_obj.year, end_obj.year + 1) 
         for month in range(1, 13) if ThirdThurs(year, month) < dt.datetime.now().date()]

columnsNames = ['1-mth', '3-mth', '6-mth', '9-mth', '12-mth']
DTE = [int(30 * n) for n in [1, 3, 6, 9, 12]]

volatility = {}
for TRADING_DAYS, TimePeriod in zip(DTE, columnsNames):
    volatility[TimePeriod] = stock_data['Close'].pct_change().rolling(window=TRADING_DAYS).std() * np.sqrt(252)

historical_volatility_df = pd.DataFrame(index=dates, columns=columnsNames)
historical_volatility_df.index.name = 'period'

def historical_vol(x):
    df2 = x.copy()
    for date in x.index:
        try:
            df2.loc[date] = round(volatility[x.name].loc[date] * 100, 2)
        except KeyError:
            df2.loc[date] = np.nan
    return df2

historical_volatility_df = historical_volatility_df.apply(lambda x: historical_vol(x), axis=0)

df2 = pd.DataFrame(columns=['max', 'mean', 'min'], index=DTE)
df2.index.name = 'DTE'

df2['max'] = historical_volatility_df[columnsNames].max().values
df2['mean'] = historical_volatility_df[columnsNames].mean().values
df2['min'] = historical_volatility_df[columnsNames].min().values

fig1 = plt.figure(figsize=(12, 8))
ax1 = fig1.add_subplot(111)

plt.plot(df2.index, df2['max'], 'k+-', label='max')
plt.plot(df2.index, df2['mean'], 'ms-', label='mean')
plt.plot(df2.index, historical_volatility_df.iloc[-1, :], 'gs-', label='current')
plt.plot(df2.index, df2['min'], 'k+-', label='min')

for i, v in df2['mean'].items():
    ax1.text(i, v + 1, f"{v:.0f}", ha="center")
for i, v in enumerate(historical_volatility_df.iloc[-1, :]):
    ax1.text(df2.index[i], v - 2.5, f"{v:.0f}", ha="center")

plt.title('Historical Volatility Cone vs. Implied volatility')
plt.legend(loc='upper right')
plt.xlabel('Days to Expiry (DTE)')
plt.ylabel('Volatility (%)')
plt.xticks(np.linspace(0, 360, 13))
plt.ylim(0, 70)
plt.xlim(0, 370)

plt.show()
