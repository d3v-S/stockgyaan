from datetime import date

import yfinance


# downloading data from Yahoo finance
def _downloadDataFromYF(symbol="^NSEBANK",
                         symbol_type="index",
                         start="2021-04-27",
                         end="2021-04-27",
                         period=None,
                         interval="1m"):
    if period is None:
        try:
            df = yfinance.download(symbol, start=start, end=end, interval=interval)
        except:
            return None
    else:
        try:
            df = yfinance.download(symbol, period=period, interval=interval)
        except:
            return None
    return df



# per minute dataframe from yahoo finance
def ohlcDF_YF(symbol="^NSEBANK",
             symbol_type="index",      # compatibility purpose
             start="2021-04-27",
             end=None,
             timeframe=1):
    if end == None:
        today = date.today()
        end = today.strftime("%Y-%m-%d")
    timeframe=str(timeframe) + "m"
    df = _downloadDataFromYF(symbol, start=start, end=end, interval=timeframe)
    if df is None:
        return None
    return df
