from PyQt5.QtCore import QStringListModel, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLineEdit, QCompleter
from nsetools import Nse

from common.utils_ import setUpParent, dbgOK


class NseDownload(QThread):
    downloaded = pyqtSignal()
    def __init__(self, parent=None):
        super(QThread, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)

    def run(self):
        nse = Nse()
        self.parent.index_list = nse.get_index_list()
        self.parent.stock_list = [x for x in nse.get_stock_codes().keys()]
        dbgOK(self, "Downloaded stock list for autocomplete. Exiting thread...")
        self.downloaded.emit()




class StockLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(QLineEdit, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)

        # thread
        self.index_list = None
        self.stock_list = None

        self.thread = NseDownload(parent=self)
        self.thread.downloaded.connect(self.setDataInModel)
        self.thread.start()

    @pyqtSlot()
    def setDataInModel(self):
        if self.index_list is None:
            return
        self.model = QStringListModel()
        completer = QCompleter()
        completer.setModel(self.model)
        self.model.setStringList(self.index_list + self.stock_list)
        self.setCompleter(completer)
        dbgOK(self, "Autocompleter model has been set.")




