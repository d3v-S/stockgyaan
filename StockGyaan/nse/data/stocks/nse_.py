from nsetools import Nse

from common.utils_ import STOCK, INDEX


def validateNameFromNse(name):
    try:
        nse = Nse()
        if nse.is_valid_code(name):
            return (name, STOCK)
        if nse.is_valid_index(name):
            return (name, INDEX)
        if "NIFTY" in name:
            new_name = name.replace("NIFTY", "")
            index_list = nse.get_index_list()
            for s in index_list:
                if new_name in s:
                    symbol = s
                    return (s, INDEX)
    except:
        return None


def getQuote(name):
    try:
        nse=Nse()
        if nse.is_valid_code(name):
            return nse.get_quote(name)
        if nse.is_valid_index(name):
            return nse.get_index_quote(name)
    except:
        return None

