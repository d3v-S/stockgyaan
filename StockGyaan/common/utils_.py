import datetime

import requests, pickle, requests_cache, time


def setUpParent(parent):
    if parent is None:
        return (None, None, None)
    else:
        if not hasattr(parent, "log") or not hasattr(parent, "status"):
            return (None, None, None)
        return (parent, parent.log, parent.status)


def setLocation(location, filename):
    if location is not None:
        return (location + filename)
    else:
        return None



# logging
def dbg(obj, string):
    if obj is not None and hasattr(obj, "log") and obj.log is not None:
        s = "{:<20s}{:<20s}".format(type(obj).__name__,str(time.time()))
        obj.log.debug(s + "\t--->\t" + string)


def dbgOK(obj, string):
    end = "{:<100s}{:<15s}".format(string, ":: [OK]")
    dbg(obj, end)


def dbgErr(obj, string):
    end = "{:<100s}{:<15s}".format(string, ":: [ERR]")
    dbg(obj, end)


def dbgDld(obj, string):
    end = "{:<100s}{:<15s}".format(string, ":: [DOWNLOAD]")
    dbg(obj, end)


def dbgCharts(obj, string):
    end = "{:<100s}{:<15s}".format(string, ":: [CHARTS]")
    dbg(obj, end)



def info(obj, string, color=None):
    if obj is not None:
        if obj.status is not None:
            s = "{:<10s} ".format(str(datetime.datetime.now().time()))
            obj.status.info(s + string, color=color)


INFO_START_COLOR = "blue"
INFO_FINISHED_COLOR = "green"
INFO_ERROR_COLOR = "red"

def infoStart(obj, text=None):
    info(obj, "[STARTED] " + str(text), color=INFO_START_COLOR)

def infoFinished(obj, text=None):
    info(obj, "[FINISHED] " + str(text), color=INFO_FINISHED_COLOR)

def infoError(obj, text=None):
    info(obj, "[ERROR] " + str(text), color=INFO_ERROR_COLOR)





       
def err(obj, string):
    if obj is not None:
        if obj.status is not None:
            obj.status.err(string)


def defaultSlot(obj, slot_type=None, name=None):
    string = "{slot_type} is not defined for widget - {name}".format(slot_type=slot_type, name=name)
    err(obj, string)

##
# Everything needs to save status.
##

def checkTypeObject(obj, t, status=None):
    if isinstance(obj, t):
        return obj
    return None


def checkTypeData(obj, t):
    if type(obj) is t:
        return obj
    return None

##
# Status management
##

STATUS_KEY = "STATUS"
STATUS_DATA = "DATA"

STATUS_SUBMITTED = "SUBMIT"
STATUS_FINISHED = "FINISHED"
STATUS_STARTED = "STARTED"
STATUS_ERROR = "ERROR"

def statusUpdate(status_dict, text, data):
    if status_dict is not None:
        status_dict[STATUS_KEY] = str(text)
        status_dict[STATUS_DATA] = str(data)

def getStatus(status_dict):
    if status_dict is not None:
        if STATUS_KEY in status_dict.keys():
            return status_dict[STATUS_KEY]

def getStatusData(status_dict):
    if status_dict is not None:
        if STATUS_DATA in status_dict.keys():
            return status_dict[STATUS_DATA]


def statusSubmitted(status_dict, data=None):
    statusUpdate(status_dict, STATUS_SUBMITTED, data)
    
def statusFinished(status_dict, data=None):
    statusUpdate(status_dict, STATUS_FINISHED, data)

def statusStarted(status_dict, data=None):
    statusUpdate(status_dict, STATUS_STARTED, data)

def statusError(status_dict, data=None):
    statusUpdate(status_dict, STATUS_ERROR, data)




##
# internet utils.
##

def _doNothing(something):
    return something
 
def _requestData(url, func=_doNothing, return_type="text", status_dict=None):
    try:
        statusStarted(status_dict, "URL: " + str(url))
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            if return_type == "text":
                return func(res.text)
            if return_type == "content":
                return func(res.content)
            return func(res)

        print("_request Data : Error code for url: " + str(url))
    except requests.exceptions.Timeout:
        print("_request Data : Timeout for url: " + str(url))
        return None
    

def getURL(url, func=_doNothing, cache=False, return_type="text"):
    if not cache:
        with requests_cache.disabled():
            return _requestData(url, func = func, return_type=return_type)
    else:
        if requests_cache.patcher.is_installed():
            return _requestData(url, func = func, return_type=return_type)

    
    
##
# serializing
##

def objToFile(obj, filename):
    dbfile = open(filename, 'wb')    
    pickle.dump(obj, dbfile)                     
    dbfile.close()

def fileToObj(filename):
    dbfile = open(filename, 'rb')     
    db = pickle.load(dbfile)
    dbfile.close()
    return db



##
# image utils
##

import io
from PIL import Image



def __resizeImageWidth(img, width):
    wpercent = (width/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    return img.resize((width,hsize), Image.ANTIALIAS)

def __resizeImageHeight(img, height):
    hpercent = (height/float(img.size[1]))
    wsize = int((float(img.size[0]*float(hpercent))))
    return img.resize((wsize, height), Image.ANTIALIAS)



# keep aspect ratio same on resizing downloaded data.
def resizeImageKeepingAspectRatio(img_data, limit_width, limit_height=None):
    img = Image.open(img_data)
    w = img.size[0]
    h = img.size[1]
    if w > limit_width:
        img = __resizeImageWidth(img, limit_width)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        return bio.getvalue()
    else:
        if limit_height != None:
            if h > limit_height:
                img = __resizeImageHeight(img, limit_height)
                bio = io.BytesIO()
                img.save(bio, format="PNG")
                return bio.getvalue()
    return img_data.getvalue()




def loadImageUrl(url, url_cache=None):
    if url_cache:
        if url in url_cache.keys():
            print("Cache data for url: " + str(url))
            return url_cache[url]
        else:
            data = _requestData(url, return_type="response")
            url_cache[url] = data
            print("Downloading image data: " + str(data))
            return data
    else:
        data = _requestData(url, return_type="response")
        print("Downloading image data: " + str(data))
        return data
    
##
# string to bool
##
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
    
##
# Constants
##
APP_NAME = "StockGyaan"
DEFAULT_FOLDER = "/home/d3v/StockGyan/"
DOWNLOAD_FOLDER = DEFAULT_FOLDER + "downloads/"
CONFIG_FILE = DEFAULT_FOLDER + "config.cfg"
DOWNLOAD_OPTIONCHAIN_FOLDER = DEFAULT_FOLDER + "optionchain/"

STOCK = "stocks"
INDEX = "index"



STRING_DOWNLOAD_STARTED = "starting download [{source}][{symbol}]"
STRING_DOWNLOAD_FINISHED = "download finished [{source}][{symbol}]"
STRING_DOWNLOAD_ERROR = "error in download. [{source}][{symbol}]"



