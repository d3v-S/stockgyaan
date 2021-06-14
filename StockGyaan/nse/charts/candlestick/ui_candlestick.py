import os
import time

from PyQt5.QtCore import pyqtSlot, QEvent, Qt, QTimer, QThread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QTabWidget, QDialog, QPushButton, QLabel
from PyQt5.sip import delete
from PyQt5.uic.properties import QtGui

from common.utils_ import setUpParent, checkTypeObject, getStatus, info, dbgOK, dbgErr, getStatusData
from common.widgets.log import LoggingDialog, LoggingStatus
from nse.charts.candlestick.widget_charts import ChartsGV
from nse.stock_info import StockInfo


class ChartArea(QScrollArea):
    """ scrollable area to show charts """
    def __init__(self,
                 parent=None,
                 datasource=None):
        super(QScrollArea, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.setWidgetResizable(True)               # necessary
        self.charts = ChartsGV(parent=self,
                               onClickHandler=self.onClickHandler,
                               ctrlOnClickHandler=self.ctrlOnClickHandler)
        self.chartsgv = self.charts.getGV()         # set up chart
        self.setUI()                                # set up UI

    def wheelEvent(self, ev):
        """ ignore the wheel when inside the finplot graph """
        if ev.type() == QEvent.Wheel:
            ev.ignore()

    def setUI(self):                                ## Mandatory steps
        content_widget = QWidget()
        self.setWidget(content_widget)
        vbox = QVBoxLayout(content_widget)
        vbox.addWidget(self.chartsgv)

    def getChart(self):
        return self.charts


    def dataIsNull(self):
        self.chartsgv.hide()

    def dataIsNotNull(self):
        self.chartsgv.show()

    def updateCharts(self, df):
        self.charts.updateCandleSticks(df)

    def onClickHandler(self, ev, p):
        if ev.button() == Qt.RightButton:
            self.parent.stock_info.delSnr(p.y())
            self.charts.removeLine(p.y())
        else:
            self.parent.stock_info.addSnr(p.y())
            self.charts.drawLine(p.y())

    def ctrlOnClickHandler(self, ev, p):
        self.parent.stock_info.setTrendLines(self.charts.getTrendLines())



## ---- Main Widget for UI ---- ##
class UIcandlestick(QWidget):
    def __init__(self,
                 stock_info=None,
                 parent=None,
                 location=None):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)      # set up parent
        if self.log is None:
            self.log = LoggingDialog()
            self.status = LoggingStatus()

             # check for stock info
        self.stock_info = checkTypeObject(stock_info, StockInfo)  # stock_info be StockInfo
        self.timeframe = None
        if self.stock_info is not None:
            self.timeframe = self.stock_info.timeframe

        # location
        self.location = location

            # Label ui
        self.label = QLabel()

            # buttons
        self.clear_all_button = QPushButton('ClearDrawing')
        self.clear_all_button.clicked.connect(self.clearLines)

                # set up charts area.
        self.tabs = QTabWidget()                                        # charts QTabWidget
        self.tabs.currentChanged.connect(self.tabChanged)

                # set up UI
        self.setLabelUI()
        self.setTabUI()
        self.setUI()

            # current selected tab widgets
        self.chartsarea = self.getCurrentChartsArea()

            # timer to check Thread.
        self.time_ = 0
        self.ui_update=False

        self.download_timer = 50
        self.timer = QTimer()
        self.timer.timeout.connect(self.downloadData)
        self.timer.setInterval(1000)
        self.timer.start()


            # to reset
        self.changeStockInfo(self.stock_info)


    ##
    # UI
    ##
    def setLabelUI(self):
        if self.stock_info is None:
            self.label.setText("Not updated ")
            return
        string = "<table><tr>" \
                    "<td colspan=12 style='font-size:20px;'><b>{sym}</b></td>" \
                    "<td colspan=5>PRICE: {price}</td>" \
                 "</tr></table>".format(
                                    sym = self.stock_info.symbol,
                                    price = self.stock_info.getCurrentPrice(),
                                    )
        self.label.setText(string)

    def setTabUI(self):
        for i, tf in enumerate(self.timeframe):
            self.tabs.addTab(ChartArea(parent=self), str(tf) + " MIN")


    def setLabelNButtons(self):
        q = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.label, 80)
        hbox.addWidget(self.clear_all_button, 20)
        q.setLayout(hbox)
        return q


    def setUI(self):
        hbox = QHBoxLayout()

        q = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.setLabelNButtons(), 10)
        vbox.addWidget(self.tabs, 85)
        vbox.addWidget(self.status, 5)

        q.setLayout(vbox)

        hbox.addWidget(q, 100)
        self.setLayout(hbox)

    def getCurrentChartsArea(self):
        return self.tabs.currentWidget()


    ###
    # Slots
    ###
    @pyqtSlot()
    def tabChanged(self):
        self.chartsarea = self.getCurrentChartsArea()
        df = self.stock_info.getCandleStickDataFrame()
        if df is None:
            info(self, "DOWNLOAD STATUS:" + str(getStatus(self.stock_info.dld_df_status)) + " => DF is None.")
            dbgErr(self, "Downloaded Dataframe is None.")
            self.chartsarea.dataIsNull()
            return

        self.chartsarea.dataIsNotNull()
        index = self.tabs.currentIndex()

        # restore SNR on every graph:
        self.chartsarea.charts.restoreListOfLines(self.stock_info.snr)

        self.__updateCandleStickCharts(df[index])
        self.ui_update = True

        info(self, "DOWNLOAD STATUS:"+ str(getStatus(self.stock_info.dld_df_status)) +
             " . TIP: if not visible, change TABS or ZOOM OUT completely")


    @pyqtSlot()
    def clearLines(self):
        self.chartsarea.charts.removeAllLines()
        self.chartsarea.charts.removeAllTrendLines()
        for y in self.stock_info.snr:
            self.stock_info.delSnr(y)
        self.stock_info.setTrendLines(self.chartsarea.charts.getTrendLines())



    @pyqtSlot()
    def updateUI(self):

        self.setLabelUI()
        self.tabChanged()


        # oi_df = self.stock_info.oi_df                           # process it
        # new_oi_df = oi_df[oi_df['strikePrice'].between(31000, 36000, inclusive=False)]  # https://stackoverflow.com/questions/46860038/how-to-get-specific-number-of-rows-based-on-column-values-in-dataframe
        # self.oi_table.setDf(new_oi_df[['strikePrice', 'CE_lastPrice', 'PE_lastPrice']])


    @pyqtSlot()
    def downloadData(self):
        self.time_ = (self.time_ + 1) % self.download_timer
        if self.time_ == 0:
            self.ui_update = False
            self.stock_info.downloadData()
            self.updateUI()

        info(self, "STATUS: " + str(getStatus(self.stock_info.dld_df_status)) + " <- " + (self.stock_info.symbol)
             + " :: " + (getStatusData(self.stock_info.dld_df_status)))


    # Candlestick chart update
    #
    def __updateCandleStickCharts(self, df):
        self.chartsarea.charts.updateCandleSticks(df)


    ##
    # Changing stock datasource
    ##
    def changeStockInfo(self, stock_info):
        if stock_info is None:
            return
        self.stock_info = stock_info
        if self.location is not None:
            self.path = self.location + self.stock_info.symbol +".pkl"

        self.chartsarea.charts.removeAllLines()
        self.stock_info.downloadData()
        dbgOK(self, "Changed StockInfo in UINse :: " + str(stock_info.symbol))
        info(self, "Changed stock: " + str(stock_info.symbol) + " <- dowload in progress..")
        self.updateUI()
        self.chartsarea.charts.restoreListOfLines(self.stock_info.snr)
        self.chartsarea.charts.setTrendLines(self.stock_info.getTrendLines())


#
#

