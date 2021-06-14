import time

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QSplitter
import pandas as pd

from common.utils_ import setUpParent, infoError, infoFinished, infoStart
from common.widgets.log import LoggingDialog, LoggingStatus
from common.widgets.table import DataFrameModel, DfTable
from nse.data.options.optionsummary_ import *
from common.ui import STATUS_MAX_HEIGHT


class UIsummary(QWidget):

    # FNO_TOP_PRICE_GAINER = "FnoTopPriceGainer"
    # FNO_TOP_PRICE_LOSER  = "FnoTopPriceLoser"
    FNO_TOP_OI_GAINER = "FnoTopOIGainer"
    FNO_TOP_OI_LOSER = "FnoTopOILoser"
    FNO_MOST_ACTIVE_CE = "MostActiveCE"
    FNO_MOST_ACTIVE_PE = "MostActivePE"
    FNO_MOST_ACTIVE_FUT = "MostActiveFutIndex"
    FNO_LONG_UNWINDING = "Long Unwinding"
    FNO_SHORT_COVERING = "Short Covering"
    FNO_SHORT_BUILDUP = "Short Buildup"
    FNO_LONG_BUILDUP = "Long Buildup"

    STOCK_MOST_ACTIVE_FUT = "MostActiveStocksFut"
    STOCK_MOST_ACTIVE_CE = "MostActiveCEStocks"
    STOCK_MOST_ACTIVE_PE = "MostActivePEStocks"


    functions_dict = {}
    # functions_dict[FNO_TOP_PRICE_GAINER] = getFNOTopPriceGainerIndex
    # functions_dict[FNO_TOP_PRICE_LOSER] = getFNOTopPriceLoserIndex
    functions_dict[FNO_TOP_OI_GAINER] = getFNOTopOIGainerIndex
    functions_dict[FNO_TOP_OI_LOSER] = getFNOTopOILoserIndex
    functions_dict[FNO_MOST_ACTIVE_CE] = getTrendingCEOptionsIndex
    functions_dict[FNO_MOST_ACTIVE_PE] = getTrendingPEOptionsIndex
    functions_dict[FNO_MOST_ACTIVE_FUT] = getTrendingFuturesIndex
    functions_dict[FNO_LONG_UNWINDING] = getIndexLongUnwinding
    functions_dict[FNO_SHORT_COVERING] = getIndexShortCovering
    functions_dict[FNO_SHORT_BUILDUP] = getIndexShortBuildUp
    functions_dict[FNO_LONG_BUILDUP] = getIndexLongBuildUp


    def __init__(self, pool, parent=None):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        if self.log is None:
            self.log = LoggingDialog()
            self.status = LoggingStatus(self)
            self.status.setMaximumHeight(STATUS_MAX_HEIGHT)

        self.pool = pool
        self.old_df = None
        self.new_df = None
        self.text = None
        self.start_download = False
        self.DataFrameModel = DataFrameModel()

            # UI
        self.spinner = QComboBox()
        for k in UIsummary.functions_dict.keys():
            self.spinner.addItem(k)

        self.table = DfTable(parent=self)
        self.setUI()

            # signal
        self.spinner.currentIndexChanged.connect(self.updateTable)

        #     # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkThread)
        self.timer.setInterval(5000)
        self.timer.start()

            # useQthread because it may crash
        self.downloader = DataFrameDownloader(parent=self)
        self.downloader.downloaded.connect(self.updateUI)
        self.downloader.start()

    def checkThread(self):
        if not self.downloader.isRunning():
            infoError(self, "TIMER restarts DOWNLOADER")
            self.downloader.start()


    @pyqtSlot()
    def updateUI(self):
        self.table.setDf(self.new_df)
        self.start_download = False
        infoFinished(self, "UPDATED table.")


    def setUI(self):
        qwidget =QWidget()
        box = QVBoxLayout()
        box.addWidget(self.spinner, 10)
        box.addWidget(self.table, 90)
        qwidget.setLayout(box)

        qsplitter = QSplitter(Qt.Vertical)
        qsplitter.addWidget(qwidget)
        qsplitter.addWidget(self.status)

        vbox = QVBoxLayout()
        vbox.addWidget(qsplitter)

        self.setLayout(vbox)

    def updateTable(self):
        self.text = self.spinner.currentText()
        self.start_download = True
        infoStart(self, "Download: " + self.text)


class DataFrameDownloader(QThread):
    downloaded = pyqtSignal()
    def __init__(self, parent):
        super(QThread, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)

    def run(self):
        while True:
            if self.parent.text is not None and self.parent.start_download:
                DOWNLOAD_STRING = "Download: " + self.parent.text
                infoStart(self, DOWNLOAD_STRING)
                func = UIsummary.functions_dict[self.parent.text]
                arr_json = func()
                print(arr_json)
                if arr_json is not None:
                    self.parent.new_df = pd.json_normalize(arr_json)
                    del self.parent.new_df['InstName']
                    del self.parent.new_df['co_code']
                    del self.parent.new_df['ExpDate']
                    del self.parent.new_df['CompanyName']
                    if 'ScripCode' in self.parent.new_df.columns:
                        del self.parent.new_df['ScripCode']
                    if 'FaOdiff' in self.parent.new_df.columns and 'OpenInterest' in self.parent.new_df.columns:
                        keys = ['Symbol', 'StrikePrice', 'OptType', 'OpenInterest', 'chgOpenInt', 'LTP', 'PrevLtp', 'FaOdiff']
                        self.parent.new_df = self.parent.new_df[keys]


                self.downloaded.emit()
                infoFinished(self, DOWNLOAD_STRING)
            time.sleep(1)
