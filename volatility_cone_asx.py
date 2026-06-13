import datetime as dt
import pandas as pd
import numpy as np
import calendar
import re
import yfinance as yf

from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

cal2 = calendar.month(2024, 4)
symbol = '^GSPC'

# Fetch historical data
end = dt.datetime.now()
start = dt.datetime(2022, 1, 2)

stock_data = yf.download(symbol, start=start, end=end)

# Check if the response is valid
if stock_data is not None:
    Close = stock_data.Close

    # Compute log returns and historical trailing volatility
    log_returns = np.log(stock_data.Close / stock_data.Close.shift(1))
    log_returns = log_returns.replace([np.inf, -np.inf], np.nan).dropna()  # Handle division by zero
    TRADING_DAYS = 20
    volatility = log_returns.rolling(window=TRADING_DAYS, min_periods=1).std() * np.sqrt(252)  # Specify window size correctly

    # Create Historical Volatility Cones
    def ThirdThurs(year, month):
        # Create a datetime.date for the last day of the given month
        daysInMonth = calendar.monthrange(year, month)[1]
        date = dt.date(year, month, daysInMonth)
        offset = 4 - date.isoweekday()
        if offset > 0:
            offset -= 7
        date += dt.timedelta(offset)
        
        now = dt.date.today()
        if date.year == now.year and date.month == now.month and date < now:
            raise Exception('Missed third Thursday')

        return date - dt.timedelta(7)

    dates = [ThirdThurs(year, month) for year in range(2020, 2024) for month in range(1, 13) if ThirdThurs(year, month) <= dt.datetime.now().date()]

    columnsNames = ['1-mth', '3-mth', '6-mth', '9-mth', '12-mth']
    tradingDays = [int(20 * n) for n in [1, 3, 6, 9, 12]]
    DTE = [int(30 * n) for n in [1, 3, 6, 9, 12]]
    data = np.array([np.arange(len(dates))] * len(columnsNames)).T

    volatility = {}
    for TRADING_DAYS, TimePeriod in zip(tradingDays, columnsNames):
        volatility[TimePeriod] = log_returns.rolling(window=TRADING_DAYS, min_periods=1).std() * np.sqrt(252)  # Specify window size correctly

    historical_volatility_df = pd.DataFrame(data, columns=columnsNames, index=dates)
    historical_volatility_df.index.name = 'period'

    def historical_vol(x):
        df2 = x.copy()
        for date, val in x.iteritems():
            try:
                df2.loc[date] = round(volatility[x.name].loc[date, symbol] * 100, 2)
            except:
                df2.loc[date] = np.nan
        return df2

    historical_volatility_df = historical_volatility_df.apply(lambda x: historical_vol(x), axis=0)

    df2 = pd.DataFrame(data='', columns=['max', 'mean', 'min'], index=DTE)
    df2.index.name = 'DTE'

    df2['max'] = pd.Series(historical_volatility_df[columnsNames].max().values, index=DTE)
    df2['mean'] = pd.Series(historical_volatility_df[columnsNames].mean().values, index=DTE)
    df2['min'] = pd.Series(historical_volatility_df[columnsNames].min().values, index=DTE)

    fig1 = plt.figure(figsize=(12, 8))
    ax1 = fig1.add_subplot(111)

    plt.plot(df2.index, df2['max'], 'k+-')
    plt.plot(df2.index, df2['mean'], 'ms-')
    plt.plot(df2.index, historical_volatility_df.iloc[-1, :], 'gs-')
    plt.plot(df2.index, df2['min'], 'k+-')

    for i, v in df2['mean'].iteritems():
        ax1.text(i, v + 1, "%d" % v, ha="center")
    for i, v in enumerate(historical_volatility_df.iloc[-1, :]):
        ax1.text(df2.index[i], v - 2.5, "%d" % v, ha="center")

    plt.title('Historical Volatility Cone vs. Implied volatility')
    plt.legend(['max', 'mean', 'current', 'min'], loc='upper right')
    plt.xlabel('Days to Expiry (DTE)')
    plt.ylabel('Volatility (%)')
    plt.xticks(np.linspace(0, 360, 13))
    plt.ylim(0, 70)
    plt.xlim(0, 370)

    plt.show()
else:
    print("Failed to fetch data from Yahoo Finance.")
