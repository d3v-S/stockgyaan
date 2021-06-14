

## CHECKBOX: COMPACT/NOT COMPACT
## ## Input
## ## List
## ## Status for the list:
import os

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from common.utils_ import setUpParent, DOWNLOAD_FOLDER, fileToObj, objToFile, info, dbgOK
from common.widgets.log import LoggingStatus, LoggingDialog
from common.ui import WL_UPDATE_INTERVAL, WL_INPUT_MAX_HEIGHT, WL_STATUS_MAX_HEIGHT, WL_MAX_WIDTH
from nse.watchlist.widgets.inputstock import InputStock
from nse.watchlist.widgets.liststock import ListStock


class WL(QWidget):
    def __init__(self, pool, app, location=DOWNLOAD_FOLDER, parent=None):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.log = LoggingDialog()
        self.status = LoggingStatus(self)
        self.status.setMaximumHeight(WL_STATUS_MAX_HEIGHT)

        self.pool = pool    # to download using multiprocess
        self.app = app      # to process events.

        # set maximum width for this widget
        self.setMaximumWidth(WL_MAX_WIDTH)
        self.setObjectName("WATCHLIST")


        self.file = location + "/WL.pkl"


        self.double_clicked_item = None     # item that is double clicked.
        self.list_of_stocks = []            # list of stocks, taken from listwidget



        self.input = InputStock()
        self.input.stock_added.connect(lambda sym: self.addStock(sym))
        self.input.setMaximumHeight(WL_INPUT_MAX_HEIGHT)

        self.list = ListStock(parent=self)
        self.setUI()        # set up UI
        self.load()         # load it if file exists
        dbgOK(self, "Watchlist constructor called. UI setup complete.")

        # timer to init Download in StockInfo itself
        self.update_interval = WL_UPDATE_INTERVAL
        self._time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.runDownload)
        self.timer.setInterval(1000)
        self.timer.start()


    def runDownload(self):
        self._time = (self._time + 1) % self.update_interval
        if self._time == 0:
            # download and update the UI
            list_stock_info = self.list.getStockInfoList()
            length = len(list_stock_info)
            for index, si in enumerate(list_stock_info):
                if si is not None:
                    si.downloadCurrentData()
                    info(self, "Downloaded {downloaded}/{total}. Current: {sym}".format(downloaded=str(index), total=str(length-1),                                                            sym=si.symbol))
            self.updateUI()

    def updateUI(self):
        self.list.updateUI() # go through each item in list and udpate it to latest stock_info




    def setUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.input)
        vbox.addWidget(self.list)
        vbox.addWidget(self.status)
        self.setLayout(vbox)


    def addStock(self, symbol):
        self.list.addStockToList(symbol)


    def load(self):
        if os.path.exists(self.file):
            self.list_of_stocks = fileToObj(self.file)
            for stock_name in self.list_of_stocks:
                self.addStock(stock_name)
            info(self, "Watchlist loaded from file")


    def save(self):
        objToFile(self.list_of_stocks, self.file)


