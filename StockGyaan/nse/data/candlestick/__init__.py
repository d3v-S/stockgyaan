from datetime import date, timedelta
from common.utils_ import statusError, statusFinished, statusStarted, STRING_DOWNLOAD_ERROR, STRING_DOWNLOAD_FINISHED, STRING_DOWNLOAD_STARTED

from nse.data.candlestick.moneycontrol_economictimes_ import ohlcDF_MC, ohlcDF_ET, perMinute_MoneyControl
from nse.data.candlestick.yahoofinance_ import ohlcDF_YF 

def getToday():
    today = date.today()
    return today.strftime("%Y-%m-%d")


def getFewsDaysBack(num_days=7):
    today = date.today()
    weeks_ago = today - timedelta(days=num_days)
    return weeks_ago.strftime("%Y-%m-%d")


# default : send last 14 days back data.

def ohlcListOfDF(source ="mc",
                 symbol="BANKNIFTY",
                 symbol_type="index",
                 start=None,
                 end=None,
                 timeframes=[], num_days=10, status_dict=None):
    if end is None:
        end = getToday()

    if start is None:
        start = getFewsDaysBack(num_days)

    list_df = []
    if source == "mc":
        statusStarted(status_dict, STRING_DOWNLOAD_STARTED.format(symbol=symbol, source=source))
        arr_json = perMinute_MoneyControl(symbol, symbol_type, start, end)
        if arr_json is None:
            statusError(status_dict, STRING_DOWNLOAD_ERROR.format(symbol=symbol, source=source))
            return None
        for tf in timeframes:
            df = ohlcDF_MC(symbol, symbol_type, start, end, tf, arr_json=arr_json)
            list_df.append(df)
        statusFinished(status_dict, STRING_DOWNLOAD_FINISHED.format(symbol=symbol, source=source))
        return list_df
    return None



