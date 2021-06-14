from PyQt5 import sip
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from common.utils_ import err, dbgErr, setUpParent, info, dbgOK
from nse.pool_functions import validateNseName
from nse.stock_info import StockInfo
from nse.watchlist.widgets.listwidgetitem import ListItemWidget


class ListStock(QListWidget):
    double_clicked = pyqtSignal()
    def __init__(self, parent):
        super(QListWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)  # parent is the main widget where this is attached.

        self.itemDoubleClicked.connect(lambda item: self.emitSignalDoubleClicked(item))     # item is double clicked, then it should emit stuff.

        self.setUI();

    def setUI(self):
        pass


    @pyqtSlot()
    def emitSignalDoubleClicked(self, item):
        item_widget = self.itemWidget(item)
        self.parent.double_clicked_item = item_widget.stock_info  # ItemWidget
        self.double_clicked.emit()
        dbgOK(self, "Double Clicked " + str((self.parent.double_clicked_item.symbol)))



    def updateUI(self):
        for i in range(self.count()):
            item = self.item(i)
            item_widget = self.itemWidget(item)
            item_widget.updateUI()


    # save this state to file.
    def saveState(self):
        self.parent.list_of_stocks = self.__getStocks()     # serializable format that can be pickled
        self.parent.save()
        pass


    def __getStocks(self):
        list_stocks = []
        for i in range(self.count()):
            item = self.item(i)
            item_widget = self.itemWidget(item)
            if item_widget is None:
                continue
            stock_info = item_widget.stock_info
            if stock_info is not None:
                list_stocks.append(stock_info.symbol)
        return list_stocks


    # used by parent to download data per stockinfo
    def getStockInfoList(self):
        list_stocks = []
        for i in range(self.count()):
            item = self.item(i)
            item_widget = self.itemWidget(item)
            if item_widget is None:
                continue
            stock_info = item_widget.stock_info
            if stock_info is None:
                sip.delete(self.takeItem(i))
                continue
            list_stocks.append(stock_info)
        return list_stocks






    # List takes in the name of symbol to add.
    # It needs to be validated into StockInfo
    def addStockToList(self, symbol):
        self.__symbolToStockInfo(symbol)
        info(self, "added symbol: " + str(symbol))


    # helper functions for adding stocks to list
    def __symbolToStockInfo(self, symbol):
        is_valid_nse = validateNseName(symbol)
        dbgOK(self, "Symbol: " + symbol)
        if is_valid_nse is None:
            err(self, "SYMBOL NOT IN NSE: " + str(symbol))
        else:
            (nse, sym_type) = is_valid_nse
            if self.__isDuplicate(nse):
                err(self, "SYMBOL ALREADY PRESENT IN LIST: " + str(nse))
                return
            si = StockInfo(symbol=nse, pool=self.parent.pool, app=self.parent.app)
            self.__addItemToList(si)
            self.saveState()


    def __addItemToList(self, stock_info):
        item = QListWidgetItem()
        item_widget = ListItemWidget(stock_info, parent=self, item=item)   # Item widget is created from stock_info, stock_info is created from symbol.
        item.setSizeHint(item_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, item_widget)


    def __isDuplicate(self, sym):
        for i in range(self.count()):
            item = self.item(i)
            item_widget = self.itemWidget(item)
            stock_info = item_widget.stock_info
            if stock_info is None:
                sip.delete(self.list.takeItem(i))
                dbgErr(self, "ListItemWidget.stock_info is None, it is supposed to be deleted")
                continue
            if sym == stock_info.symbol:
                return True
        return False






