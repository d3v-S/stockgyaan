
from nsepython import *
from flatten_json import flatten
from common.utils_ import statusError, statusFinished, statusStarted
from common.utils_ import STRING_DOWNLOAD_STARTED, STRING_DOWNLOAD_ERROR, STRING_DOWNLOAD_FINISHED


class OI:
    oi_df_keys =    [   'strikePrice',
                        'expiryDate',
                        'CE_lastPrice',
                        'PE_lastPrice',
                        'CE_openInterest',
                        'PE_openInterest',
                        'CE_changeinOpenInterest',
                        'PE_changeinOpenInterest',
                        'CE_totalBuyQuantity',
                        'PE_totalBuyQuantity',
                        'CE_totalSellQuantity',
                        'PE_totalSellQuantity',
                        'CE_totalTradedVolume',
                        'PE_totalTradedVolume',
                        'CE_impliedVolatility',
                        'PE_impliedVolatility'
                ]

    oi_df_partial_key = [   'openInterest',
                            'changeinOpenInterest',
                            'totalBuyQuantity',
                            'totalSellQuantity',
                            'totalTradedVolume',
                            'impliedVolatility',
                            'lastPrice',
                ]
    @classmethod
    def __getJsonData(cls, symbol='BANKNIFTY'):
        return nse_optionchain_scrapper(symbol)
        
    @classmethod
    def __optionsData(cls, oi_json, expiry=None,):
        if expiry is None:
            expiry = oi_json['records']['expiryDates'][0] # nearest date.
        
        data = oi_json['records']['data']
        filtered_arr=[]
        for item in data:
            if item['expiryDate'] != expiry:
                continue
            fj = flatten(item)
            filtered_arr.append(fj)
        return sorted(filtered_arr, key=lambda i: i['strikePrice'])
    

    @classmethod
    def optionsDataInDataFrame(cls, filtered_arr=None, expiry=None, symbol="BANKNIFTY"):
        if filtered_arr == None:
            filtered_arr = cls.__optionsData(cls.__getJsonData(symbol), expiry=expiry)
        df = pd.json_normalize(filtered_arr)
        return df[cls.oi_df_keys]

    @classmethod
    def optionsDataInDataFrameWithoutKey(cls, filtered_arr=None, expiry=None, symbol="BANKNIFTY"):
        if filtered_arr == None:
            filtered_arr = cls.__optionsData(cls.__getJsonData(symbol), expiry=expiry)
        df = pd.json_normalize(filtered_arr)
        return df

    @classmethod
    def findTopNFromDF(cls, df, key, n):
        top_n = df[key].nlargest(n)
        return df[df[key].isin(top_n)]

    @classmethod
    def findTopNStrikePrice(cls, df, key, n):
        df = cls.findTopNFromDF(df, key, n)
        strike_price = df['strikePrice'].tolist()
        key_val = df[key].tolist()
        return list(zip(strike_price, key_val))

    @classmethod
    def findStrikePrice(cls, df, partial_key, n):
        key1 = "CE_" + partial_key
        key2 = "PE_" + partial_key
        ce = cls.findTopNStrikePrice(df, key1, n)
        pe = cls.findTopNStrikePrice(df, key2, n)
        return (ce, pe)

    @classmethod
    def optionsDataSummary(cls, oi_df, n):
        d = {}
        for k in cls.oi_df_partial_key:
            d[k] = cls.findStrikePrice(oi_df, k, n)
        return d

    @classmethod
    def checkFnOSymbol(cls, symbol):
        if symbol.upper() in fnolist():
            return symbol.upper()
        if symbol.upper() == "NIFTY 50":
            return "NIFTY"
        if symbol.upper() == "NIFTY FIN SERVICE":
            return "FINNIFTY"
        if "NIFTY" in symbol.upper():
            new_sym = symbol.upper().replace("NIFTY", "").strip()
            for sym in fnolist():
                if "NIFTY" in sym:
                    if new_sym in sym:
                        return sym.upper();
        return None


    @classmethod
    def futurePrice(cls, symbol, expiry="latest"):
        sym = cls,checkFnOSymbol(symbol)
        if sym is not None:
            return nse_quote_ltp(sym, expiry, "Fut")
        return None


    
### 
# options data api: https://forum.unofficed.com/t/nsepython-documentation/376/18
###    

def checkFnOSymbol(symbol):
    return OI.checkFnOSymbol(symbol)



def optionsData(symbol="BANKNIFTY", expiry=None, status_dict=None):
    """get options chain data in dataframe

    Args:
        symbol (str, optional): NSE-Symbol. Defaults to "BANKNIFTY".
        expiry (str, optional): format = "12-May-2021". Defaults to None.

    Returns:
        dataframe: optionchain data in dataframe. can be directly shown in a table.
    """
    sym = checkFnOSymbol(symbol)
    statusStarted(status_dict, STRING_DOWNLOAD_STARTED.format(symbol=sym, source="nse"))
    if sym is None:
        statusError(status_dict, STRING_DOWNLOAD_ERROR.format(symbol=sym, source="nse"))
        return None
    ldf =  OI.optionsDataInDataFrame(symbol=sym, expiry=expiry)
    statusFinished(status_dict, STRING_DOWNLOAD_FINISHED.format(symbol=sym, source="nse"))
    return ldf



def optionsDataWithoutKeys(symbol="BANKNIFTY", expiry=None, status_dict=None):
    """get options chain data in dataframe

    Args:
        symbol (str, optional): NSE-Symbol. Defaults to "BANKNIFTY".
        expiry (str, optional): format = "12-May-2021". Defaults to None.

    Returns:
        dataframe: optionchain data in dataframe. can be directly shown in a table.
    """
    sym = checkFnOSymbol(symbol)
    statusStarted(status_dict, STRING_DOWNLOAD_STARTED.format(symbol=sym, source="nse"))
    if sym is None:
        statusError(status_dict, STRING_DOWNLOAD_ERROR.format(symbol=sym, source="nse"))
        return None
    ldf =  OI.optionsDataInDataFrameWithoutKey(symbol=sym, expiry=expiry)
    statusFinished(status_dict, STRING_DOWNLOAD_FINISHED.format(symbol=sym, source="nse"))
    return ldf




def optionsKeys():
    return OI.oi_df_keys

def optionsPartialKeys():
    return OI.oi_df_partial_key

def optionsDataTopN(df, key, n):
    return OI.findTopNFromDF(df, key, n)



