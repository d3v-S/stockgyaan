from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys, logging



# Uncomment below for terminal log messages
# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class LoggingDialog(QDialog, QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.INFO)

        layout = QVBoxLayout()
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)


    def debug(self, string):
        logging.debug (string)

    def info(self, string):
        logging.info(string)

    def warn(self, string):
        logging.info(string)

    def err(self, string):
        logging.error(string)


#
# widget to show the Status:
class LoggingStatus(QWidget):
    def __init__(self, parent=None, info_color=None, error_color=None):
        """ write information in Status bar. (lower side of window)
        Args:
            parent ([type], optional): parent widget. Defaults to None.
            info_color ([type], optional): color when info is shown. Defaults to None.
            error_color ([type], optional): color when err is shown. Defaults to None.
        """
        super(LoggingStatus, self).__init__()
        self.parent = parent
        if parent is not None:
            self.log = parent.log
        else:
            self.log = False
        self.label = QLabel()
        self.label.setObjectName("status")

        self.button = QPushButton("Logs")
        #self.button.clicked.connect(self.showLog)

        # ui
        self.info_color = info_color
        self.err_color = error_color
        self.setUI()

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.label, 90)
        #hbox.addWidget(self.button, 10)
        self.setLayout(hbox)
    
    def info(self, string, color=None):
        if self.log:
            self.log.info(string)
        colour = "green"
        if color is not None:
            colour = color
        if self.info_color is not None:
            colour = self.info_color
        self.label.setText(string)
        self.label.setStyleSheet("color: " + str(colour))

    def err(self, string):
        if self.log:
            self.log.err(string)
        colour = "red"
        
        if self.err_color is not None:
            colour = self.err_color
        self.label.setText(string)
        self.label.setStyleSheet("color: " + str(colour))

        msgbox = QMessageBox()
        msgbox.setAttribute(Qt.WA_DeleteOnClose)
        msgbox.setText(string)
        msgbox.exec()

    @pyqtSlot()
    def showLog(self):
        self.log.show()



