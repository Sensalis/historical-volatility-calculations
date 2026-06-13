import datetime as dt
import pandas as pd
import numpy as np
import calendar
import yfinance as yf
import math
import matplotlib.pyplot as plt

cal2 = calendar.month(2024, 6)
symbol = "^AXJO"

# Fetch historical data

# Get the current date
end = dt.date.today().strftime('%Y-%m-%d')
end_obj = dt.datetime.strptime(end, '%Y-%m-%d')
# Set the start date
start = '2021-01-01'
start_obj = dt.datetime.strptime(start, '%Y-%m-%d')

stock_data = yf.download(symbol, start=start, end=end)
periods = [20, 60, 120, 180, 240]

def parkinson_volatility(stock_data, periods=[20, 60, 120, 180, 240]):
    """
    Calculates the Parkinson volatility estimator using the high and low prices.

    Args:
        stock_data (pandas.DataFrame): A DataFrame containing the 'High' and 'Low' columns.
        periods (list): The number of trading day periods to calculate the volatility over. Default is [20, 60, 120, 180, 240].

    Returns:
        pandas.DataFrame: A DataFrame containing the Parkinson volatility estimator for each period.
    """

    # Calculate the log of the high-low ratio
    hl_ratios = np.log(stock_data['High'] / stock_data['Low'])

    # Create an empty dictionary to store the results
    parkinson_vol = {}

    for period in periods:
        # Calculate the sum of the squared log ratios
        squared_hlratios = hl_ratios.rolling(window=period).apply(lambda x: (x ** 2).sum())

        # Calculate the Parkinson volatility estimator
        parkinson_vol[f'Parkinson_vol_{period}'] = squared_hlratios.apply(lambda x: np.sqrt(x / (4 * period * math.log(2)))*math.sqrt(252))
    # annualize the volatility estimator 
    parkinson_vol_df = pd.DataFrame(parkinson_vol)
    return parkinson_vol_df

# Calculate Parkinson volatility
parkinson_vol_df = parkinson_volatility(stock_data, periods)

DTE = [int(30*n) for n in [1,3,6,9,12]]

# Create a DataFrame to store the statistics
statistics_df = pd.DataFrame()

# Calculate the minimum value for each column
statistics_df['Minimum'] = parkinson_vol_df.min()

# Calculate the maximum value for each column
statistics_df['Maximum'] = parkinson_vol_df.max()

# Calculate the average value for each column
statistics_df['Average'] = parkinson_vol_df.mean()

# Get the latest data for each column
statistics_df['Latest'] = parkinson_vol_df.iloc[-1]

print(statistics_df)

# Create Volatility cone
plt.figure(figsize=(10, 6))

# Plot the minimum values
plt.plot(DTE, statistics_df['Minimum'], label='Minimum')

# Plot the maximum values
plt.plot(DTE, statistics_df['Maximum'], label='Maximum')

# Plot the average values
plt.plot(DTE, statistics_df['Average'], label='Average')

# Plot the latest values
plt.plot(DTE, statistics_df['Latest'], label='Latest')

# Set the x-axis label
plt.xlabel('Days for Calculation')

# Set the y-axis label
plt.ylabel('Volatility in %')

# Set the title
plt.title('Annualised Parkinson Volatility Cone')

# Add a legend
plt.legend()

# Show the plot
plt.show()


# Export stock_data to CSV
stock_data.to_csv('stock_data.csv', index=False)