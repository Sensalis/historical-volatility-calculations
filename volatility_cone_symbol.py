import datetime as dt
import pandas as pd
import numpy as np
import calendar
import yfinance as yf
import math

from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

cal2 = calendar.month(2024, 5)
symbol = "^AXJO"

# Fetch historical data

# Get the current date
end = dt.date.today().strftime('%Y-%m-%d')
end_obj = dt.datetime.strptime(end, '%Y-%m-%d')
# Set the start date
start = '2020-01-02'
start_obj = dt.datetime.strptime(start, '%Y-%m-%d')

stock_data = yf.download(symbol, start=start, end=end)

tradingDays=[20,60,120,180,240]

def parkinson_volatility(stock_data, periods=tradingDays):
    """
    Calculates the Parkinson volatility estimator using the high and low prices.
    
    Args:
        data (pandas.DataFrame): A DataFrame containing the 'High' and 'Low' columns.
        period (int): The number of trading days to calculate the volatility over.
        
    Returns:
        float: The Parkinson volatility estimator.
    """
 
    
    
    # Calculate the log of the high-low ratio
    hl_ratios = (stock_data['High'] / stock_data['Low']).apply(math.log)
    
#Create an empty dictionary to store the results  
    hl_ratios_dict = {}

        # Loop through each period
    for period in periods:
        # Calculate (1 / period) * hl_ratios
        hl_ratios_dict[f'hl_ratio_{period}'] = (1 / period) * hl_ratios

# Create a new DataFrame from the dictionary
    hl_ratios_df = pd.DataFrame(hl_ratios_dict)
    
    # Calculate the sum of the squared log ratios
    sum_squared_ratios = (hl_ratios_df ** 2)
#    sum_squared_ratios.to_excel('my_data.xlsx', index=False)
    #sum_squared_ratios = (hl_ratios_df ** 2).sum()
    df = pd.DataFrame(sum_squared_ratios)

    for period in periods:
        col_name = f'Rolling_Sum_{period}'
        df[col_name] = sum_squared_ratios[f'hl_ratio_{period}'].rolling(window=period).sum()
    # Calculate the Parkinson volatility estimator
    parkinson_vol = {}
    for period in periods:
        parkinson_vol[period] = sum_squared_ratios[f'hl_ratio_{period}'].astype(float).rolling(window=period).apply(lambda s: math.sqrt(s.sum) / (4 * math.log(2)))


## Compute log returns and historical trailing volatility

#volatility = log_returns.rolling(window=TRADING_DAYS).std() * np.sqrt(252)  # Specify window size correctly

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

dates = [ThirdThurs(year, month) for year in range(start_obj.year, end_obj.year+1) for month in range(1, 13) if ThirdThurs(year, month) < dt.datetime.now().date()]
columnsNames = ['1-mth', '3-mth', '6-mth', '9-mth', '12-mth']

DTE = [int(30 * n) for n in [1, 3, 6, 9, 12]]
data = np.array([np.arange(len(dates))] * len(columnsNames)).T
# data data frame with dates as index and columnsNames as columns, not populated with data
volatility = {}
# Populate volatility data frame with symbol-specific data
for TRADING_DAYS, TimePeriod in zip(tradingDays, columnsNames):
    print(TRADING_DAYS, TimePeriod)
    volatility[TimePeriod] = log_returns.rolling(window=TRADING_DAYS).std() * np.sqrt(252)

#    # Initialize historical_volatility_df with columns
#    historical_volatility_df = pd.DataFrame(columns=columnsNames)
#
#    # Modify the historical_vol function to populate historical_volatility_df correctly
#    def historical_vol(x):
#        df2 = pd.Series(index=columnsNames)
#        for idx in historical_volatility_df.index:
#            try:
#                df2[idx] = round(volatility[x].loc[idx] * 100, 2)  # Use x instead of historical_volatility_df.name
#            except KeyError:
#                df2[idx] = np.nan
#        return df2

#   # Apply the historical_vol function to calculate symbol-specific historical volatility
#   historical_volatility_df = historical_volatility_df.apply(lambda x: historical_vol(x), axis=0)  # Use lambda function to pass x

historical_volatility_df = pd.DataFrame(data, columns=columnsNames, index=dates)
historical_volatility_df.index.name = 'period'

def historical_vol(x):
    df2 = x.copy()
    for date, val in x.iteritems():
        try:
            df2.loc[date] = round(volatility[x.name].loc[date,symbol]*100,2)
        except:
            df2.loc[date] = np.nan
    return df2


historical_volatility_df = historical_volatility_df.apply(lambda x: historical_vol(x), axis=0)

df2 = pd.DataFrame(data='', columns=['max','mean','min'], index=DTE)
df2.index.name = 'DTE'


df2['max'] = pd.Series(historical_volatility_df[columnsNames].max().values, index=DTE)
df2['mean'] = pd.Series(historical_volatility_df[columnsNames].mean().values, index=DTE)
df2['min'] = pd.Series(historical_volatility_df[columnsNames].min().values, index=DTE)

fig1 = plt.figure(figsize=(12,8))
ax1 = fig1.add_subplot(111)

plt.plot(df2.index, df2['max'], 'k+-')
plt.plot(df2.index, df2['mean'], 'ms-')

plt.plot(df2.index, historical_volatility_df.iloc[-1,:], 'gs-')

plt.plot(df2.index, df2['min'], 'k+-')

for i, v in df2['mean'].iteritems():
    ax1.text(i, v+1, "%d" %v, ha="center")
for i, v in enumerate(historical_volatility_df.iloc[-1,:]):
    ax1.text(df2.index[i], v-2.5, "%d" %v, ha="center")

plt.title('Historical Volatility Cone vs. Implied volatility')
plt.legend(['max', 'mean', 'current','min' ], loc='upper right')

plt.xlabel('Days to Expiry (DTE)')
plt.ylabel('Volatility (%)')
plt.xticks(np.linspace(0,360,13))
plt.ylim(0, 70)
plt.xlim(0, 370)