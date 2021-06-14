from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

from common.utils_ import infoStart, infoError, infoFinished
from common.widgets.log import LoggingDialog, LoggingStatus
from nse.option_analysis.widgets.active_analysis import OIAnalysis
from nse.option_analysis.widgets.input_stock_completer import InputStock
from common.ui import STATUS_MAX_HEIGHT


class OIAnalysisChart(QWidget):
    def __init__(self, parent, pool):
        super(QWidget, self).__init__()
        self.log = LoggingDialog()
        self.status = LoggingStatus(self)
        self.status.setMaximumHeight(STATUS_MAX_HEIGHT)

        self.input = InputStock(parent=self, pool=pool)
        self.input.analysis.connect(self.updateAnalysis) # button press


            # qlabels
        self.ce_oi_image = QLabel()
        self.pe_oi_image = QLabel()
        self.ce_price_image = QLabel()
        self.pe_price_image = QLabel()
        self.active_analysis = OIAnalysis(parent=self.input)
        self.setUI()

            # timer to update:
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.updateImages)
        self.timer.start()



    def setUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.input, 10)
        vbox.addWidget(self.ce_oi_image, 30)
        vbox.addWidget(self.pe_oi_image, 30)
        vbox.addWidget(self.status, 5)
        self.setLayout(vbox)

    # def setOIImageUI(self):
    #     qwidget = QWidget()
    #     hbox = QHBoxLayout()
    #     hbox.addWidget(self.ce_oi_image)
    #     #hbox.addWidget(self.pe_oi_image)
    #     qwidget.setLayout(hbox)
    #     return qwidget
    #
    # def setPriceImageUI(self):
    #     qwidget = QWidget()
    #     hbox = QHBoxLayout()
    #     hbox.addWidget(self.ce_price_image)
    #     #hbox.addWidget(self.pe_price_image)
    #     qwidget.setLayout(hbox)
    #     return qwidget




    def dataToPixmap(self, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data.getvalue())
        return pixmap

    def updateAnalysis(self):
        trade = self.input.getTrade()
        self.active_analysis.getPlotData(trade["index"], trade["strike"])
        infoStart(self, " loading files .. ")


    def updateImages(self):
        if self.active_analysis.plot_data is not None:
            infoStart(self, " UPDATING images...")
            plot_data = self.active_analysis.plot_data
            ce_oi_pixmap = self.dataToPixmap(plot_data["ce_oi_price"])
            pe_oi_pixmap = self.dataToPixmap(plot_data["pe_oi_price"])
            # ce_price_pixmap = self.dataToPixmap(plot_data["ce_price"])
            # pe_price_pixmap = self.dataToPixmap(plot_data["pe_price"])
            self.ce_oi_image.setPixmap(ce_oi_pixmap)
            self.pe_oi_image.setPixmap(pe_oi_pixmap)
            # self.ce_price_image.setPixmap(ce_price_pixmap)
            # self.pe_price_image.setPixmap(pe_price_pixmap)
            infoFinished(self, " UPDATING done.")
        else:
            infoError(self, " plot_data is None")
