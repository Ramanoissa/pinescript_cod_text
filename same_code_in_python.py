import numpy as np
import pandas as pd
import binance.client
from binance.client import Client


pkey= "api_key"

skey= "secret_key"

client= Client(api_key=pkey, api_secret=skey)

def add_to_array(apointer1, apointer2, val):
    apointer1.insert(0, val)
    apointer2.insert(0, len(apointer1)-1)
    apointer1.pop()
    apointer2.pop()

def trendlines_and_sma(df, _period=24, PivotPointNumber=6, up_trend_color='lime', down_trend_color='red'):
    pivot_high = pd.Series(np.nan, index=df.index)
    pivot_low = pd.Series(np.nan, index=df.index)
    trend_top_values = [np.nan] * PivotPointNumber
    trend_top_position = [np.nan] * PivotPointNumber
    trend_bottom_values = [np.nan] * PivotPointNumber
    trend_bottom_position = [np.nan] * PivotPointNumber
    bottom_lines = [None] * 3
    top_lines = [None] * 3
    maxline = 3
    count_line_low = 0
    count_line_high = 0
    starttime = 0

    for i in range(len(df)):
        if not pd.isnull(pivot_high[i]):
            add_to_array(trend_top_values, trend_top_position, pivot_high[i])

        if not pd.isnull(pivot_low[i]):
            add_to_array(trend_bottom_values, trend_bottom_position, pivot_low[i])

        if i >= starttime:
            for x in range(maxline):
                if bottom_lines[x] is not None:
                    bottom_lines[x].remove()
                if top_lines[x] is not None:
                    top_lines[x].remove()

            for pivot1 in range(PivotPointNumber - 1):
                up_val1 = 0.0
                up_val2 = 0.0
                up1 = 0
                up2 = 0

                if count_line_low <= maxline:
                    for pivot2 in range(PivotPointNumber - 1, pivot1, -1):
                        value1 = trend_bottom_values[pivot1]
                        value2 = trend_bottom_values[pivot2]
                        position1 = trend_bottom_position[pivot1]
                        position2 = trend_bottom_position[pivot2]

                        if value1 > value2:
                            different = (value1 - value2) / (position1 - position2)
                            high_line = value2 + different
                            low_location = i
                            low_value = df['low'][i]
                            valid = True

                            for j in range(position2 + 1 - _period, i+1):
                                if df['close'][i-j] < high_line:
                                    valid = False
                                    break
                                low_location = j
                                low_value = high_line
                                high_line += different

                            if valid:
                                up_val1 = high_line - different
                                up_val2 = value2
                                up1 = low_location
                                up2 = position2
                                break

                d_value1 = 0.0
                d_value2 = 0.0
                d_position1 = 0
                d_position2 = 0

                if count_line_high <= maxline:
                    for pivot2 in range(PivotPointNumber - 1, pivot1, -1):
                        value1 = trend_top_values[pivot1]
                        value2 = trend_top_values[pivot2]
                        position1 = trend_top_position[pivot1]
                        position2 = trend_top_position[pivot2]

                        if value1 < value2:
                            different = (value2 - value1) / (position2 - position1)
                            high_line = value2 - different
                            low_location = i
                            low_value = df['high'][i]
                            valid = True

                            for j in range(position2 + 1 - _period, i+1):
                                if df['close'][i-j] > high_line:
                                    valid = False
                                    break
                                low_location = j
                                low_value = high_line
                                high_line -= different

                            if valid:
                                d_value1 = high_line + different
                                d_value2 = value2
                                d_position1 = low_location
                                d_position2 = position2
                                break

                if up1 != 0 and up2 != 0 and count_line_low < maxline:
                    count_line_low += 1
                    bottom_lines[count_line_low-1] = (up2 - _period, up_val2, up1, up_val1, up_trend_color)

                if d_position1 != 0 and d_position2 != 1 and count_line_high < maxline:
                    count_line_high += 1
                    top_lines[count_line_high-1] = (d_position2 - _period, d_value2, d_position1, d_value1, down_trend_color)

    return bottom_lines, top_lines

def smacross(df, smafastin=21, smaslowin=55):
    smafast = df['close'].rolling(window=smafastin).mean()
    smaslow = df['close'].rolling(window=smaslowin).mean()
    crossup = (smafast.shift() < smaslow.shift()) & (smafast > smaslow)
    crossdn = (smafast.shift() > smaslow.shift()) & (smafast < smaslow)
    return smafast, smaslow, crossup, crossdn
