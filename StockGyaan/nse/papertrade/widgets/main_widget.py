from PyQt5.QtWidgets import QWidget, QVBoxLayout

from common.utils_ import infoFinished, DOWNLOAD_FOLDER
from common.widgets.log import LoggingStatus, LoggingDialog

from nse.papertrade.widgets.active_trade import ActiveTradeList
from nse.papertrade.widgets.input_completer import InputRow
from common.ui import STATUS_MAX_HEIGHT


class PaperTrade(QWidget):
    def __init__(self, parent, pool, location=DOWNLOAD_FOLDER):
        super(QWidget, self).__init__()
        self.log = LoggingDialog()
        self.status = LoggingStatus()
        self.status.setMaximumHeight(STATUS_MAX_HEIGHT)

        self.input = InputRow(parent=self, pool=pool)
        self.input.add_trade.connect(self.addTrade)
        self.active_trade_list= ActiveTradeList(parent=self.input)

        # path
        self.path = location + "/pt.wkl"

        self.setUI()

    def setUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.input, 10)
        vbox.addWidget(self.active_trade_list, 95)
        vbox.addWidget(self.status, 5)
        self.setLayout(vbox)


    def addTrade(self):
        trade = self.input.getTrade()
        self.active_trade_list.addTrade(trade)
        infoFinished(self, " added trade - " + str(trade))

    def updateTrade(self):
        self.active_trade_list.updateTrades()

