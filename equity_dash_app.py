import numpy as np
import pandas as pd

import yfinance as yf
import datetime as dt
from datetime import date
# import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

import dash
from dash import Dash, dcc, html, dash_table, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash.exceptions import PreventUpdate

from technical_analysis import (get_support_resistance_fractal_candlestick,
                                 get_support_resistance_window_shift, 
                                 has_breakout)

# Load external style
external_stylesheets = [
    {  "href": "https://fonts.googleapis.com/css2?"
                "family=Roboto:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
    dbc.themes.BOOTSTRAP
]

# Setting up the app
app = Dash(__name__,
           external_stylesheets=external_stylesheets,
           suppress_callback_exceptions=True)

app.title = "Equity Dashboard"

app.layout = html.Div([
    html.H1('Equity research dashboard'),
    dbc.Row([
        dbc.Col(
            html.Div(['Select Ticker: ', 
                      dcc.Input(id='ticker-input', value = '^SPX', type='text')
                      ])),
        dbc.Col(
            html.Div([
                'Select Date Range: ',
                dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=date(1990,1,1),
                max_date_allowed=date.today(),
                start_date=date(2025,1,1),
                # initial_visible_month=date.today()+ dt.timedelta(days=-42),
                end_date=date.today())
            ]))]),
    dcc.Store(id='hist-data'),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='price-chart'),width=9),
        dbc.Col(html.Div(id='company-info'),width=3)
    ]),

      
])



# Getting data

# params: Ticker, start date, end date

@app.callback(
        Output("hist-data","data"),
        Output("company-info","children"),
        Output('price-chart','figure'),
        Input("ticker-input","value"),
        Input("date-picker-range","start_date"),
        Input("date-picker-range", "end_date"),
        prevent_intial_call=True
)
def get_yf_hist_data(ticker, start_dt, end_dt):
    ticker_data = yf.Ticker(ticker)
    df_hist = ticker_data.history(start=start_dt, end=end_dt).reset_index()
    df_hist = df_hist.dropna()
    df_hist['Date']= pd.to_datetime(df_hist['Date']).dt.date
    

    dt_obs = [d.strftime("%Y-%m-%d") for d in df_hist["Date"]]
    dt_all = pd.date_range(start=list(df_hist['Date'])[0], end = list(df_hist['Date'])[-1])
    dt_missing =  [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
    levels = get_support_resistance_fractal_candlestick(df_hist,42)

     # Get breakout levels
    brkout_text = ""
    if has_breakout(levels[-5:], df_hist.iloc[-2],df_hist.iloc[-1]):
        brkout_text = f"{ticker} just broke out of levels"
   
    # Get company names
    ticker_fin = ticker_data.info
    try:
        ticker_fin_out = html.Div([
            html.P(brkout_text),
            html.P("Company Sector: " + ticker_fin['sector']),
            html.P("P/E Ratio: " + str(ticker_fin['trailingPE'])),
            html.P("Company Beta: " + str(ticker_fin["beta"]))
        ])
    except:
        ticker_fin_out = html.Div(
            html.P(brkout_text)
            )

    # Moving Average
    df_hist['MA5'] = df_hist['Close'].rolling(window=5).mean()
    df_hist['MA20'] = df_hist['Close'].rolling(window=20).mean()

    # Stochastic
    

    # fig = go.Figure()
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.01,
        row_width=[0.2,0.7]
    )
    fig.add_trace(
        go.Candlestick(x=df_hist['Date'],
                       open=df_hist['Open'],
                       high=df_hist['High'],
                       low=df_hist['Low'],
                       close=df_hist['Close'],
                       name='OHLC')
                       ,row=1,col=1
                       )
    fig.add_trace(
        go.Scatter(x=df_hist['Date'],
                   y=df_hist['MA5'],
                   opacity=0.7,
                   line=dict(color='blue',width=2),
                   name='MA 5')
    )
    fig.add_trace(
        go.Scatter(x=df_hist['Date'],
                   y = df_hist['MA20'],
                   opacity=0.7,
                   line=dict(color='orange',width=2),
                   name='MA 20')
    )
    for level in levels:
        fig.add_hline(y=level[1],
                      x0=df_hist['Date'][level[0]],
                      x1=max(df_hist['Date']),
                      line_dash='dash')
    fig.update_xaxes(rangebreaks=[dict(values=dt_missing)]) # remove missing dates
    fig.update_layout(xaxis_rangeslider_visible=False) # remove weird slider

    # Update Volume colors if Open < Close price increase: green
    colors = ['green' if row['Close'] - row['Open'] >= 0 else 'red' for index,row in df_hist.iterrows()]

    fig.add_trace(go.Bar(x=df_hist['Date'],
                         y=df_hist['Volume'],
                         showlegend=False,
                         marker_color=colors),
                         row=2,col=1
    )
    

    fig.update_layout(
        title= ticker + " Live Share Price: "
    )
    
    # add chart title 
    fig.update_yaxes(title_text="Price", row=1,col=1)
    fig.update_yaxes(title_text='Volume', row=2,col=1)

    return  df_hist.to_dict('records'), ticker_fin_out, fig



## ML

# @app.callback(
#     Output('price-chart','figure'),
#     Input("hist-data","data")
# )
# def update_price_graph(hist_data):
#     df = pd.DataFrame(hist_data)
#     fig = go.Figure()
#     # fig = make_subplots(
#     #     rows=2, cols=1, shared_xaxes=True,
#     #     vertical_spacing=0.03, subplot_titles=('OHLC', 'Volume'),
#     #     row_width=[0.2,0.7]
#     # )
#     fig.add_trace(
#         go.Candlestick(x=df['Date'],
#                        open=df['Open'],
#                        high=df['High'],
#                        close=df['Close'],
#                        name='OHLC'),
#                        row=1, col=1
#     )
#     fig.add_trace(go.Bar(x=df['Date'],
#                          y=df['Volume'],
#                          showlegend=False),
#                          row=2,col=1)
#     fig.update(layout_xaxis_rangeslider_visible=False)
#     return fig



if __name__ == '__main__':
    app.run(debug=True)


