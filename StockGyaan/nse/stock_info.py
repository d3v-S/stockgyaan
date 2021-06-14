import os
import threading
from datetime import date, timedelta
from configparser import ConfigParser

import pandas

from common.utils_ import fileToObj, info, objToFile, setLocation, statusSubmitted, statusFinished, dbgOK, \
    DOWNLOAD_FOLDER
from .data.stocks.charts_images_ import getDailyImage, getDailyHAImage
from .pool_functions import downloadCandlesticksData, validateNseName, downloadCurrentData, downloadOptionsData


class StockInfo:
    def __init__(self, symbol, pool, location=DOWNLOAD_FOLDER, timeframe=[3,5,15,30,60], app=None):
        self.symbol = symbol.upper()              # symbol has no spaces, nse names have spaces.
        self.timeframe = timeframe

            # to be downloaded.
        self.symbol_type = None
        self.quote = None
       
       
        self.dld_df_status = {}
        self.df = None
        self.pandas_ta_df = None    ## pandas_ta changes the DF hence.
        self.indicators = None      ## dict containing PandasSeries maybe, per container

        self.dld_oi_df_status = {}
        self.oi_df = None


            # images from marketinout
        self.daily_image = None     ## data of image, put in Pixmap
        self.candle_image= None
        self.img_downloaded = False

            # image huge size
        self.huge_candle = None
        self.huge_ha = None

        self.image_cache = {}
        self.max_width = 100
        self.max_height = 75

           # files
        self.filenamesnr = self.symbol + "_snr_.pkl"
        self.path_snr = setLocation(location, self.filenamesnr)

        # support and resistances.
        self.snr = []
        self.loadFileSNR()

        # trendliens
        self.filenametrend = self.symbol + "_trend_.pkl"
        self.path_trend = setLocation(location, self.filenametrend)
        self.trendlines = None
        self.loadFileTrend()

        # global config
        self.pool = pool     # create thread and send things to pool for asycing things.
        self.app = app

        self.pool.apply_async(validateNseName, args=(self.symbol,), callback=self.setNseAndType)
        self.pool.apply_async(downloadCurrentData, args=(self.symbol, ), callback=self.setQuote)


    # getter and setters
    # callbacks
    def setNseAndType(self, ret):
        if ret is not None:
            (self.nse, self.symbol_type) = ret
        else:
            (self.nse, self.symbol_type) = (None, None)


    def setQuote(self, quote):
        self.quote = quote


    def setDF(self, df):
        self.df = df
        if self.df is None:
            string = " :: None downloaded"
        else:
            string = " downloaded number of df: " + str(len(self.df))
        statusFinished(self.dld_df_status, data=string)
        list_df = []
        for dfs in self.df:
            df1 = dfs.copy()
            list_df.append(df1)
        self.pandas_ta_df = list_df


    def setOIDF(self, oi_df):
        self.oi_df = oi_df
        if oi_df is None:
            string = "None Downloaded"
        else:
            if not isinstance(oi_df, pandas.DataFrame):
                string = "expected DF, got : " + str(type(oi_df))
            else:
                string = "downlaoded number of DF: " + str(len(oi_df))
       
       

    def setFut(self, fut_tup):
        if fut_tup is None:
            return
        self.fut_near = fut_tup[0]
        self.fut_next = fut_tup[1]

    def setDailyImage(self, img_data):
        self.daily_image = img_data

    def setDailyHAImage(self, img_data):
        self.candle_image = img_data

    def setHugeCandleImage(self, img_data):
        self.huge_candle = img_data

    def setHugeHAImage(self, img_data):
        self.huge_ha = img_data




    # Price information
    #
    def isPriceLoaded(self):
        if self.quote is None:
            return False
        return True


    def getChangeInPrice(self):
        if self.quote is not None:
            if "change" in self.quote.keys():
                return self.quote["change"]
            return 0
        return 0
        

    def getPChangeInPrice(self):
        if self.quote is not None:
            if "pChange" in self.quote.keys():
                return self.quote["pChange"]
            return 0
        return 0
        
    def getCurrentPrice(self):
        if self.quote is not None:
            return self.quote["lastPrice"]
        return 0
        
    def getVwap(self):
        if self.quote is not None:
            if "averagePrice" in self.quote.keys():
                return self.quote["averagePrice"]
            return "0"
        return 0

    def getNseName(self):
        if hasattr(self, "nse"):
            return str(self.nse)
        return self.symbol

    
    def getCandleStickDataFrame(self):
        return self.df

    def getOIDataFrame(self):
        return self.oi_df

    def getPandasTADataFrame(self):
        return self.pandas_ta_df


    def addSnr(self, y):
        self.snr.append(y)
        self.saveFileSNR()

    def delSnr(self, y):
        if y in self.snr:
            self.snr.remove(y)
        self.saveFileSNR()

    def setTrendLines(self, list_trends):
        self.trendlines = list_trends[:]
        self.saveFileTrend()

    def getTrendLines(self):
        return self.trendlines

    # async downloading function.
    def downloadData(self):
        self.pool.apply_async(downloadCandlesticksData, args=(self.symbol, self.dld_df_status), callback=self.setDF)
        self.pool.apply_async(downloadCurrentData, args=(self.symbol, ), callback=self.setQuote)
        statusSubmitted(self.dld_df_status, " <-- " + (self.symbol))


    def downloadCurrentData(self):
        self.pool.apply_async(downloadCurrentData,
                              args=(self.symbol,), callback=self.setQuote)
        
        
    def downloadOptionsData(self):
        self.pool.apply_async(downloadOptionsData,
                              args=(self.symbol,), callback=self.setOIDF)
        statusSubmitted(self.dld_oi_df_status, " <-- " + (self.symbol))



    def downloadDailyImage(self):

        if self.img_downloaded:
            return

        if self.daily_image is not None and self.candle_image is not None:
            return

        self.pool.apply_async(getDailyImage,
                              args=(self.symbol, self.max_width, self.max_height, self.image_cache, 10),
                              callback=self.setDailyImage)

        self.pool.apply_async(getDailyHAImage,
                              args=(self.symbol, self.max_width, self.max_height, self.image_cache, 10),
                              callback=self.setDailyHAImage)

        self.pool.apply_async(getDailyImage,
                              args=(self.symbol, 900, 1000, self.image_cache, "5"),
                              callback=self.setHugeCandleImage)

        self.pool.apply_async(getDailyHAImage,
                              args=(self.symbol, 900, 1000, self.image_cache, "5"),
                              callback=self.setHugeHAImage)
        self.img_downloaded = True


    # load configuration from files:
    def loadFile(self, filepath):
        if filepath is not None:
            if not os.path.exists(filepath):
                return
            return fileToObj(filepath)

    def loadFileSNR(self):
        ret = self.loadFile(self.path_snr)
        if ret is not None:
            self.snr = ret

    def loadFileTrend(self):
        ret = self.loadFile(self.path_trend)
        if ret is not None:
            self.trendlines = ret


    def saveFileSNR(self):
        if self.path_snr is not None:
            objToFile(self.snr, self.path_snr)

    def saveFileTrend(self):
        if self.path_trend is not None:
            objToFile(self.trendlines, self.path_trend)
