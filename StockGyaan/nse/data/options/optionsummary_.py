import json
import requests
from common.utils_ import statusFinished, statusStarted


def _getIndiaInfoOnlineJson(url, status_dict=None):
    try:
        statusStarted(status_dict, "download started for indiainfoonline")
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            json_ = json.loads(res.text)
            if json_["response"]["type"] == "success":
                for k in json_["response"]["data"].keys():
                   
                    if "List" in k:
                        next_key = k.replace("List", "").strip()
                        statusFinished(status_dict, "returned the json.")
                        return json_["response"]["data"][k][next_key]
                   
                    if "list" in k:
                        next_key = k.replace("list", "").strip()
                        statusFinished(status_dict, "returned the json.")
                        return json_["response"]["data"][k][next_key]
                return json_["response"]["data"]
        return None
    except:
        return None


def getListOfExpiry():
    url = "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FPCR-Index-Expiry-List%3FresponseType%3Djson"
    json_ =  _getIndiaInfoOnlineJson(url)
    if json_ is not None:
        return json_
    return None


def getNearestExpiry():
    arr_json = getListOfExpiry()
    if arr_json is None:
        return "10-06-2021"
    return arr_json[0]["exdate"]

def getNextExpiry():
    arr_json = getListOfExpiry()
    return arr_json[1]["exdate"]


def getPCRSummaryIndex(expiry="27-05-2021"):
    url = "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FPCR-Index-Expiry-List%3FresponseType%3Djson"
    return _getIndiaInfoOnlineJson(url)


def getFuturesSummaryIndex(symbol="FINNIFTY", expiry=None):
    if expiry is None:
        expiry = getNearestExpiry()
    if expiry == "next":
        expiry = getNextExpiry()
    url = "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FFNO-OverView-FuturesQuotesVersion2%2FFUTIDX%2F{symbol}%2F{expiry}%3FresponseType%3Djson".format(symbol=symbol, expiry=expiry)
    return  _getIndiaInfoOnlineJson(url)


def getFNOTopPriceGainerIndex(expiry=None):
    if expiry is None:
        expiry = getNearestExpiry()
    url = "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-Futures-Options-version2%2FMR%2F{expiry}%2Foptidx%2Fall%2Fce%2Fall%2FL%2Fdesc%2F20%2FFaOchange%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getFNOTopPriceLoserIndex(expiry="27-05-2021"):
    if expiry is None:
        expiry = getNearestExpiry()
    url = "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-Futures-Options-version2%2FMR%2F{expiry}%2Foptidx%2Fall%2Fce%2Fall%2FL%2Fdesc%2F20%2FFaOchange%2Fasc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getFNOTopOIGainerIndex(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-Futures-Options-version2%2FMR%2F{expiry}%2Foptidx%2Fall%2Fce%2Fall%2FIOI%2Fdesc%2F20%2FchgOpenInt%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getFNOTopOILoserIndex(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-Futures-Options-version2%2FMR%2F{expiry}%2Foptidx%2Fall%2Fce%2Fall%2FDOI%2Fdesc%2F20%2FchgOpenInt%2Fasc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getTrendingCEOptionsIndex(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FMostActiveStockAndIndex-version3%2Foptidx%2Fce%2F{expiry}%2Fall%2Fall%2FOpenInterest%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getTrendingPEOptionsIndex(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FMostActiveStockAndIndex-version3%2Foptidx%2Fpe%2F{expiry}%2Fall%2Fall%2FOpenInterest%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getTrendingFuturesIndex(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FMostActiveStockAndIndex-version3%2Ffutidx%2Fxx%2F{expiry}%2Fall%2Fall%2FOpenInterest%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getTrendingFuturesStocks(expiry = getNearestExpiry()):
    url = "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FMostActiveStockAndIndex-version3%2Ffutstk%2Fxx%2F{expiry}%2Fall%2Fall%2FOpenInterest%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getTrendingCEOptionsStocks(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FMostActiveStockAndIndex-version3%2Foptstk%2Fce%2F{expiry}%2Fall%2Fall%2FOpenInterest%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getTrendingPEOptionsStocks(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FMostActiveStockAndIndex-version3%2Foptstk%2Fpe%2F{expiry}%2Fall%2Fall%2FOpenInterest%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getIndexLongUnwinding(expiry = getNearestExpiry()):
    url= "https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-FNO-OI-version2%2FOI%2Foptidx%2Fall%2F{expiry}%2Fc%2FDOIDPR%2Fall%2FOIchg%2Fasc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getIndexShortCovering(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-FNO-OI-version2%2FOI%2Foptidx%2Fall%2F{expiry}%2Fc%2FDOIIPR%2Fall%2FOIchg%2Fasc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getIndexShortBuildUp(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-FNO-OI-version2%2FOI%2Foptidx%2Fall%2F{expiry}%2Fc%2FIOIDPR%2Fall%2FOIchg%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

def getIndexLongBuildUp(expiry = getNearestExpiry()):
    url="https://www.indiainfoline.com/api/papi-call-api.php?url=%2FDerivative%2FDerivative.svc%2FGet-FNO-OI-version2%2FOI%2Foptidx%2Fall%2F{expiry}%2Fc%2FIOIIPR%2Fall%2FOIchg%2Fdesc%3Fresponsetype%3Djson".format(expiry=expiry)
    return _getIndiaInfoOnlineJson(url)

print(getIndexLongBuildUp())