import requests
from bs4 import BeautifulSoup


def get_chartink_stocks(url, scan_clause):
    with requests.Session() as s:
        scanner_url = url #'https://chartink.com/screener/vishal-mehta-mean-reversion'
        r = s.get(scanner_url)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf = soup.select_one("[name='csrf-token']")['content']
        s.headers['x-csrf-token'] = csrf
        process_url = 'https://chartink.com/screener/process'
        payload = {
            # NOTE Vishal Mehta Mean Reversion Selling - Place Limit Order at 1% of Latest Close Price 3% SL and 6% Target Exit all positions at 3PM
            'scan_clause': scan_clause #'( {33489} ( latest close > latest sma( close, 200 ) and latest rsi( 2 ) > 50 and '\
            #'latest close > 1 day ago close * 1.03 and latest close > 200 and latest close < 5000 and latest close > ( 4 days ago close * 1.0 ) ) ) '
        }

        r = s.post(process_url, data=payload)
        return r.json()['data']