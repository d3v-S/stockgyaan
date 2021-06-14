import glob
import io
import time
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

import matplotlib.pyplot as plt

from common.utils_ import setUpParent


class OIAnalysis(QWidget):
    keys = ['strikePrice',
            'CE_lastPrice',
            'PE_lastPrice',
            'CE_openInterest',
            'PE_openInterest' ]

    def __init__(self, parent):     # parent == INPUT_STOCK
        super(QWidget, self).__init__()
        self.loaded_files = {}
        self.parent = parent

        print("\n\n --- Parent: " + str(self.parent))

        self.index_list = self.parent.index_list

        self.plot_symbol = None
        self.plot_strike = None
        self.plot_now = False
        self.plot_data = None

        # downloader
        self.downloader = FileLoaders(parent=self)
        self.downloader.start()


    def loadCSVFiles(self, symbol, epoch):
        filename = symbol + "_" + str(epoch) + ".csv"
        df = pd.read_csv(filename)
        return df[OIAnalysis.keys]

    def getTodayEpoch(self):
        #return int(datetime.date.today().strftime('%s'))
        from datetime import date
        today = str(date.today())
        today_start = today + " 09:15:00"
        today_end = today + " 15:30:00"
        pattern = '%Y-%m-%d %H:%M:%S'
        epoch_start = int(time.mktime(time.strptime(today_start, pattern)))
        epoch_end = int(time.mktime(time.strptime(today_end, pattern)))
        return (epoch_start, epoch_end)


    def getTodayFiles(self, symbol):
        dir = self.parent.location
        glob_wildcard = dir + symbol+"_*.csv"
        list_files = glob.glob(glob_wildcard)
        new_list = []
        (tstart, tend) = self.getTodayEpoch()
        for file in list_files:
            epoch = self.getEpochFromFilename(file)
            if tstart > int(epoch)  or int(epoch) > tend :
                continue
            new_list.append(file)
        return new_list


    def getEpochFromFilename(self, filename):
        return  filename.split("_")[1].split(".")[0]


    def getStrike(self, df, strike):
        return df.loc[df['strikePrice'] == int(strike)]


    def getDfFromFiles(self, symbol):
        list_files = self.getTodayFiles(symbol)
        list_files.sort()
        last_epoch = 0
        if symbol not in self.loaded_files:
            self.loaded_files[symbol] = {}
            self.loaded_files[symbol]["df"] = []
            self.loaded_files[symbol]["epoch"] = []
        else:
            last_epoch = self.loaded_files[symbol]["epoch"][-1]

        for file in list_files:
            epoch = self.getEpochFromFilename(file)
            if int(epoch) > int(last_epoch):
                df = pd.read_csv(file)
                self.loaded_files[symbol]["df"].append(df)
                self.loaded_files[symbol]["epoch"].append(epoch)
                last_epoch = epoch



    def plotChartsAgainstEpoch(self, symbol, strike, key):
        list_df = self.loaded_files[symbol]["df"]
        list_epoch = self.loaded_files[symbol]["epoch"]
        print(list_epoch)
        list_ = []
        last_epoch = 0
        new_list_epoch = []
        for  index, df in enumerate(list_df):
            epoch = list_epoch[index]
            if int(epoch) - int(last_epoch) < 300:
                last_epoch = epoch
                continue
            strike_df = self.getStrike(df, strike)
            chart_y = strike_df[key].tolist()[0]
            list_.append(chart_y)
            new_list_epoch.append(epoch)
        print("\n\n\n KEY: " + str(key))
        print(new_list_epoch)
        print(list_)

        plt.plot(new_list_epoch, list_)
        bio = io.BytesIO()
        plt.savefig(bio)
        plt.close()
        return bio


    def plotTwoChartsAgainstEpoch(self, symbol, strike, key1, key2, timediff=300):
        list_df = self.loaded_files[symbol]["df"]
        list_epoch = self.loaded_files[symbol]["epoch"]
        list_y1 = []
        list_y2 = []
        last_epoch = 0
        new_list_epoch = []

        for  index, df in enumerate(list_df):
            epoch = list_epoch[index]
            if int(epoch) - int(last_epoch) < timediff:
                last_epoch = epoch
                continue
            strike_df = self.getStrike(df, strike)
            chart_y = strike_df[key1].tolist()[0]
            chart_y2 = strike_df[key2].tolist()[0]
            list_y1.append(chart_y)
            list_y2.append(chart_y2)

            new_list_epoch.append(epoch)

        print(new_list_epoch)

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(new_list_epoch, list_y1, color="red")
        ax1.set_ylabel('OI', color="red")
        ax1.tick_params(axis='y', labelcolor="red")

        ax2.plot(new_list_epoch, list_y2, color="blue")
        ax2.set_ylabel('Price', color='blue')
        ax2.tick_params(axis='y', labelcolor="blue")

        ax1.tick_params(axis='x', labelsize=9, labelrotation=90)
        ax2.tick_params(axis='x', labelsize=9, labelrotation=90)

        fig.tight_layout()
        bio = io.BytesIO()
        fig.savefig(bio, figsize=(20,4))
        plt.close(fig)
        return bio


    def plotOI_CE(self, symbol, strike):
        return self.plotChartsAgainstEpoch(symbol, strike, 'CE_openInterest')

    def plotOI_PE(self, symbol, strike):
        return self.plotChartsAgainstEpoch(symbol, strike, 'PE_openInterest')

    def plotPrice_CE(self, symbol, strike):
        return self.plotChartsAgainstEpoch(symbol, strike, 'CE_lastPrice')

    def plotPrice_PE(self, symbol, strike):
        return self.plotChartsAgainstEpoch(symbol, strike, 'PE_lastPrice')

    def plotCharts(self, symbol, strike):
        plots_data = {}
        plots_data["ce_oi"] = self.plotOI_CE(symbol, strike)
        plots_data["pe_oi"] = self.plotOI_PE(symbol, strike)
        plots_data["ce_price"] = self.plotPrice_CE(symbol, strike)
        plots_data["pe_price"] = self.plotPrice_PE(symbol, strike)
        return plots_data

    def plotTwinCharts(self, symbol, strike):
        plots_data = {}
        plots_data["ce_oi_price"] = self.plotTwoChartsAgainstEpoch(symbol,
                                                                   strike,
                                                                   'CE_openInterest',
                                                                   'CE_lastPrice')
        plots_data["pe_oi_price"] = self.plotTwoChartsAgainstEpoch(symbol,
                                                                   strike,
                                                                   'PE_openInterest',
                                                                   'PE_lastPrice')
        return plots_data


    def getPlotData(self, symbol, strike):
        self.plot_symbol = symbol
        self.plot_strike = strike
        self.plot_now=True




    #
    #
    # def plotOICharts(self, symbol, strike):
    #     list_df = self.loaded_files[symbol]["df"]
    #     list_epoch = self.loaded_files[symbol]["epoch"]
    #     list_ce_oi = []
    #     list_pe_oi = []
    #
    #     for df in list_df:
    #         strike_df = self.getStrike(df, strike)
    #         ce_io = strike_df['CE_openInterest'].tolist()[0]
    #         pe_io = strike_df['PE_openInterest'].tolist()[0]
    #         list_ce_oi.append(ce_io)
    #         list_pe_oi.append(pe_io)
    #
    #     plt.plot(list_epoch, list_ce_oi)
    #     plt.plot(list_epoch, list_pe_oi)
    #     pixmap = QPixmap()
    #     bio = io.BytesIO()
    #     plt.savefig(bio)
    #     pixmap.loadFromData(bio.getvalue())
    #     plt.close()
    #     return pixmap



class FileLoaders(QThread):
    def __init__(self, parent):
        super(QThread, self).__init__()
        self.parent = parent


    def run(self):
        time_ = 0
        while True:
            if self.parent.plot_now or time_ == 0:
                if self.parent.plot_symbol is None or self.parent.plot_strike is None:
                    self.parent.plot_data = None
                else:
                    self.parent.plot_data = self.parent.plotTwinCharts(self.parent.plot_symbol, self.parent.plot_strike)
                self.parent.plot_now = False
            if time_ == 0:
                for symbol in self.parent.index_list:
                    self.parent.getDfFromFiles(symbol)
            time_ = (time_ + 1) % 120
            time.sleep(0.5)














