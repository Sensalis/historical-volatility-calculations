import ccxt

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
    
    # Print OHLCV data
    print(f'OHLCV data for {exchange_timeframe} timeframe:')
    for data in ohlcv:
        print(data)

# Note: Adjust the output format as per your requirement. OHLCV data consists of timestamps, open, high, low, close, and volume.
