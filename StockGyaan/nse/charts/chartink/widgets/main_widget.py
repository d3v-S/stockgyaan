#
#   Each should be encapsulated with someway to have a period.
#   Active Indicators.
#
import time

from PyQt5.QtCore import QThread, Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QLabel, QSplitter

from common.utils_ import setUpParent, info, infoStart, infoFinished, infoError, DOWNLOAD_FOLDER, objToFile
from common.widgets.log import LoggingDialog, LoggingStatus
from nse.charts.chartink.widgets.indicator_list import IndicatorList
from nse.data.data_chartink_charts import get_chartink_stocks_images
from common.ui import CHARTINK_DOWNLOAD_PERIOD, \
    STATUS_MAX_HEIGHT, CHARTINK_PERIOD_DICT


class ChartInkPics(QWidget):
    def __init__(self, pool, stock_info, parent=None, location=DOWNLOAD_FOLDER):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        # own status
        self.log = LoggingDialog()
        self.status = LoggingStatus(self)
        self.status.setMaximumHeight(STATUS_MAX_HEIGHT)

        self.stock_info = stock_info
        self.timeframe = [1] + self.stock_info.timeframe + [120, 240]
        self.pool = pool

        self.path = location + "/chartink_indicators.pkl"

        self.scroll_area = QScrollArea()
        self.scroll_area.vbox = None
        self.setScrollArea()

        self.image_label_list = []
        self.setCharts()


        self.indicator_list = IndicatorList()
        self.setUI()

        self.downloader = ChartInkImageDownloader(parent=self)
        self.downloader.start()


        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.checkThread)
        self.timer.start()


    def saveIndicators(self, dict_indicators):
        objToFile(dict_indicators, self.path)
        pass

    def restoreIndicators(self, dict_indicators):
        pass


    def checkThread(self):
        if not self.downloader.isRunning():
            infoError(self, "TIMER restarts DOWNLOADER")
            self.downloader.start()


    def setScrollArea(self):
        self.scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.scroll_area.setWidget(content_widget)
        vbox = QVBoxLayout(content_widget)
        self.scroll_area.vbox = vbox


    def setCharts(self):
        for i in self.timeframe:
            qlabel = QLabel()
            pixmap = QPixmap()
            qlabel.setPixmap(pixmap)
            #self.image_pixmap_list.append(pixmap)
            self.image_label_list.append(qlabel)
            self.scroll_area.vbox.addWidget(qlabel)


    def setUI(self):
        box = QVBoxLayout()
        splitter = QSplitter()
        splitter.addWidget(self.scroll_area)
        splitter.addWidget(self.indicator_list)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        status_splitter = QSplitter(Qt.Vertical)
        status_splitter.addWidget(splitter)
        status_splitter.addWidget(self.status)
        box.addWidget(status_splitter)
        self.setLayout(box)


    # image from chatink
    def getImagesFromChartink(self):
        indicator = self.indicator_list.getIndicators()
        symbol = self.stock_info.symbol.upper()
        tf = self.timeframe
        if symbol == "NIFTY BANK":
            symbol = "BANKNIFTY"
        if symbol == "NIFTY 50":
            symbol = "NIFTY"
        for index, i in enumerate(tf):
            period = CHARTINK_PERIOD_DICT[i]
            imgdata = get_chartink_stocks_images(symbol, i, period, indicator)
            if imgdata is None:
                infoError(self," can not download image from chartink.")
                continue
            #pixmap = self.image_pixmap_list[index]
            #pixmap.loadFromData(imgdata)
            pixmap = QPixmap()
            pixmap.loadFromData(imgdata)
            label = self.image_label_list[index]
            label.setPixmap(pixmap)

    def changeStockInfo(self, stock_info):
        self.stock_info = stock_info
        self.update_now = True
        info(self, "[CHANGED] stock: " + stock_info)



class ChartInkImageDownloader(QThread):
    def __init__(self, parent):
        super(QThread, self).__init__()
        self.parent = parent

    def run(self):
        time_ = 0
        DOWNLOAD_STRING = "Download: " + str(self.parent.stock_info.symbol)
        while True:
            if time_ == 0 or self.parent.update_now:
                infoStart(self.parent, DOWNLOAD_STRING)
                self.parent.getImagesFromChartink()
                infoFinished(self.parent, DOWNLOAD_STRING)
                self.parent.update_now = False
            time_ = (time_ + 1) % CHARTINK_DOWNLOAD_PERIOD
            time.sleep(1)











