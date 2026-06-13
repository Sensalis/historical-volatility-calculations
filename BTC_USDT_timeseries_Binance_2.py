import ccxt
import pandas as pd

# Create Binance exchange instance
exchange = ccxt.binance()

# Define symbol (BTC/USDT)
symbol = 'BTC/USDT'

# Define timeframes
timeframes = ['1d', '1h', '15m', '5m']

# Download data for each timeframe
for tf in timeframes:
    # Set timeframe
    exchange_timeframe = tf
    
    # Fetch OHLCV (Open/High/Low/Close/Volume) data
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=exchange_timeframe)
    
    # Convert OHLCV data to dataframe
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Print dataframe
    print(f'Dataframe for {exchange_timeframe} timeframe:')
    print(df)

# Note: Adjust the output format as per your requirement. The dataframe contains columns for timestamp, open, high, low, close, and volume.
