import io

import requests, json, pandas as pd, time, math
import datetime
import yfinance
from datetime import date
from nsetools import Nse
from bs4 import BeautifulSoup as bs


class CandleStickDataStream:
    
    sources = ["et", "mc"]
    
    # datetime format:
    datetime_format = "%Y-%m-%d %H:%M"
    
    # economic times
    et_index_url = "https://ettechcharts.indiatimes.com/ETLiveFeedChartRead/livefeeddata?scripcode={symbol}&exchangeid=50&datatype=intraday&filtertype={timeframe}&firstreceivedataid={end}+15%3A30&lastreceivedataid={start}+9%3A15&directions=all&callback=serviceHit.chartResultCallback&scripcodetype=company"
    et_stock_url = "https://ettechcharts.indiatimes.com/ETLiveFeedChartRead/livefeeddata?scripcode={symbol}EQ&exchangeid=50&datatype=intraday&filtertype={timeframe}&firstreceivedataid={end}+15%3A30&lastreceivedataid={start}+9%3A15&directions=all&callback=serviceHit.chartResultCallback&scripcodetype=company"
    
    
    # moneycontrol
    mc_index_url = "https://priceapi.moneycontrol.com/techCharts/history?symbol={symbol}&resolution={timeframe}&from={start}&to={end}"
    mc_stock_url = "https://priceapi.moneycontrol.com/techCharts/techChartController/history?symbol={symbol}&resolution={timeframe}&from={start}&to={end}"
    mc_index_code = []

    # common_error:
    err_timeout = {"err": "err_timeout"}
    err_response = {"err": "err_response"}

    # commmon input to website specific format
    
    # symbol = symbol.
    # sumbol_type = ["index", "eq"]
    # timeframe = ["1", "5", "15", ] like this.
    # start = "date 9:15"
    # end = "date 3:31"

    
    @classmethod
    def __ETParamsToUrl(cls, symbol, symbol_type, timeframe, start, end):
        url = None
        if symbol_type == "index":
            url = cls.et_index_url
        else:
            url = cls.et_stock_url
        # assume timeframe in 1 5 15:
        et_tf = str(timeframe)+"MIN"
        url = url.format(timeframe=et_tf, symbol=symbol, start=start, end=end)
        return url


    @classmethod
    def __MCIndexList(cls):
        url = "https://www.moneycontrol.com/markets/indian-indices/"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                soup = bs(res.text, 'html.parser')
                list_classes = soup.find_all(class_="ind_li")
                list_names = []
                for c in list_classes:
                    tup = (c.text, c.get('id').split("_")[1])   # (name, code)
                    list_names.append(tup)
                cls.mc_index_code = list_names
                return list_names
            return None
        except requests.exceptions.Timeout:
            return None


    @classmethod
    def __MCIndexToCode(cls, symbol):
        symbol = symbol.upper()
        if len(cls.mc_index_code) == 0:
            cls.__MCIndexList()
        symbol = symbol.replace("NIFTY", "").strip()
        for tup in cls.mc_index_code:
            sym = tup[0].replace("NIFTY", "").strip()
            if sym == symbol:
                return tup[1]
        return 9


    @classmethod
    def __MCParamsToUrl(cls, symbol, symbol_type, timeframe, start, end):
        url = None
        if symbol_type == "index":
            code = cls.__MCIndexToCode(symbol)  # assume it has NIFTY in name.
            symbol = str(code)                  # default is NIFTY 50
            url = cls.mc_index_url
        else:
            url = cls.mc_stock_url
        start_epoch = math.trunc(time.mktime(time.strptime(start + " 9:15", cls.datetime_format)))
        end_epoch = math.trunc(time.mktime(time.strptime(end + " 15:30", cls.datetime_format)))
        tf = "1" # there is no other than 1, in stocks it is 1, 3, 5, 15 etc.
        url = url.format(timeframe = tf, start=start_epoch, end=end_epoch, symbol=symbol)
        return url
    



    # common output from website specific format.
    # [{"Date": "2021-04-16 09:15", "Open":, "Close":, "High":, "Low":, "Volume":}, {}, {} ]

    @classmethod
    def __ETDataToJson(cls, et_data):
        j = et_data.split("quote")[1].split("]")[0].split("[")[1]
        new_j = '{"data":[' + j + ']}'
        parsed = json.loads(new_j)
        return parsed["data"][1:] # first one, if not historical will be wrong
    

    
    @classmethod
    def __MCDataToJson(cls, mc_data):
        #print("MCData: " + str(mc_data))
        j = json.loads(mc_data)
        #print(j)
        list_ = []
        epoch_time = j["t"][::-1]
        high = j["h"][::-1]
        low = j["l"][::-1]
        op = j["o"][::-1]
        close = j["c"][::-1]
        volume = j["v"][::-1]

        for i,t in enumerate(epoch_time):
            d = {}
            normal_time = datetime.datetime.fromtimestamp(t)
            d["Date"] = str(normal_time)[:(len(str(normal_time))-3)]
            d["High"] = high[i]
            d["Low"] = low[i]
            d["Open"] = op[i]
            d["Close"] = close[i]
            d["Volume"] = volume[i]

            list_.append(json.loads(json.dumps(d)))
        
        return list_
    

    @classmethod
    def getDataFromSource(cls, source="et", symbol="BANKNIFTY", symbol_type="index",  timeframe="1", start="2021-04-27", end="2021-04-27"):
        url = None
        if source == "et":
            url = cls.__ETParamsToUrl(symbol, symbol_type, timeframe, start, end)
        
        if source == "mc":
            if "&" in symbol:
                symbol = symbol.replace("&", "%26")
            url = cls.__MCParamsToUrl(symbol, symbol_type, timeframe, start, end)

        try:
            print("URL: " + url)
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                json_data = None
                if source == "et":
                    return cls.__ETDataToJson(res.text)
                
                if source == "mc":
                    return cls.__MCDataToJson(res.text)
            else:
                return None
        except requests.exceptions.Timeout:
            return None




class CandleStickUtils:
    
    # datetime format:
    datetime_format = "%Y-%m-%d %H:%M"
    
    @classmethod
    def jsonToCSV(cls, arr_json, filename=None):
        df = pd.json_normalize(arr_json)
        if filename == None:
            df.to_csv("test.csv", index=None)
            return "test.csv"
        df.to_csv(filename, index=None)
        return filename


    # giving direct DF converted by normalize is having issues
    # remove the same filename for everything.
    @classmethod
    def jsonToCSVToDF(cls, arr_json):
        s_buf = io.StringIO()
        cls.jsonToCSV(arr_json, s_buf)
        s_buf.seek(0)
        dateparse = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M')
        df = pd.read_csv(s_buf, index_col= 'Date', parse_dates=['Date'], date_parser=dateparse).sort_index()
        s_buf.close()
        return df
    
    
     # ###################################################################
    #
    # merge candles:    (works best with mc)
    #                   (some skips in ET)
    #
    # ####################################################################
    
    # return OHLCV
    @classmethod
    def __mergeNCandleData(cls, arr_json, n, start):
        high_all = []
        low_all = []
        volume = 0
        for i in range(0, n):
            high_all.append(arr_json[start + i]["High"])
            low_all.append(arr_json[start + i]["Low"])
            volume = volume + arr_json[start + i]["Volume"]
        high = max(high_all)
        low = min(low_all)
        op = arr_json[start]["Open"]
        close = arr_json[start + n-1]["Close"]
        return (op, high, low, close, volume)
    

    # 
    # paritition arr_json into days:
    # 
    @classmethod
    def __partInDays(cls, arr_json):
        end = 0
        list_of_days = []
        for i in range(0, len(arr_json) - 1):
            d = arr_json[i]
            d_prev = arr_json[i + 1]
            time_curr = math.trunc(time.mktime(time.strptime(d["Date"], cls.datetime_format)))
            time_prev = math.trunc(time.mktime(time.strptime(d_prev["Date"], cls.datetime_format)))

            diff = abs(time_curr - time_prev) 
            if diff > 3600: # min diff = 1 min = 60 second in epoch. 6 hours = 6 * 60 * 60.
                interval = (i, end) # i > start. i -> start.
                list_of_days.append(interval)
                end = i + 1
        
        list_of_days.append((len(arr_json)-1, end)) # start -> len. (len > start.)
        return list_of_days
    
    # merge candles for one day:
    # arr_json = [0, 1, 2, 3 .. this wise time]
    # assume arr_json to be ascending in time, not descending.
    @classmethod
    def __mergeOneDayCandle(cls, asc_arr_json, window_size, start_index, end_index):
        new_arr_json = []
        index = 0
        for i in range(0, abs(start_index - end_index)):
            index = i
            if (i % window_size != 0):
                continue
            d = {}
            d["Date"] = asc_arr_json[i]["Date"]
            #print("D::" + str(d["Date"]))
            if (i + window_size) > (start_index - end_index):
                window_size = (start_index - end_index) - i
            r = cls.__mergeNCandleData(asc_arr_json, int(window_size), i) # starts from 0.
            d["Open"], d["High"], d["Low"], d["Close"], d["Volume"] = r
            j = json.loads(json.dumps(d))
            i = i + int(window_size)
            new_arr_json.append(j)
        return new_arr_json # returns ascending list of jsons.

    
    # merge complete arr_json
    @classmethod
    def mergeArrJsonToLargerTimeFrame(cls, arr_json, smaller_tf, larger_tf):
        list_of_days = cls.__partInDays(arr_json)
        new_arr_json = []
        for i in reversed(list_of_days):
            #print("date: " + str(arr_json[i[0]]["Date"]) + " -- " + str(arr_json[i[1]]["Date"]))
            asc_arr_json = arr_json[i[1]:i[0]+1][::-1] # +1 because it was missing 9:15 always.
            new_arr_json = new_arr_json + (cls.__mergeOneDayCandle(asc_arr_json, (larger_tf/smaller_tf), i[0], i[1]))
        return new_arr_json[::-1]



## ------------------------------------------------------------------------------------------------------



def _ohlcDataPerMin(source,
                    symbol="BANKNIFTY",
                    symbol_type="index",
                    start="2021-04-27",
                    end=None):
    """return data in specific format:

    Args:
        symbol (str, optional): mc-symbol / et-symbol. Defaults to "BANKNIFTY".
        symbol_type (str, optional): index or stock. Defaults to "index".
        timeframe (str, optional): [1, 3, 5, 15 ...]. Defaults to "1".
        start (str, optional): start date. format=2021-04-04. Defaults to "2021-04-27".
        end (str, optional): end date, format= 2021-05-05. Defaults to "2021-04-27".
    Returns:
        Array of JSON
    """
    if end == None:
        today = date.today()
        end = today.strftime("%Y-%m-%d")

    if source == "mc":
        timeframe = "1"
    elif source == "et":
        timeframe = "1MIN"
    else:
        timeframe="1"

    return CandleStickDataStream.getDataFromSource(source=source,
                                                   symbol=symbol,
                                                   symbol_type=symbol_type,
                                                   timeframe=timeframe,
                                                   start=start, end=end)


# download data per minute.
def perMinute_MoneyControl(symbol="BANKNIFTY",
                           symbol_type="index",
                           start="2021-04-27",
                           end=None):
    return _ohlcDataPerMin("mc", symbol, symbol_type, start, end)


def perMinute_EconomicTimes(symbol="BANKNIFTY",
                           symbol_type="index",
                           start="2021-04-27",
                           end=None):
    return _ohlcDataPerMin("et", symbol, symbol_type, start, end)



# convert array of json to df.
# for larger df:

def perMinuteToLargerMinute(arr_json, minute):
    return CandleStickUtils.mergeArrJsonToLargerTimeFrame(arr_json, 1, minute)


# proper output:
def ohlcDF_MC(symbol="BANKNIFTY",
            symbol_type="index",
            start="2021-04-27",
            end=None,
            tf=1,
            arr_json=None):
    if arr_json is None:
        arr_json = perMinute_MoneyControl(symbol, symbol_type, start, end)
    arr_json_tf = perMinuteToLargerMinute(arr_json, tf)
    return CandleStickUtils.jsonToCSVToDF(arr_json_tf)


def ohlcDF_ET(symbol="BANKNIFTY",
            symbol_type="index",
            start="2021-04-27",
            end=None,
            tf=1):
    arr_json = perMinute_EconomicTimes(symbol, symbol_type, start, end)
    if arr_json is None:
        return None
    arr_json_tf = perMinuteToLargerMinute(arr_json, tf)
    return CandleStickUtils.jsonToCSVToDF(arr_json_tf)
































#
def checkSymbolFromNse(symbol="BANKNIFTY"):
    """ checks name whether it is index or stock """
    nse = Nse()
    symbol = symbol.upper()
    if "NIFTY" in symbol:
        new_sym = symbol.replace("NIFTY", "")
        index_list = nse.get_index_list()
        for s in index_list:
            if new_sym in s:
                symbol = s
                return (s, "index")
    else:
        if nse.is_valid_code(symbol):
            return(symbol, "stock")
    return None



