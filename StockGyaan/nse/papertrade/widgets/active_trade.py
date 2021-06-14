import datetime
import os

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem

from common.utils_ import setUpParent, infoStart, infoFinished, objToFile, fileToObj, DOWNLOAD_FOLDER
from common.ui import PAPERTRADE_ACTIVE_TRADE_UPDATE_INTERVAL, PAPERTRADE_EXIT_BUTTON_WIDTH


class ActiveTrade(QWidget):
    def __init__(self, trade_dict):
        super(QWidget, self).__init__()
        self.trade_dict = trade_dict
        self.active = True

        # trading dict.
        self.trade_label = QLabel()
        self.trade_label.setText(self.labelString(self.trade_dict))

        # current price
        self.trade_curr = QLabel()
        self.trade_exit = QPushButton("X")
        self.trade_exit.setMaximumWidth(PAPERTRADE_EXIT_BUTTON_WIDTH)
        self.trade_exit.clicked.connect(self.disableTrade)


        #
        self.setUI()

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.trade_label)
        hbox.addWidget(self.trade_curr)
        hbox.addWidget(self.trade_exit)
        self.setLayout(hbox)

    def disableTrade(self):
        self.active = False
        self.setDisabled(True)





    def labelString(self, dict_):
        # string_start = "<table>"
        # string_end = "</table>"
        # string_mid = "<tr><td>{index}</td>" \
        #              "<td>{type}</td>clear
        #              " \
        #              "<td>{strike}</td>" \
        #              "<td>{sl}</td>" \
        #              "<td>{price}</td>" \
        #              "</tr>"
        print(dict_)
        print(dict_["price"])
        string = "{:<15s}{:<5s}{:<5s}{:<10s}{:<4s}{:<8s}{:<10s}".format(
                                    dict_["index"],
                                    dict_["type"],
                                    dict_["op"],
                                    dict_["strike"],
                                    dict_["sl"]+"%",
                                    dict_["price"],
                                    str(datetime.datetime.now().time())
                                )
        return string

    def calcPL(self, current_price):
        print(self.trade_dict)
        d = (current_price - float(self.trade_dict["price"]))
        string_to_add = str(current_price) + "   " + str(round(d, 2)) + "    " + str(datetime.datetime.now().time())
        self.trade_curr.setText(string_to_add)
        qp = QPalette()
        if d < 0:
            if (d / float(self.trade_dict["price"])) >= float(self.trade_dict["sl"]):
                self.disableTrade()
            # set colors for labels
            qp.setColor(self.trade_label.foregroundRole(), Qt.darkRed)
            qp.setColor(self.trade_curr.foregroundRole(), Qt.darkRed)
        elif d == 0:
            qp.setColor(self.trade_label.foregroundRole(), Qt.darkBlue)
            qp.setColor(self.trade_curr.foregroundRole(), Qt.darkBlue)
        else:
            qp.setColor(self.trade_label.foregroundRole(), Qt.darkGreen)
            qp.setColor(self.trade_curr.foregroundRole(), Qt.darkGreen)
        self.trade_label.setPalette(qp)
        self.trade_curr.setPalette(qp)
        return d




class ActiveTradeList(QListWidget):
    def __init__(self, parent, location=DOWNLOAD_FOLDER):
        super(QListWidget, self).__init__()

        (self.parent, self.log, self.status) = setUpParent(parent)            ## input_completer

        # active trades history
        self.active_trades = []
        self.path = location + "active_trade.pkl"
        self.loadState()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTrades)
        self.timer.setInterval(PAPERTRADE_ACTIVE_TRADE_UPDATE_INTERVAL)
        self.timer.start()



    def addTrade(self, dict_):
        at = ActiveTrade(dict_)
        item = QListWidgetItem()
        item.setSizeHint(at.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, at)


    def updateTrades(self):
        self.active_trades = []
        for i in range(self.count()):
            item = self.item(i)
            itemwidget = self.itemWidget(item)
            trade_dict = itemwidget.trade_dict
            self.active_trades.append(trade_dict)

            infoStart(self, " UPDATING trades ... ")
            if itemwidget.active:
                curr_price = self.parent.getCurrentPriceOfGivenTrade(trade_dict["index"], trade_dict["type"], trade_dict["strike"])
                itemwidget.calcPL(curr_price)
            infoFinished(self, " UPDATING trades.")
        # save the active trades.
        self.saveState()
        #infoFinished(self, "Saved active trades.")



    def saveState(self):
        objToFile(self.active_trades, self.path)

    def loadState(self):
        if os.path.exists(self.path):
            self.active_trades = fileToObj(self.path)
            for trades in self.active_trades:
                self.addTrade(trades)


