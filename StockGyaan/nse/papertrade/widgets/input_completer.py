import time

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QWidget, QComboBox, QHBoxLayout, QPushButton

from common.utils_ import DOWNLOAD_OPTIONCHAIN_FOLDER, setUpParent, infoStart, infoFinished
from common.widgets.autocompleter import QLECompleter
from nse.data.options.optionchain_ import optionsDataWithoutKeys

##
#  User paper trade to Show Analysis too.
##
from common.ui import PAPERTRADE_INPUT_HEIGHT, PAPERTRADE_INPUT_UPDATE_INTERVAL


class PTDownloader(QThread):
    downloaded = pyqtSignal()
    def __init__(self, parent):
        super(QThread, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)


    def run(self):
        time_ = 0
        # time_download = 0
        result = None
        while True:
            time_ = (time_ + 1) %  PAPERTRADE_INPUT_UPDATE_INTERVAL                       # per 2 second download.
                    # download OI data
            if not self.parent.update_now:
                if time_ != 0:
                    time.sleep(0.5)
                    continue
            for index in self.parent.index_list:
                DOWNLOAD_STRING = "download -> " + str(index)

                infoStart(self, DOWNLOAD_STRING)
                result = self.parent.pool.map(optionsDataWithoutKeys, self.parent.index_list)
                infoFinished(self, DOWNLOAD_STRING)

            self.parent.oidf_list = result
            self.parent.getSelectedValues()
            self.downloaded.emit()
            self.parent.update_now = False




class InputRow(QWidget):
    add_trade = pyqtSignal()
    analysis = pyqtSignal()
    def __init__(self, parent, pool, location=DOWNLOAD_OPTIONCHAIN_FOLDER):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)


        # select
        self.index_list = ["BANKNIFTY", "NIFTY"]
        self.oidf_list = []

        # pool
        self.pool = pool
        self.location = location

        # select options
        list_string = ["Not updated"]
        tup = QLECompleter(list_string)
        self.index_strike = tup[0]
        self.index_strike_model = tup[1]
        self.index_strike.setDisabled(True)
        # self.index_strike = QComboBox()


        # select index
        self.index_input = QComboBox()
        self.index_input.currentIndexChanged.connect(self.updateNow)
        for i in self.index_list:
            self.index_input.addItem(i)

        # select type
        self.index_type = QComboBox()
        self.index_type.currentIndexChanged.connect(self.updateNow)
        self.index_type.addItem("CE")
        self.index_type.addItem("PE")


        # SL
        self.sl_input = QLineEdit()
        self.sl_input.setPlaceholderText("StopLoss in Percent")

        # Buy/Sell
        self.buy_sell_cb = QComboBox()
        self.buy_sell_cb.addItem("Buy")
        self.buy_sell_cb.addItem("Sell")
        self.buy_sell_cb.currentIndexChanged.connect(self.updateNow)


        # Add it to trade button:
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self.emitAddTradeSignal)


        # ui
        self.setUI()
        self.setMaximumHeight(PAPERTRADE_INPUT_HEIGHT)

        # Downloader
        self.update_now = False
        self.downloader = PTDownloader(parent=self)
        self.downloader.downloaded.connect(self.unblockButtons)
        self.downloader.start()


    @pyqtSlot()
    def emitAddTradeSignal(self):
        self.add_trade.emit()


    @pyqtSlot()
    def unblockButtons(self):
        if not self.index_strike.isEnabled():
            self.index_strike.clear()
        self.index_strike.setDisabled(False)

    @pyqtSlot()
    def updateNow(self):
        self.update_now = True
        self.index_strike.setDisabled(True)

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.index_input)
        hbox.addWidget(self.index_type)
        hbox.addWidget(self.buy_sell_cb)
        hbox.addWidget(self.index_strike)
        hbox.addWidget(self.sl_input)
        hbox.addWidget(self.add_button)
        self.setLayout(hbox)


    def getSelectedValues(self):
        index = self.index_input.currentText()
        type_ = self.index_type.currentText()
        op = self.buy_sell_cb.currentText()

        i = self.index_list.index(index)
        if len(self.oidf_list) > 0:
            df = self.oidf_list[i]
            list_strike = self.getListOfStrike(df)
            list_strike_1 = []
            for strike in list_strike:
                price = self.getPriceOfStrike(df, strike, type_, op)
                s = str(strike) + "  Rs. " + str(price)
                list_strike_1.append(s)
            self.index_strike_model.setStringList(list_strike_1)
            # self.index_strike.clear()
            # for i in list_strike_1:
            #     self.index_strike.addItem(i)


    def getListOfStrike(self, df):
        list_ = df['strikePrice'].tolist()
        return [str(x) for x in list_]

    def getPriceOfStrike(self, df, strike, type_="CE", op="Buy"):
        df = df.loc[df['strikePrice'] == int(strike)]

        if op == "Buy":
            if type_ == "CE":
                return df['CE_askPrice'].tolist()[0]
            if type_== "PE":
                return df['PE_askPrice'].tolist()[0]

        if op == "Sell":
            if type_ == "CE":
                return df['CE_bidprice'].tolist()[0]
            if type_ == "PE":
                return df['PE_bidprice'].tolist()[0]


    def getLTPOfStrike(self, df, strike, type_="CE"):
        df = df.loc[df['strikePrice'] == int(strike)]
        if type_ == "CE":
            return df['CE_lastPrice'].tolist()[0]
        if type_ == "PE":
            return df['PE_lastPrice'].tolist()[0]





    def getTrade(self):
        d = {}
        d["index"] = self.index_input.currentText()
        d["type"] = self.index_type.currentText()
        strike_price = self.index_strike.text().strip().split(" ")
        if len(strike_price) > 1:
            d["strike"] = strike_price[0]
            d["price"] = strike_price[-1]
        else:
            d["strike"] = strike_price[0]
            d["price"] = 0
        d["sl"] = self.sl_input.text().strip()
        d["op"] = self.buy_sell_cb.currentText()
        return d


    def getCurrentPriceOfGivenTrade(self, index, type, strike):
        i = self.index_list.index(index)
        if len(self.oidf_list) > 0:
            df = self.oidf_list[i]
            return self.getLTPOfStrike(df, strike, type)
        return 0









