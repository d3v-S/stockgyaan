import time

import pandas
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QTabWidget, QVBoxLayout

from common.utils_ import setUpParent, getStatus, getStatusData, dbgErr, info, dbgOK
from common.widgets.log import LoggingDialog, LoggingStatus
from nse.charts.candlestick.widget_charts import ChartsGV
from nse.data.options.optionchain_ import optionsPartialKeys


class OIArea(QWidget):
    """ Main widget containing 2 graphics View """
    def __init__(self,
                 parent=None):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)      # set up parent
        self.charts_1 = ChartsGV(onClickHandler=self.onClickHandler)                                      # set up chart 1
        self.charts_2 = ChartsGV(onClickHandler=self.onClickHandler)                                      # set up chart 2
        self.setUI()                                                    # set up UI

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.charts_1.getGV(), 50)
        hbox.addWidget(self.charts_2.getGV(), 50)
        self.setLayout(hbox)


    def oiDataIsNull(self):
        """ case where the stock does not have FnO """
        self.charts_1.getGV().hide()
        self.charts_2.getGV().hide()

    def oiDataIsNotNull(self):
        self.charts_1.getGV().show()
        self.charts_2.getGV().show()

    def onClickHandler(self, ev, p):
        pass
        # dbg(self, "** onClickHandler: " + str(ev))
        # dbg(self, "** onClickHandler: " + str(p))



## ---- Main OI Widget ---- ##
class UIoptionchain(QWidget):

    def __init__(self, stock_info, parent=None, location=None):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)  # set up parent
        if self.log is None:
            self.log = LoggingDialog()
            self.status = LoggingStatus(self)

            # stock_info
        self.stock_info = stock_info

            # tabs
        self.oi_tabs = QTabWidget()  # oi QTabWidget
        self.partial_keys = optionsPartialKeys()  # partial keys
        self.oi_tabs.currentChanged.connect(self.oiTabChanged)
        self.oiarea = self.oi_tabs.currentWidget()

            # timer to check Thread.
        self.time_ = 0
        self.download_timer = 10


        self.timer = QTimer()
        self.timer.timeout.connect(self.downloadData)
        self.timer.setInterval(1000)
        self.timer.start()

            # ui
        self.setOITabUI()
        self.setUI()


    ## -- download data -- ##
    def downloadData(self):
        self.time_ = (self.time_ + 1) % self.download_timer
        if self.time_ == 0:
            self.stock_info.downloadOptionsData()
            self.oiTabChanged()

        info(self, "STATUS: " + str(getStatus(self.stock_info.dld_oi_df_status)) +
             " <- " + str(self.stock_info.symbol) + " :: " + str(getStatusData(self.stock_info.dld_oi_df_status)))

    ## -- UI -- ##
    def setOITabUI(self):
        for i, pkey in enumerate(self.partial_keys):
            self.oi_tabs.addTab(OIArea(parent=self), str(pkey))

    def setUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.oi_tabs, 95)
        vbox.addWidget(self.status, 5)
        self.setLayout(vbox)

    ## -- updateUI -- ##
    @pyqtSlot()
    def oiTabChanged(self):
        self.oiarea = self.oi_tabs.currentWidget()
        idx = self.oi_tabs.currentIndex()
        pkey = self.oi_tabs.tabText(idx)
        oi_df = self.stock_info.getOIDataFrame()
        print(oi_df)
        if oi_df is None:
            dbgErr(self, "Downloaded Options Dataframe is None.")
            info(self, "OI dataframe is None. Either it will download, or this does not have FnO")
            self.oiarea.oiDataIsNull()
            return

        if not isinstance(oi_df, pandas.DataFrame):
            info(self, "OI info has an error. Maybe stock does not have FnO.")
            self.oiarea.oiDataIsNull()
            return

        self.oiarea.oiDataIsNotNull()
        (ce_df, pe_df) = self.preProcessDF(oi_df, pkey)
        self.__updateBarCharts(ce_df, pe_df)
        dbgOK(self, "OI tabChaned UI update completed.")


    def preProcessDF(self, df, key):
        df = df.set_index('strikePrice')
        key1 = 'CE_' + key
        key2 = 'PE_' + key
        ce_df = df[key1]
        pe_df = df[key2]
        info(self, "OI plotted @ " + str(time.time()))
        return (ce_df, pe_df)


    def __updateBarCharts(self, ce_df, pe_df):
        self.oiarea.charts_1.updateBar(ce_df)
        self.oiarea.charts_2.updateBar(pe_df)

    def changeStockInfo(self, stock_info):
        self.stock_info = stock_info
        self.downloadData()
