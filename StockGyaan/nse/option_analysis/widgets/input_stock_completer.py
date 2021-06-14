import time

from PyQt5.QtCore import QStringListModel, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QCompleter, QLineEdit, QWidget, QComboBox, QHBoxLayout, QPushButton

from common.utils_ import DOWNLOAD_FOLDER, dbgOK, DOWNLOAD_OPTIONCHAIN_FOLDER
from common.widgets.autocompleter import QLECompleter
from nse.data.options.optionchain_ import optionsData, optionsDataWithoutKeys
import pandas as pd


##
#  User paper trade to Show Analysis too.
##


class PTDownloader(QThread):
    downloaded = pyqtSignal()
    def __init__(self, parent):
        super(QThread, self).__init__()
        self.parent = parent


    def run(self):
        time_download = 0
        result = None
        while True:
            time_download = (time_download + 1) % 300        # per 2.5 minute download
            if time_download == 0:
                for index in self.parent.index_list:
                    result = self.parent.pool.map(optionsDataWithoutKeys, self.parent.index_list)

                if result is not None:
                    for i, symbol in enumerate(self.parent.index_list):
                        file_name = symbol + "_" + str(int(time.time())) + ".csv"
                        df = result[i]
                        df.to_csv( self.parent.location + file_name)

            self.parent.oidf_list = result
            self.downloaded.emit()
            time.sleep(0.5)



class InputStock(QWidget):
    analysis = pyqtSignal()
    def __init__(self, parent, pool, location=DOWNLOAD_OPTIONCHAIN_FOLDER):
        super(QWidget, self).__init__()

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


        # add teh analysis button
        self.analysis_button = QPushButton()
        self.analysis_button.clicked.connect(self.emitAnalysisSignal)

        # ui
        self.setUI()

        # Downloader
        self.update_now = False
        self.downloader = PTDownloader(parent=self)
        self.downloader.downloaded.connect(self.unblockButtons)
        self.downloader.start()


    @pyqtSlot()
    def emitAnalysisSignal(self):
        self.analysis.emit()

    @pyqtSlot()
    def unblockButtons(self):
        self.index_strike.setDisabled(False)

    @pyqtSlot()
    def updateNow(self):
        self.update_now = True
        self.index_strike.setDisabled(True)

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.index_input)
        hbox.addWidget(self.index_type)
        hbox.addWidget(self.index_strike)
        hbox.addWidget(self.analysis_button)
        self.setLayout(hbox)


    def getSelectedValues(self):
        index = self.index_input.currentText()
        type_ = self.index_type.currentText()
        i = self.index_list.index(index)
        if len(self.oidf_list) > 0:
            df = self.oidf_list[i]
            list_strike = self.getListOfStrike(df)
            self.index_strike_model.setStringList(list_strike)


    def getListOfStrike(self, df):
        list_ = df['strikePrice'].tolist()
        return [str(x) for x in list_]


    def getTrade(self):
        d = {}
        d["index"] = self.index_input.currentText()
        d["type"] = self.index_type.currentText()
        strike_price = self.index_strike.text().strip().split(" ")
        d["strike"] = strike_price[0]
        d["price"] = strike_price[-1]
        return d











