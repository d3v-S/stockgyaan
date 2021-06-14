import sys
from io import StringIO

import requests
from PIL.Image import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from bs4 import BeautifulSoup

indicator_delimiter = "%7E"     # ~
param_comma = "%2C"             # ,

# c1 & c2
G_lower_indictors = [
    ("AccDist","Accumulation Distribution", 0),     # param = n/a
    ("Aroon", "Aroon Up/Down Indicator", 1),
    ("AroonOsc", "Aroon Oscillator", 1),
    ("RSI", "RSI", 1),
    ("ADX", "ADX", 1),
    ("ATR", "ATR", 1),
    ("BBW", "Bollinger band width", 2),
    ("CMF", "Chaikin Money Flow", 1),
    ("COscillaotr", "Chaikin oscillator", 0),
    ("CVolatility", "Chaikin volatility", 2),
    ("CCI", "Commodity Channel Index", 1),
    ("DPO", "Detrended Price Oscillator", 1),
    ("FStoch", "Fast Stochastic", 1),
    ("MACD", "MACD", 2),
    ("Momentum", "Momentum", 1),
    ("MFI", "Money Flow Index", 1),
    ("OBV", "On Balance Volume", 0),
    ("SStoch", "Slow Stochastic", 1),
    ("StochRSI", "Stoch RSI", 1),
]


# c3 & c4
G_overlay_indicators = [
    ("BB", "Bollinger Bands", 2),
    ("ParabolicSAR", "Parabolic sar", 2),
    ("supertrend", "Super Trend", 2),
    ("Envelop", "envelope", 2),
    ("ichimoku", "Ichimoku clouds", 3),
    ("DC", "donchanin channel", 1)
]

# "a1l" <- first MA Lenght
# "a1t" <= type close
# "a1v" <= SMA, TMA, WMA, EMA


def checkIfIndicatorExists(indicator_name):
    indicator_name = indicator_name.strip()
    for index, i in enumerate(G_lower_indictors):
        if indicator_name == i[0]:
            return ("Lower", index)

    for index, i in enumerate(G_overlay_indicators):
        if indicator_name == i[0]:
            return ("Overlay", index)

    return (None, None)


def createParamString (param_list):
    string = ""
    for i in param_list:
        string = string + i + "%2C"
    return string[:-3]


def createIndicatorString(type_, indicator_list, param_string_list):
    string_ind = ""
    for i in indicator_list:
        string_ind = string_ind + i + "%7E"

    psl = ""
    for i in param_string_list:
        psl = psl + i + "%7E"

    string = ""

    if type_ == "Lower":
        string = "c1=" + string_ind + "&c2=" + psl + "&"

    if type_ == "Overlay":
        string = "c3=" + string_ind + "&c4=" + psl + "&"

    return string





# indicator to be represented by a dict:
# dict_["NAME"] = [ PARAM_LIST ]
# each key, one indicator.
def validateIndicatorDict(dict_):
    lower = []
    lower_param = []
    overlay = []
    overlay_param = []
    for key in dict_.keys():  # one key == one indicator
        param_list = dict_[key]
        (type_, index) = checkIfIndicatorExists(key) ## assume it to be from either lower
        if type_ is not None:
            if type_ == "Lower":
                lower.append(key)
                lower_param.append(createParamString(param_list))
            if type_ == "Overlay":
                overlay.append(key)
                overlay_param.append(createParamString(param_list))

    final_str = createIndicatorString("Lower", lower, lower_param) + createIndicatorString("Overlay", overlay, overlay_param)
    return final_str



def createUrl(symbol, timeframe, period,  indicator_dict, typeofchart=None, width=1900):
    indicator_string = validateIndicatorDict(indicator_dict)
    url = "https://chartink.com/raw/chartdisplayintraday.php?v=o&t=m&E=1&E2=1&h=1&l=0&vg=1&y=1&s=0&w=0&" \
            "a1=1&a1l=21&a2l=10&a3l=15&a4l=20&a5l=28&" \
            "{indicator_string}ti={period}&d={timeframe}_minute&A={symbol}&width={width}&is_premium=true&user_id=0".format(
                indicator_string = indicator_string,
                period = period,
                timeframe = timeframe,
                symbol = symbol,
                width = str(width)
            )

    print(url)

    return url


def get_chartink_stocks(symbol, url):
    with requests.Session() as s:
        scanner_url = "http://chartink.com/stocks/" + symbol + ".html"
        r = s.get(scanner_url)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf = soup.select_one("[name='csrf-token']")['content']
        s.headers['x-csrf-token'] = csrf
        #url = "https://chartink.com/raw/chartdisplayintraday.php?v=o&t=m&E=1&E2=1&h=1&l=0&vg=1&y=1&s=0&w=0&c1=AroonOsc%7EAroon%7E&c2=25%7E25%7E&a1=1&a1t=c&a1v=TMA&a1l=21&a2=1&a2t=c&a2v=EMA&a2l=10&a3=1&a3t=c&a3v=SMA&a3l=15&a4=1&a4t=c&a4v=SMA&a4l=20&a5=1&a5t=c&a5v=SMA&a5l=28&ti=5000&d=240_minute&A=TITAN&width=942&is_premium=false&user_id=0"
        r = s.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        img_content =soup.find_all("img")[0]["src"].split(",")[1]
        #print(img_content)
        import base64
        imgdata = base64.b64decode(img_content)
        pixmap = QPixmap()
        image_label = QLabel()
        pixmap.loadFromData(imgdata)
        image_label.setPixmap(pixmap)
        return image_label



dict_ = {}
dict_["RSI"] = ["15"]
dict_["supertrend"]=["10", "1.5"]
dict_["CCI"] = ["15"]

url = createUrl("BANKNIFTY", "1", "1", dict_)


from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QHBoxLayout Example")
        layout = QHBoxLayout()
        layout.addWidget(get_chartink_stocks("BANKNIFTY", url))
        self.setLayout(layout)
        print(self.children())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())