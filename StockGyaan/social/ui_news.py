import gc
import io
import time

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QTabWidget, QPushButton, QLineEdit, QHBoxLayout, QListView, QVBoxLayout, QLabel, \
    QListWidgetItem, QListWidget, QLayout, QDialog

from common.utils_ import loadImageUrl, resizeImageKeepingAspectRatio, setUpParent, dbgOK, CONFIG_FILE
from common.widgets.log import LoggingDialog, LoggingStatus
from social.data_news_ import getTwitterHashTagFeed, getTelegramChannelFeed


def loadImageFromUrl(url, max_width, max_height, url_cache=None):
    """ load image from URL. will return image_label """
    pixmap = QPixmap()
    image_label = QLabel()
    data = loadImageUrl(url, url_cache)
    if data != None:
        if max_width is None and max_height is None:
            data = data.content
        else:
            data = resizeImageKeepingAspectRatio(io.BytesIO(data.content), max_width, max_height)
        pixmap.loadFromData(data)
    image_label.setPixmap(pixmap)
    return image_label











##
# Input widget
##
class HashTagInputWidget(QWidget):
    def __init__(self, onClickHandler, parent=None):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)

        self.onClickHandler = onClickHandler
        self.line_edit = QLineEdit()  # line edit
        self.button = QPushButton("add")  # button
        self.setUI()

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.line_edit, 90)
        hbox.addWidget(self.button, 10)
        self.setLayout(hbox)
        self.button.clicked.connect(self.onClickHandlerSlot)

    @pyqtSlot()
    def onClickHandlerSlot(self):
        if self.onClickHandler is not None:
            input = self.line_edit.text()
            self.onClickHandler(input)


class NewsWidget(QWidget):
    def __init__(self, news_dict, parent=None):
        super(QWidget, self).__init__()
        self.parent = parent
        self.news_dict = news_dict
        self.setUI()

    def setUI(self):
        vbox = QVBoxLayout()
        label_author = QLabel()
        label_author.setObjectName("label_author")

        label_desc = QLabel()
        label_desc.setObjectName("label_desc")

        #label_author.setText("<b>"+self.news_dict["author"] + "</b>\t\t" + self.news_dict["published"])
        string_author_published = "{:<30s}{:<20s}".format(self.news_dict["author"],
                                                          self.news_dict["published"])
        label_author.setText(string_author_published)

        label_desc.setText(self.news_dict["text"])
        label_desc.setWordWrap(True)

        vbox.addWidget(label_author)
        vbox.addWidget(label_desc)
        for img in self.news_dict["imgs"]:
            label_img = loadImageFromUrl(img, max_width=400, max_height=400, url_cache=self.parent.url_cache)
            print(label_img)
            label_img.setObjectName("label_image")
            vbox.addWidget(label_img)
        vbox.addStretch()
        vbox.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(vbox)

    def getNewsDict(self):
        return self.news_dict


def getTradingViewdata(hashtag):
    pass


class FeedDownloader(QThread):
    downloaded = pyqtSignal()
    def __init__(self, pool, parent=None):
        super(QThread, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.feed = None
        self.pool = pool

    def run(self):
        while self.parent.is_running:
            print(self, "Downloading hashtag: " + str(self.parent.hashtag))

            if self.parent.news_type is None:
                self.feed = self.pool.apply_async(
                    getTwitterHashTagFeed, args=(self.parent.hashtag,)).get()

            if self.parent.news_type == "telegram":
                self.feed = self.pool.apply_async(
                    getTelegramChannelFeed, args=(self.parent.hashtag,)).get()

            if self.parent.news_type == "tv":
                self.feed = self.pool.apply_async(
                    getTradingViewdata,
                    args=(self.parent.hashtag,)).get()

            for news_dict in self.feed:
                for img in news_dict["imgs"]:
                    self.parent.url_cache[img] = loadImageUrl(img, self.parent.url_cache)
            if self.parent.is_running:
                self.downloaded.emit()
            time.sleep(self.parent.update_interval)
        dbgOK(self, " -- xxx -- Qthread has been killed: "+ self.parent.hashtag + " -- xxx --")




class NewsArea(QListWidget):
    """ takes in the list of news_dict."""

    def __init__(self, hashtag, parent=None, news_type=None):
        super(QListView, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.hashtag = hashtag
        self.feed = []            # list_news_dict
        self.news_type = news_type
        self.url_cache = {}



        # downloader
        self.is_running = True
        self.update_interval = 30
        self.thread = FeedDownloader(parent=self, pool = self.parent.pool)
        self.thread.downloaded.connect(self.updateUI)
        self.thread.start()

        # click
        self.itemClicked.connect(lambda item: self.zoomThis(item))

    def addNw(self, news_dict):
        item = QListWidgetItem()
        nw = NewsWidget(news_dict, parent=self)
        item.setSizeHint(nw.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, nw)

    @pyqtSlot()
    def updateUI(self):
        diff = [x for x in self.thread.feed if x not in self.feed]
        for news_dict in diff:
            self.addNw(news_dict)
        self.feed = self.feed + diff

    @pyqtSlot()
    def zoomThis(self, item):
        dbgOK(self, " news_dict: " + str(self.itemWidget(item).getNewsDict()))
        zf = ZoomedFeed(self.itemWidget(item).getNewsDict(), parent=self)
        zf.exec()

    def closeNewsArea(self):
        dbgOK(self, "closing news_area, killing the thread.")
        self.is_running = False
        del self.url_cache
        (self.parent, self.log, self.status) = setUpParent(None)
        self.setParent(None)
        self.deleteLater()


class ZoomedFeed(QDialog):
    def __init__(self, news_dict, parent):
        super(QDialog, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.news_dict = news_dict
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setUI()

    def setUI(self):
        vbox = QVBoxLayout()
        label_author = QLabel()
        label_desc = QLabel()
        label_author.setText("<b>"+self.news_dict["author"] + "</b>\t\t" + self.news_dict["published"])
        label_desc.setText(self.news_dict["text"])
        label_desc.setWordWrap(True)
        vbox.addWidget(label_author)
        vbox.addWidget(label_desc)
        for img in self.news_dict["imgs"]:
            label_img = loadImageFromUrl(img, max_width=None, max_height=None, url_cache=self.parent.url_cache)
            print(label_img)
            vbox.addWidget(label_img)
        vbox.addStretch()
        vbox.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(vbox)





class UINews(QWidget):
    """ contains of Hashtag input and tabwidget to show the news. Readonly."""

    def __init__(self, pool, parent=None, news_type=None, config_location=CONFIG_FILE):
        super(QWidget, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        if self.parent is None:
            self.log = LoggingDialog()
            self.status = LoggingStatus(self)

           # pool
        self.pool = pool

        self.news_type = news_type

            # file load
        self.config_location = config_location

            # ui
        self.input = HashTagInputWidget(parent=self, onClickHandler=self.addHashTag)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda index: self.closeTab(index))
        self.setUI()

        self.loadFromFile()


    def loadFromFile(self):
        if self.config_location is not None:
            from configparser import ConfigParser
            cp = ConfigParser()
            cp.read(self.config_location)
            if self.news_type is None:
                if "twitter" in cp.keys():
                    comma_sep = cp["twitter"]["hashtag"]
                else:
                    return
            else:
                if self.news_type in cp.keys():
                    comma_sep = cp[self.news_type]["hashtag"]
                else:
                    return
            for i in comma_sep.split(","):
                self.addHashTag(i)




    @pyqtSlot()
    def closeTab(self, index):
        dbgOK(self, "Tab Close Requested")
        widget = self.tabs.widget(index)
        dbgOK(self, "widget from tab: " + str(type(widget)))
        widget.closeNewsArea()
        self.tabs.removeTab(index)

    def setUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.input)
        vbox.addWidget(self.tabs)
        self.setLayout(vbox)
        pass

    def updateUI(self):
        pass

    # add hashtags: input from the slot
    def addHashTag(self, input):
        widget = NewsArea(input, parent=self, news_type=self.news_type)
        self.tabs.addTab(widget, input);


