from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout

from common.widgets.autocomplete_stock import StockLineEdit


class InputStock(QWidget):
    stock_added = pyqtSignal(str)
    def __init__(self):
        super(QWidget, self).__init__()

        self.input = StockLineEdit()
        self.input.setTextMargins(20, 5, 20, 5)
        self.input.setPlaceholderText("NSE symbol name")

        self.button = QPushButton("Add")
        self.button.clicked.connect(self.emitSignal)

        self.setUI()


    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.input)
        hbox.addWidget(self.button)
        self.setLayout(hbox)


    def emitSignal(self):
        text  = self.input.text().strip()
        self.stock_added.emit(text)


