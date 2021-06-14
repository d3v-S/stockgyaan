from bs4 import BeautifulSoup as bs
import requests, feedparser


class DataStreamNews:
    # err:

    # telegram rss-bridge
    feed_telegram_base = "https://rss-bridge.bb8.fun/?action=display&bridge=Telegram&username={username}&format=Atom"
    feed_telegram_keys = ["content", 0, "value"]

    # nitter rss : twitter hashtag
    # https://github.com/zedeus/nitter/wiki/Instances
    feed_nitter_domain = ["nitter.cc", "nitter.kavin.rocks", "nitter.eu", "nitter", "nitter.exonip.de"]
    feed_nitter_base = "https://{domain}/search/rss?f=tweets&q=%23{hashtag}"
    feed_nitter_keys = ["summary_detail", "value"]

    # tradingview:
    site_tradingview_base = "https://in.tradingview.com/symbols/{symbol}/ideas/"
    site_tradingview_page = "https://in.tradingview.com/symbols/{symbol}/ideas/page-{page}"

    @classmethod
    def __getFeedData(cls, url, keys):
        try:
            res = requests.get(url, timeout=5)
            list_ = []
            if res.status_code == 200:
                feed = feedparser.parse(res.text)
                for entries in feed["entries"]:
                    # print(entries)
                    d = {}
                    html = entries  # keys = ["content", 0, values]
                    for key in keys:
                        html = html[key]  # html = entries["content"][0]["values"]
                    soup = bs(html, "html.parser")
                    d["published"] = entries["published"]
                    d["author"] = entries["author"]
                    d["text"] = soup.text
                    d["imgs"] = []
                    for i in soup.find_all('img'):
                        d["imgs"].append(i["src"])
                    list_.append(d)
                return list_
            else:
                print(url + " : ERROR : in data retrieval :  " + str(res.status_code))
                return None
        except requests.exceptions.Timeout:
            print(url + " : ERROR : TIMEOUT")
            return None

    @classmethod
    def getTradingViewData(cls, symbol, page=None):
        url = cls.site_tradingview_base.format(symbol=symbol)
        if page:
            url = cls.site_tradingview_page.format(symbol=symbol, page=page)
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                list_ = []
                soup = bs(res.text, 'html.parser')
                # assumption bs4 find_all is sequential
                t_img = soup.find_all(class_="tv-widget-idea__cover")
                t_author = soup.find_all(class_="tv-card-user-info__name")
                t_summary = soup.find_all(class_="tv-widget-idea__description-row")
                t_published = soup.find_all(class_="tv-card-stats__time")
                # print(t_img)
                # print("\n***************************\n")
                # print(t_author)
                # print("\n***************************\n")
                # print(t_summary)

                for i, item in enumerate(t_img):
                    d = {}
                    d["published"] = t_published[i]["data-timestamp"]
                    d["author"] = t_author[i].text
                    d["text"] = t_summary[i].text
                    d["imgs"] = [item["data-src"]]
                    list_.append(d)
                return list_
            else:
                print(url + " : ERROR : in data retrieval :  " + str(res.status_code))
                return None
        except requests.exceptions.Timeout:
            print(url + " : ERROR : TIMEOUT")
            return None

    @classmethod
    def getTwitterHashTagFeed(cls, hashtag):
        url = None
        for domain in cls.feed_nitter_domain:
            url = cls.feed_nitter_base.format(domain=domain, hashtag=hashtag)
            ret = cls.__getFeedData(url, cls.feed_nitter_keys)
            if ret == None:
                continue
            return ret
        return None

    @classmethod
    def getTelegramChannelFeed(cls, username):
        url = cls.feed_telegram_base.format(username=username)
        return cls.__getFeedData(url, cls.feed_telegram_keys)


def getTwitterHashTagFeed(hashtag):
    return DataStreamNews.getTwitterHashTagFeed(hashtag)


def getTelegramChannelFeed(hashtag):
    return DataStreamNews.getTelegramChannelFeed(hashtag)


def getTradingViewData(symbol, page=None):
    return DataStreamNews.getTradingViewData(symbol)


#
# Pulse Zerodha
#
class ZerodhaPulse:
    def __init__(self):
        self.url = "https://pulse.zerodha.com/"
        self.stories = []

    def parseZerodhaPulse(self):
        res = requests.get(self.url)
        if res.status_code != 200:
            return []
        soup = bs(res.text, "html.parser")
        list_titles = []
        list_soup_titles = soup.find_all(class_="title")
        for soup_title in list_soup_titles:
            d = {}
            d["link"] = soup_title.find('a')['href']
            d["title"] = soup_title.text
            d["desc"] = soup_title.parent.findNext(class_='desc').text
            list_titles.append(d)
        return list_titles

