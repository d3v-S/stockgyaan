import io

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from common.utils_ import loadImageUrl, resizeImageKeepingAspectRatio


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



def loadPixmapFromUrl(url, max_width, max_height, url_cache=None):
    """ load image from URL. will return image_label """
    data = loadImageUrl(url, url_cache=url_cache)
    if data != None:
        if max_width is None and max_height is None:
            data = data.content
        else:
            data = resizeImageKeepingAspectRatio(io.BytesIO(data.content), max_width, max_height)
    return data