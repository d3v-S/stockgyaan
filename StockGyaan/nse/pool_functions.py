from nse.data.candlestick import ohlcListOfDF
from nse.data.options.optionchain_ import optionsData
from nse.data.options.optionsummary_ import getFuturesSummaryIndex
from common.utils_ import statusError, statusSubmitted
from nse.data.stocks.nse_ import validateNameFromNse, getQuote


def validateNseName(name):
    return validateNameFromNse(name)

def downloadCurrentData(nse_name, status_dict=None):
    statusSubmitted(status_dict)
    return getQuote(nse_name)

def downloadOptionsData(symbol, status_dict=None):
    try:
        statusSubmitted(status_dict)
        return optionsData(symbol)
    except:
        statusError(status_dict, "error downloading options data")
        return None

def downloadCandlesticksData(symbol, status_dict=None):
    ret  = validateNseName(symbol)
    statusSubmitted(status_dict)
    if ret is not None:
        (nse, symbol_type) = ret
        ldf  = ohlcListOfDF(symbol=symbol, symbol_type=symbol_type, timeframes=[3,5,7,15,30,60])
        return ldf





def downloadDailyImage(symbol):
    pass


def downloadOptionDelta():
    pass

def processOptionsData(symbol):
    return optionsData(symbol)


def processDataframesForIndicators():
    pass

def processCandlesticksData():
    pass
