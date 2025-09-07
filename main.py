import math
import datetime as dt

import numpy as np
import yfinance as yf

from bokeh.io import curdoc
from bokeh.plotting import figure 
from bokeh.layouts import row, column
from bokeh.models import TextInput, Button, DatePicker, MultiChoice


# Data Loader
def load_data(ticker1, ticker2, start, end):
    df1 = yf.download(ticker1, start=start, end=end)[["Open", "High", "Low", "Close"]].copy()
    df2 = yf.download(ticker2, start=start, end=end)[["Open", "High", "Low", "Close"]].copy()
    for df in (df1, df2):
        for col in df.columns:
            df[col] = df[col].astype(float)
    return df1, df2


# Plot builder
def plot_data(data, indicators, sync_axis=None):
    df = data

    open_prices = df["Open"].squeeze()
    close_prices = df["Close"].squeeze()
    high_prices = df["High"].squeeze()
    low_prices = df["Low"].squeeze()

    gain = close_prices > open_prices
    loss = open_prices > close_prices
    width = 12 * 60 * 60 * 1000  # half-day in ms for vbar

    if sync_axis is not None:
        p = figure(
            x_axis_type="datetime",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            width=1000,
            x_range=sync_axis
        )
    else:
        p = figure(
            x_axis_type="datetime",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            width=1000
        )
    
    p.xaxis.major_label_orientation = math.pi / 4
    p.grid.grid_line_alpha = 0.25

    # candlestick chart
    p.segment(df.index, high_prices, df.index, low_prices, color="black")
    p.vbar(df.index[gain], width, open_prices[gain], close_prices[gain],
           fill_color="#00ff00", line_color="#00ff00")
    p.vbar(df.index[loss], width, open_prices[loss], close_prices[loss],
           fill_color="#ff0000", line_color="#ff0000")

    # indicators
    for indicator in indicators:
        if indicator == "30 Day SMA":
            df["SMA30"] = close_prices.rolling(30).mean()
            p.line(df.index, df["SMA30"], color="purple", legend_label="30 Day SMA")
        elif indicator == "100 Day SMA":
            df["SMA100"] = close_prices.rolling(100).mean()
            p.line(df.index, df["SMA100"], color="blue", legend_label="100 Day SMA")
        elif indicator == "Linear Regression Line":
            x = np.arange(len(df.index))
            par = np.polyfit(x, close_prices.values, 1, full=True)
            slope, intercept = par[0]
            y_pred = slope * x + intercept
            p.line(df.index, y_pred, color="red", legend_label="Linear Regression")

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    return p


# Button functions
plot_area = column()  # empty container for plots

def on_button_click():
    ticker1, ticker2 = stock1_text.value, stock2_text.value
    start, end = date_picker_from.value, date_picker_to.value
    indicators = indicator_choice.value
    if not ticker1 or not ticker2:
        return
    df1, df2 = load_data(ticker1, ticker2, start, end)
    p1 = plot_data(df1, indicators)
    p2 = plot_data(df2, indicators, sync_axis=p1.x_range)
    plot_area.children = [row(p1, p2)]

# UI
stock1_text = TextInput(title="Stock 1 (e.g. AAPL)")
stock2_text = TextInput(title="Stock 2 (e.g. MSFT)")

date_picker_from = DatePicker(
    title="Start Date", 
    value="2020-01-01", 
    min_date="2000-01-01",
    max_date=dt.datetime.now().strftime("%Y-%m-%d")
)
date_picker_to = DatePicker(
    title="End Date", 
    value="2020-02-01", 
    min_date="2000-01-01",
    max_date=dt.datetime.now().strftime("%Y-%m-%d")
)

indicator_choice = MultiChoice(
    options=["100 Day SMA", "30 Day SMA", "Linear Regression Line"]
)

load_button = Button(label="Load Data", button_type="success")
load_button.on_click(on_button_click)


# Layout
layout = column(
    stock1_text,
    stock2_text,
    date_picker_from,
    date_picker_to,
    indicator_choice,
    load_button,
    plot_area
)

curdoc().add_root(layout)

