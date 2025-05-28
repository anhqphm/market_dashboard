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

from dash.exceptions import PreventUpdate


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
    html.Div(['Select Ticker: ',
        dcc.Input(id='ticker-input', value = 'SPX', type='text')
        ]),
    html.Br(),
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=date(1990,1,1),
        max_date_allowed=date.today(),
        start_date=date(2000,1,1),
        # initial_visible_month=date.today()+ dt.timedelta(days=-42),
        end_date=date.today()
    ),

    dcc.Store(id='hist-data'),
    html.Br(),
    html.Div(id='company-info'),
    # dash_table.DataTable(id='hist-data'),
    dcc.Graph(id='price-chart')
    
])



# Getting data

# params: Ticker, start date, end date

@app.callback(
        Output("hist-data","data"),
        Output("company-info","children"),
        Input("ticker-input","value"),
        Input("date-picker-range","start_date"),
        Input("date-picker-range", "end_date"),
        prevent_intial_call=True
)
def get_yf_hist_data(ticker, start_dt, end_dt):
    ticker_data = yf.Ticker(ticker)
    ticker_hist = ticker_data.history(start=start_dt, end=end_dt).reset_index()
    ticker_hist['Date']= pd.to_datetime(ticker_hist['Date']).dt.date

    ticker_fin = ticker_data.info
    try:
        ticker_fin_out = html.Div([
            html.P("Company Sector: " + ticker_fin['sector']),
            html.P("P/E Ratio: " + str(ticker_fin['trailingPE'])),
            html.P("Company Beta: " + str(ticker_fin["beta"]))
        ])
    except:
        ticker_fin_out = html.Div('')


    return ticker_hist.to_dict('records'), ticker_fin_out



@app.callback(
    Output('price-chart','figure'),
    Input("hist-data","data")
)
def update_price_graph(hist_data):
    df = pd.DataFrame(hist_data)
    price_fig = px.line(df,
                        x=df['Date'],
                        y = df['Close'],
                        template='plotly_white')
    # price_fig.update_layout()
    return price_fig



if __name__ == '__main__':
    app.run(debug=True)


