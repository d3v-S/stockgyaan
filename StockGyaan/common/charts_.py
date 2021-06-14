from PyQt5.QtWidgets import *

import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.tz import gettz

import finplot as fplt
import pandas_ta as ta


def setCandleStickColors(foreground="#777", background="#090c0e", candle_bull="#380", candle_bear="#a23", cross_hair="#888", max_zoom_points=5):
    #fplt.max_zoom_points = max_zoom_points
    fplt.foreground = foreground
    fplt.background = background
    fplt.candle_bull_color = fplt.candle_bull_body_color = candle_bull
    fplt.candle_bear_color = candle_bear
    volume_transparency = 'c'
    fplt.volume_bull_color = fplt.volume_bull_body_color = fplt.candle_bull_color + volume_transparency
    fplt.volume_bear_color = fplt.candle_bear_color + volume_transparency
    fplt.cross_hair_color = fplt.foreground+'8'
    fplt.draw_line_color = cross_hair
    fplt.draw_done_color = '#555'
    fplt.display_timezone = gettz('GMT')

####
## private methods:
####
cs_keys = ["Open", "Close", "High", "Low"]
ha_keys = ['h_open','h_close','h_high','h_low']
ema_keys = ['Close']
vma_keys = ['Volume']

# rsi
def plotRsi(df, ax, key="Close", period=14):
    """ plotting rsi
    """
    diff = df[key].diff().values
    gains = diff
    losses = -diff
    with np.errstate(invalid='ignore'):
        gains[(gains<0)|np.isnan(gains)] = 0.0
        losses[(losses<=0)|np.isnan(losses)] = 1e-10 # we don't want divide by zero/NaN
    n = 14
    m = (n-1) / n
    ni = 1 / n
    g = gains[n] = np.nanmean(gains[:n])
    l = losses[n] = np.nanmean(losses[:n])
    gains[:n] = losses[:n] = np.nan
    for i,v in enumerate(gains[n:],n):
        g = gains[i] = ni*v + m*g
    for i,v in enumerate(losses[n:],n):
        l = losses[i] = ni*v + m*l
    rs = gains / losses
    df['rsi'] = 100 - (100/(1+rs))
    df.rsi.plot(ax=ax, legend='RSI')
    fplt.set_y_range(0, 100, ax=ax)
    fplt.add_band(30, 70, ax=ax)

# ema
def plotEma(df, ax, ema):
    return df["Close"].ewm(span=ema).mean().plot(ax=ax, legend='EMA')

# vma
def plotVma(df, ax):
    return df["Volume"].rolling(20).mean().plot(ax=ax, color='#c0c030')

# candles
def plotCandles(df, ax, candle_width=0.6):
    return fplt.candlestick_ochl(df[cs_keys], ax=ax, candle_width=candle_width)



## --- PANDAS_TA changes the dataframes to smaller case--- ##


# supertrend using pandas_ta
def plotSuperTrend(df, ax, period=7, multiplier=3):
    highSeries = df["High"]
    lowSeries = df["Low"]
    closeSeries = df["Close"]
    #copy_df = df.copy()
    st = df.ta.supertrend(high=highSeries, low=lowSeries, close=closeSeries,
                     period=period, multiplier=multiplier, append=False)
    #st.plot(ax=ax)
    df1 = pd.to_numeric(st["SUPERT_7_3.0"]).to_frame()
    df1["SUPERT_7_3.0"].plot(ax=ax)


# stochrsi using pandas_ta
def plotStochRsi(df, ax, window=30, smooth1 = 3, smooth2=7):
    #copy_df = df.copy()
    srsi = df.ta.stochrsi(window=window, smooth1=smooth1, smooth2=smooth2)
    srsi.plot(ax = ax)

## cci using pandas_ta
def plotCCI(df, ax, window=15):
    highSeries = df["High"]
    lowSeries = df["Low"]
    closeSeries = df["Close"]
    # copy_df = df.copy()
    st = df.ta.cci(high=highSeries, low=lowSeries, close=closeSeries,
                        window=window, constant=2, append=False)
    st.plot(ax=ax)

## stoch using pandas_ti
def plotStoch(df, ax, window= 20, smooth_period=5):
    highSeries = df["High"]
    lowSeries = df["Low"]
    closeSeries = df["Close"]
    # copy_df = df.copy()
    st = df.ta.cci(high=highSeries, low=lowSeries, close=closeSeries,
                   window=window, smooth_window=smooth_period, append=False)
    st.plot(ax=ax)


## ------ Pandas TA ---- ##


# ha
def plotHA(df, ax):
    df['h_close'] = (df.Open+df.Close+df.High+df.Low) / 4
    ho = (df.Open.iloc[0] + df.Close.iloc[0]) / 2
    for i,hc in zip(df.index, df['h_close']):
        df.loc[i, 'h_open'] = ho
        ho = (ho + hc) / 2
    print(df['h_open'])
    df['h_high'] = df[['High','h_open','h_close']].max(axis=1)
    df['h_low'] = df[['Low','h_open','h_close']].min(axis=1)
    return df[['h_open','h_close','h_high','h_low']].plot(ax=ax, kind='candle')

# ha volume
def plotHAVolume(df, ax):
    df[['h_open','h_close','volume']].plot(ax=ax, kind='volume')

def updateCharts(df, plot_ax):
    plot_ax.update_data(df, gfx=False)
    plot_ax.update_gfx()

def updateCandles(df, plot_ax):
    df = df[cs_keys]
    updateCharts(df, plot_ax)









