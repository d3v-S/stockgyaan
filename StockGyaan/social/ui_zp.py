import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QListView, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QWidget, QLayout, QDialog, \
    QMainWindow, QMessageBox

from common.utils_ import setUpParent, dbgDld, dbgOK
from social.data_news_ import ZerodhaPulse


class FeedDownloader(QThread):
    downloaded = pyqtSignal()
    def __init__(self, parent=None):
        super(QThread, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.feed = []

    def run(self):
        while self.parent.is_running:
            dbgDld(self, "Zerodha Pulse periodic")
            self.feed = ZerodhaPulse().parseZerodhaPulse()
            if self.parent.is_running:
                self.downloaded.emit()
            time.sleep(self.parent.update_interval)
        dbgOK(self, " QThread for ZerodhaPulse terminated")

class UIzp(QListWidget):
    """ should show table in a QLabel"""

    def __init__(self, parent=None):
        super(QListWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.feed = []   # list of dict

        # downloader
        self.is_running = True
        self.update_interval = 60
        self.thread = FeedDownloader(parent=self)
        self.thread.downloaded.connect(self.updateUI)
        self.thread.start()

        # item clicked
        self.itemDoubleClicked.connect(lambda item: self.openBrowser(item))


    @pyqtSlot()
    def updateUI(self):
        diff = [x for x in self.thread.feed if x not in self.feed]
        self.feed = self.feed + diff
        for dict_ in diff:
            self.addItem(dict_["title"])
        self.setWordWrap(True)

    @pyqtSlot()
    def openBrowser(self, item):
        index = self.currentRow()
        print(type(index))
        url = self.feed[index]["link"]
        # webpage = ZPDialog(url, parent=self)
        # webpage.exec()
        url = QUrl(url)
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Open Url', 'Could not open url')




class ZPDialog(QDialog):
    def __init__(self, url, parent=None):
        super(QDialog, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.showMaximized()
        self.url = url
        self.setUI()

    def setUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(ZPWebPage(self.url, parent=self))
        self.setLayout(vbox)


class ZPWebPage(QMainWindow):
    def __init__(self, url, parent=None):
        super(QMainWindow, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.url = url
        self.minimumWidth = 500
        self.minimumHeight = 500
        self.setUI()


    def setUI(self):
        browser = QWebEngineView(parent=self)
        browser.setUrl(QUrl(self.url))
        browser.show()
        self.setCentralWidget(browser)
