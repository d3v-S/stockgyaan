# get image from market_in_out
from common.widgets.image_container import loadPixmapFromUrl


def _validityForIndianIndices(ptype="4", zoom="1", pperiod="4", psize="big"):
    type = ["1", "4", "20", "2"]  # 1 = bar, 4 = candle, 20 =  heieknashi, 2= line, 12 = renko (not with banknifty), 9 = PointandFigures ( not with bnf)
    if ptype not in type:
        ptype = str(4)
    # zoom = 1  # xzoom times
    size = ["small", "huge", "big", "medium"]
    if psize not in size:
        psize = "big"
    period = ["2", "3", "4"]  # daily=4, monthly=2, weekly=3, 5minute=5 (unavailable)
    if pperiod not in period:
        pperiod = str(4)
    return(ptype, zoom, pperiod, psize)


def _getImageForStock(symbol, max_width, max_height, url_cache=None, type="20", zoom="10", period="4", size="big"):
    (type, zoom, period, size) = _validityForIndianIndices(type, zoom, period, size)
    symbol = symbol.upper() + ".NS"
    #url = "https://www.marketinout.com/chart/servlet.php?symbol="+symbol+"&n=1&tindicator=&intraday_color=&chart_color=&tv=&dtype="\
    #      + str(type) + "&s=" + str(size) + "&dp=" + str(period) +"&dz=" + str(zoom)
    url = "https://www.marketinout.com/chart/servlet.php?symbol=" + symbol + "&n=1&tindicator=&show_lines=&show_td_lines=&show_fibo=&dindicator=64,15&tv=&dtype=" \
          + str(type) + "&s=" + str(size) + "&dp=" + str(period) + "&dz=" + str(zoom)

    return loadPixmapFromUrl(url, max_width, max_height, url_cache =url_cache)


def getDailyImage(symbol, max_width, max_height, url_cache=None, zoom="5"):
    return _getImageForStock(symbol, max_width, max_height, url_cache, type="4", zoom=zoom)

def getDailyHAImage(symbol, max_width, max_height, url_cache=None, zoom="5"):
    return _getImageForStock(symbol, max_width, max_height, url_cache, type="20", zoom=zoom)

def getWeeklyImage(symbol, max_width, max_height, url_cache=None):
    return _getImageForStock(symbol, max_width, max_height, url_cache, period="3")

def getMonthlyImage(symbol, max_width, max_height, url_cache=None):
    return _getImageForStock(symbol, max_width, max_height, url_cache, period=4)



