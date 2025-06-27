
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## Method 1: Fractal candlestick pattern

def is_support(df,i):
    cond1 = df['Low'][i] < df['Low'][i-1]
    cond2 = df['Low'][i] < df['Low'][i+1]
    cond3 = df['Low'][i-1] < df['Low'][i-2]
    cond4 = df['Low'][i+1] < df['Low'][i+2]
    return cond1 and cond2 and cond3 and cond4

def is_resistance(df,i):
    cond1 = df['High'][i] > df['High'][i-1]
    cond2 = df['High'][i] > df['High'][i+1]
    cond3 = df['High'][i-1] > df['High'][i-2]
    cond4 = df['High'][i+1] > df['High'][i+2]
    return cond1 and cond2 and cond3 and cond4

def is_far_from_level(value, levels,df):
    ave = np.mean(df['High']- df['Low'])
    return np.sum([abs(value-level)<ave for _,level in levels]) == 0

def get_support_resistance_fractal_candlestick(df,lookback_dates=42):
    df_ = df.copy()#.tail(lookback_dates).copy().reset_index(drop=True)
    levels = []
    for i in range(2, df_.shape[0]-3):
        if is_support(df_,i):
            low = df_['Low'][i]
            if is_far_from_level(low, levels,df_):
                levels.append((i,low))
        elif is_resistance(df_,i):
            high = df_['High'][i]
            if is_far_from_level(high,levels,df_):
                levels.append((i,high))
    return levels

## Method 2: window shifting

def get_support_resistance_window_shift(df,lookback_dates=42):
    df_ = df.copy()#tail(lookback_dates).copy().reset_index(drop=True)
    levels = []
    max_list = []
    min_list = []

    for i in range(5,len(df_)-5):
        # take window of 9 candles
        high_range = df_['High'][i-5:i+4]
        current_max = high_range.max()
        if current_max not in max_list:
            max_list = []
        max_list.append(current_max)
        # if max val remains unchanged after 5 session
        if len(max_list) == 5 and is_far_from_level(current_max,levels,df_):
            levels.append((high_range.idxmax(),current_max))

        low_range = df_['Low'][i-5:i+4]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list) == 5 and is_far_from_level(current_min,levels,df_):
            levels.append((low_range.idxmin(),current_min))
    return levels


## Method 3: Machine Learning K means
    
## Screen for stock just had breakout

def has_breakout(levels, previous, last):
    for _, level in levels:
        cond1 = previous['Open'] < level
        cond2 = (last['Open'] > level) and (last['Low'] > level)
    return cond1 and cond2
