import sys
import threading
from multiprocessing.pool import Pool
import os

import psutil
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QSplitter, QHBoxLayout

from  common.utils_ import *
from nse.charts.candlestick.ui_candlestick import UIcandlestick
from nse.charts.candlestick.ui_optionchain import UIoptionchain
from nse.charts.chartink.widgets.main_widget import ChartInkPics
from nse.papertrade.widgets.main_widget import PaperTrade
from nse.stock_info import StockInfo
from nse.summary.summary import UIsummary
from common.ui import STYLESHEET
from nse.watchlist.widgets.main_widget import WL
from social.ui_news import UINews
from social.ui_zp import UIzp


def _createDefaultFolders(DOWNLOAD_PATH=None):
    if not os.path.exists(DEFAULT_FOLDER):
        os.makedirs(DEFAULT_FOLDER)
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    if not os.path.exists(DOWNLOAD_OPTIONCHAIN_FOLDER):
        os.makedirs(DOWNLOAD_OPTIONCHAIN_FOLDER)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w'):
            pass

def initConfigurationFiles():
    _createDefaultFolders()


def initMultiProcessingPool():
    # https://stackoverflow.com/questions/31344582/python-multiprocessing-cpu-count-returns-1-on-4-core-nvidia-jetson-tk1
    return Pool(processes=psutil.cpu_count()*3)



class MainSocialWindow(QTabWidget):
    def __init__(self, pool):
        super(QWidget, self).__init__()

        zp = UIzp(parent=self)

        #self.addTab(self.zp, "Pulse")
        qtab = QTabWidget()
        qtab.addTab(UINews(pool=pool), "Twitter")
        qtab.addTab(UINews(pool=pool, news_type="telegram"), "Telegram")
        qtab.addTab(UINews(pool=pool, news_type="tv"), "TradingViewIdeas")

        self.addTab(zp, "News")
        self.addTab(qtab, "Social")



class MainChartWindow(QWidget):
    def __init__(self, pool, app):
        super(QWidget, self).__init__()

        # watchList:
        self.wl = WL(pool=pool, app=app)
        self.wl.list.double_clicked.connect(self.updateStockInfo)

        # candlestick
        self.charts_candlestick = UIcandlestick(parent=None, stock_info=DEFAULT_STOCK_INFO)

        # OI
        self.charts_oi  = UIoptionchain(parent=None, stock_info=DEFAULT_STOCK_INFO)

        # PaperTrade
        self.paper_trade = PaperTrade(parent=None, pool=pool)

        # Chartink Charts:
        self.chartink_charts = ChartInkPics(pool=pool, stock_info=DEFAULT_STOCK_INFO)

        # OI Analysis
        #self.oi_analysis_chart = OIAnalysisChart(parent=None, pool=pool)

        # summary
        self.summary = UIsummary(pool=pool)

        # socail
        self.social = MainSocialWindow(pool)

        # ui
        self.setUI()


    def updateStockInfo(self):
        stock_info = self.wl.double_clicked_item
        self.charts_candlestick.changeStockInfo(stock_info)
        self.charts_oi.changeStockInfo(stock_info)
        self.chartink_charts.changeStockInfo(stock_info)
        print("------ STOCK_INFO ---- " + stock_info.symbol)


    def candlestickUI(self):
        qsplitter = QSplitter(Qt.Vertical)
        qsplitter.addWidget(self.charts_candlestick)
        qsplitter.addWidget(self.charts_oi)
        return qsplitter

    def middleSectionUI(self):
        qtabwidget = QTabWidget()
        qtabwidget.addTab(self.candlestickUI(), "Charts Interactive")
        qtabwidget.addTab(self.chartink_charts, "Chart Images")
        qtabwidget.addTab(self.summary, "Market Status")
        qtabwidget.addTab(self.paper_trade, "PaperTrade")
        #qtabwidget.addTab(self.oi_analysis_chart, "OI Analysis")
        return qtabwidget


    def setUI(self):
        hbox = QHBoxLayout()
        qsplitter = QSplitter()
        qsplitter.addWidget(self.wl)
        qsplitter.addWidget(self.middleSectionUI())
        qsplitter.addWidget(self.social)
        hbox.addWidget(qsplitter)
        self.setLayout(hbox)




initConfigurationFiles()
pool = initMultiProcessingPool()
app = QApplication(sys.argv)


def runT(app):
    while True:
        app.processEvents()
        time.sleep(1)


t1 = threading.Thread(target=runT, args=(app,))



DEFAULT_STOCK_INFO = StockInfo("BANKNIFTY", pool=pool, app = app)


#screen =  ChartInkPics(pool=pool, stock_info=DEFAULT_STOCK_INFO )  #WL(pool=pool, app=app)

#screen = PaperTrade(parent=None, pool=pool)

#screen =  UINews(pool=pool)#UIoptionchain(stock_info=DEFAULT_STOCK_INFO)
#screen = OIAnalysisChart(parent = None, pool=pool)#
screen =  MainChartWindow(pool=pool, app=app)
screen.setStyleSheet(STYLESHEET)
screen.show()
app.exec_()