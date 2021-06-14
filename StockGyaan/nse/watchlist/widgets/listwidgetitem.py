from PyQt5.QtCore import pyqtSlot,  Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

# NAME PRICE DELETEBUTTON
from PyQt5.sip import delete

from common.utils_ import setUpParent, info
from common.ui import WL_ITEM_MAX_HEIGHT, WL_ITEM_BUTTON_MAX_WIDTH, WL_FONT_SIZE


class ListItemWidget(QWidget):

    STRING_ITEM_DELETED = "Item deleted."
    STRING_ITEM_DELETE_ERR = "Error in deleting item"

    def __init__(self, stock_info, parent, item):         # parent == the QListWidget.
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)

        self.stock_info = stock_info

        self.list = self.parent     # List where this item is attached.
        self.item = item            # ListWidgetItem it is attached to.




        self.label = QLabel()
        self.setObjectName("wl_item_label")
        font = self.label.font()
        font.setPixelSize(WL_FONT_SIZE)
        font.setBold(True)
        self.label.setFont(font)
        self.label.maximumHeight = WL_ITEM_MAX_HEIGHT

        self.delete_button = QPushButton("x")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setFixedHeight(WL_ITEM_MAX_HEIGHT)
        self.delete_button.setFixedWidth(WL_ITEM_BUTTON_MAX_WIDTH)
        self.delete_button.clicked.connect(self.deleteThisItem)

        self.setUI()


    @pyqtSlot()
    def deleteThisItem(self):
        row = self.parent.row(self.item)
        item = self.parent.takeItem(row)
        item_widget = self.parent.itemWidget(item)
        self.stock_info = None
        self.item = None                    # remove reference
        self.parent.saveState()             # make this change persistent

        if item_widget is not None:         # corrosponding ListItem
            delete(item_widget)

        if item is not None:
            delete(item)
            (self.parent, self.log, self.status) = setUpParent(None)
            # information should on list statuss
            info(self, ListItemWidget.STRING_ITEM_DELETED)
        else:
            info(self, ListItemWidget.STRING_ITEM_DELETE_ERR)




    def setUI(self):
        hbox = QHBoxLayout()
        self.setLabelText()
        hbox.addWidget(self.label, 70)              # label
        hbox.addWidget(self.delete_button, 30)      # delete button
        self.setLayout(hbox)


    def setLabelText(self):
        # (text, qpalette) = self.createLabelText()
        # self.label.setAutoFillBackground(True)
        # self.setPalette(qpalette)
        if self.stock_info is not None:
            change = self.stock_info.getChangeInPrice()
            qp = QPalette()
            if change is None:
                change = 0
            if float(change) < 0:
                qp.setColor(self.label.foregroundRole(), Qt.darkRed)
            else:
                qp.setColor(self.label.foregroundRole(), Qt.darkGreen)
            self.label.setPalette(qp)
        self.label.setText(self.createLabelText())



    def createLabelText(self):
        if not self.stock_info.isPriceLoaded():
            color = "black"
            current_price = "not yet loaded"
            change = 0

        else:
            change = self.stock_info.getChangeInPrice()
            if change is None:
                change = 0
            current_price = self.stock_info.getCurrentPrice()

        # string_start = "<table style='color: " + color + ";'>"
        # string_end = "</table>"
        # string_price = "<tr><td colspan=20 style='font-size:" + WL_ITEM_LABEL_SYM_FONT_SIZE + "px;'>" \
        #                "<b>{:<20s}</b></td>" \
        #                "<td colspan=7 style='font-size:10px;'>" \
        #                "<b>{:<10s}</b></td></tr>".format(self.stock_info.getNseName(),
        #                                                  str(current_price))

        # MAX_SYM_SIZE = 30
        # curr_size = len(self.stock_info.getNseName())
        # spaces_req = MAX_SYM_SIZE - curr_size
        # span_spaces = " "
        # for i in range(spaces_req):
        #     span_spaces = span_spaces + " "
        # span_spaces = "<span>" + span_spaces + "</span>"


        # string_price1 = "<span style='color: "+ color +";font-size:10px;'><b>{symbol}</b></span>".format(symbol=self.stock_info.getNseName())
        # string_price2 = "<span style='font-size:9px;'><b>{price}</b></span>".format(price=str(current_price))

        string_price = "{:<13s}{:<9s}{:<11s}".format(self.stock_info.getNseName(), str(current_price), str(change))
        return  string_price


    def updateUI(self):
        if self.isVisible():
            self.setLabelText()
            self.label.repaint()




