# Import libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import psycopg2
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import datetime
import math

## Function for loading financial data from our database using SQL JOIN
def load_data():
    conn = psycopg2.connect(
        database = 'cuzegotk',
        user = 'cuzegotk',
        password = 'NekW2BqJ8hW1wO3hCdpuEESPiP-y131V',
        host = 'raja.db.elephantsql.com'
    )
    cur = conn.cursor()
    cur.execute('SELECT F.ticker, F.last_year, F.year, F.revenue, F.revenue_ly, B.quarter_end, Q.revenue, Q.gross_profit, Q.operating_profit, Q.net_income, B.total_assets, B.total_liabilities, B.intangible_assets, B.shareholders_equity, S.shares_outstanding, L.sector, M.predicted, M.rating FROM companyfinancials F JOIN companyquarterends Q on F.ticker = Q.ticker JOIN companybalancesheets B ON Q.ticker = B.ticker JOIN sharesoutstanding S ON S.ticker = B.ticker JOIN modelpredictions M on M.ticker = S.ticker JOIN companylisting L ON S.ticker = L.ticker')
    data = cur.fetchall()
    cur.close()
    conn.close()

    columns = ['ticker', 'last_year', 'year', 'revenue_a', 'revenue_ly', 'quarter_end', 'revenue_q', 'gross_profit', 'operating_profit', 'net_income', 'total_assets', 'total_liabilities', 'intangible_assets', 'shareholders_equity', 'shares_outstanding', 'sector', 'predicted', 'rating']
    df = pd.DataFrame(data, columns=columns)

    return df

## Loading data from database
df = load_data()

## Load Drop Down Bar
def load_dropdown():
    conn = psycopg2.connect(
        database = 'cuzegotk',
        user = 'cuzegotk',
        password = 'NekW2BqJ8hW1wO3hCdpuEESPiP-y131V',
        host = 'raja.db.elephantsql.com'
    )
    cur = conn.cursor()
    cur.execute('SELECT ticker, company  FROM companylisting')
    companies = cur.fetchall()
    cur.close()
    conn.close()

    return html.Div([
            dcc.Dropdown(
                    id='stock-search-bar',
                    placeholder='Enter Stock Ticker',
                    options=[{'label':i[0]+' - '+i[1], 'value':i[0]} for i in companies],
                    value='AMZN',
                    style={
                        'width': '50%',
                        'margin-left': '0.5em',
                        'margin-top': '1em',
                        'font-family': 'Courier New, Times, Helvetica',
                        'color': '#191919',
                    }
                )
            ])

# Dash Application
app = dash.Dash()
server = app.server

app.layout = html.Div([
    html.H1(
        children='Stock Dashboard',
        style={
            'width': '100%',
            'font-family': 'Courier New, Times, Helvetica',
            'text-align': 'left',
            'color': '#ffffff',
            'margin': '1em'
        }
    ),
    html.Hr(),
    load_dropdown(),
    html.H2(
        id='summary',
        children='Stock Summary',
        style={
            'width': '100%',
            'text-align': 'left',
            'margin': '1em',
            'font-family': 'Courier New, Times, Helvetica',
            'color': '#ffffff',
        }
    ),
    dcc.RadioItems(
        id='timeline',
        options=[
            {'label': '5D', 'value': 5},
            {'label': '1M', 'value': 23},
            {'label': '3M', 'value': 69},
            {'label': '6M', 'value': 138},
            {'label': '1Y', 'value': 252},
            {'label': '2Y', 'value': 504}
        ],
        value=5,
        style={
            'display': 'inline-block',
            'margin-left': '0.5em',
            'font-family': 'Courier New, Times, Helvetica',
            'color': '#ffffff',
        }
    ),
    html.Div([
        dcc.Graph(
            id='figure',
            figure={
                'data':[],
                'layout':go.Layout(
                    plot_bgcolor= '#191919',
                    paper_bgcolor= '#191919',
                    font= {
                        'color': '#ffffff'
                    }
                    )
            },
            style={
                'width':'47.5%',
                'margin-left': '0.5%',
                'float': 'left',
                'height': 'auto',
            }
        ),
        html.Div([
            html.H3(
                id='profile',
                children='Stock Profile',
                style={
                    'width': '100%',
                    'margin-top': '0',
                    'margin-left': '0.5%',
                    'font-family': 'Courier New, Times, Helvetica',
                    'color': '#ffffff',
                    }
            ),
            html.Hr(),
            html.Div([
                    html.P(
                        children='Predicted Rating:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='predicted-rating',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Last Trade Price:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='trade-price',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Market Cap:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='market-cap',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='As of Quarter-End:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='quarter-end',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Earnings per Share:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='eps',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Book Value per Share:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='bvs',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='YoY Revenue Growth:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='revenue-growth',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Gross Income / Margin:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='gross',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Operating Income / Margin:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='operating',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Net Income / Margin:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='net',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr()
                ],
                style={
                    'width':'48.5%',
                    'height':'500px',
                    'float': 'left',
                    'margin-left':'1%',
                    'margin-top':'0',
                }
            ),
            html.Div([
                    html.P(
                        children='Analyst Rating:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='analyst-rating',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Shares Outstanding:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='shares-outstanding',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Sector:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='sector',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Total Assets:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='assets',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children="Shareholders' Equity:",
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='equity',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Total Liabilities:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='liabilities',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Return on Equity:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='roe',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Return on Assets:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='roa',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Debt-to-Equity Ratio:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='debt-equity',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr(),
                    html.P(
                        children='Debt-to-Asset Ratio:',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-top': '0.5em',
                            'margin-bottom': '0.5em'
                        }
                    ),
                    html.P(
                        id='debt-asset',
                        children='N/A',
                        style={
                            'font-size': '1.25em',
                            'font-family': 'Courier New, Times, Helvetica',
                            'color': '#ffffff',
                            'margin-left': '1em',
                            'margin-top': '0',
                            'margin-bottom': '0'
                        }
                    ),
                    html.Hr()
                ],
                style={
                    'width':'48.5%',
                    'height':'500px',
                    'float': 'right',
                    'margin-right':'1%',
                    'margin-top':'0',
                }
            ),
            ],
            style={
                'width':'51.5%',
                'float': 'right'
            }
        )
        ],
        style={
            'width':'100%',
        }
    )
])

## Update Main Header based on ticker symbol
@app.callback(Output('summary', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        return '{} Stock Summary'.format(value)

## Update Secondary Header based on ticker symbol
@app.callback(Output('profile', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        return '{} Stock Profile'.format(value)

## Update Figure to display stock price chart based on ticker symbol
@app.callback(Output('figure', 'figure'), [Input('stock-search-bar', 'value'), Input('timeline', 'value')])
def update_output(ticker, days):

    data = web.DataReader(ticker.replace('.', '-'), 'yahoo', (datetime.datetime.now() - datetime.timedelta(days=735)).strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d'))
    new_figure = go.Figure(
                    data=[go.Scatter(
                        x=[data.index[i].strftime('%Y-%m-%d') for i in range(len(data)-1,len(data)-days-1,-1)],
                        y=[data['Adj Close'][i] for i in range(len(data)-1,len(data)-days-1,-1)],
                        mode='lines+markers'
                    )],
        layout=go.Layout(
            title='{} Price Chart'.format(ticker),
            xaxis={'title': 'Date'},
            yaxis={'title': 'Stock Price'},
            hovermode='closest',
            plot_bgcolor= '#191919',
            paper_bgcolor= '#191919',
            font= {
                'color': '#ffffff'
            }
            )
    )

    return new_figure

## Update rating predicted by our machine learning model for the stock
@app.callback(Output('predicted-rating', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            return df[df['ticker'] == value]['predicted'].values[0]

        except:
            return 'N/A'

## Update analyst rating of stock
@app.callback(Output('analyst-rating', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            return df[df['ticker'] == value]['rating'].values[0]

        except:
            return 'N/A'

## Update the number of shares outstanding for the stock
@app.callback(Output('shares-outstanding', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            shares = int(df[df['ticker'] == value]['shares_outstanding'].values[0])

            if len(str(shares).replace('-','')) >= 13:
                shares = '{}T'.format(round(shares / 1000000000000, 2))
            elif len(str(shares).replace('-','')) >= 10:
                shares = '{}B'.format(round(shares / 1000000000, 2))
            elif len(str(shares).replace('-','')) >= 7:
                shares = '{}M'.format(round(shares / 1000000, 2))
            elif len(str(shares).replace('-','')) >= 4:
                shares = '{}K'.format(round(shares / 1000, 2))

            return shares

        except:
            return 'N/A'

## Update the GICS Sector code for stock
@app.callback(Output('sector', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            return df[df['ticker'] == value]['sector'].values[0]
        except:
            return 'N/A'

## Update Total Asset value for stock
@app.callback(Output('assets', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            assets = int(df[df['ticker'] == value]['total_assets'].values[0])

            if len(str(assets).replace('-','')) >= 13:
                assets = '{}T'.format(round(assets / 1000000000000, 2))
            elif len(str(assets).replace('-','')) >= 10:
                assets = '{}B'.format(round(assets / 1000000000, 2))
            elif len(str(assets).replace('-','')) >= 7:
                assets = '{}M'.format(round(assets / 1000000, 2))
            elif len(str(assets).replace('-','')) >= 4:
                assets = '{}K'.format(round(assets / 1000, 2))

            return assets

        except:
            return 'N/A'

## Update Shareholders Equity value for stock
@app.callback(Output('equity', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            shareholders_equity = int(df[df['ticker'] == value]['shareholders_equity'].values[0])

            if len(str(shareholders_equity).replace('-','')) >= 13:
                shareholders_equity = '{}T'.format(round(shareholders_equity / 1000000000000, 2))
            elif len(str(shareholders_equity).replace('-','')) >= 10:
                shareholders_equity = '{}B'.format(round(shareholders_equity / 1000000000, 2))
            elif len(str(shareholders_equity).replace('-','')) >= 7:
                shareholders_equity = '{}M'.format(round(shareholders_equity / 1000000, 2))
            elif len(str(shareholders_equity).replace('-','')) >= 4:
                shareholders_equity = '{}K'.format(round(shareholders_equity / 1000, 2))

            return shareholders_equity

        except:
            return 'N/A'

## Update Total liabilities value for stock
@app.callback(Output('liabilities', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            total_liabilities = int(df[df['ticker'] == value]['total_liabilities'].values[0])

            if len(str(total_liabilities).replace('-','')) >= 13:
                total_liabilities = '{}T'.format(round(total_liabilities / 1000000000000, 2))
            elif len(str(total_liabilities).replace('-','')) >= 10:
                total_liabilities = '{}B'.format(round(total_liabilities / 1000000000, 2))
            elif len(str(total_liabilities).replace('-','')) >= 7:
                total_liabilities = '{}M'.format(round(total_liabilities / 1000000, 2))
            elif len(str(total_liabilities).replace('-','')) >= 4:
                total_liabilities = '{}K'.format(round(total_liabilities / 1000, 2))

            return total_liabilities

        except:
            return 'N/A'

## Update last trade price of stock from yahoo finance
@app.callback(Output('trade-price', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            data = web.DataReader(value.replace('.', '-'), 'yahoo', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d'))

            return '{} as of {}'.format(round(data['Adj Close'][len(data)-1], 2), datetime.datetime.now().strftime('%m-%d-%Y'))
        except:
            return 'N/A'

## Calculate and Update Market-capitalization value for stock. Trade Price multiplied by the amount of shares outstanding
@app.callback(Output('market-cap', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            shares = df[df['ticker'] == value]['shares_outstanding'].values[0]

            data = web.DataReader(value.replace('.', '-'), 'yahoo', (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d'))
            marketcap = int(data['Adj Close'][len(data)-1] * shares)

            if len(str(marketcap)) >= 13:
                marketcap = '{}T'.format(round(marketcap / 1000000000000, 2))
            elif len(str(marketcap)) >= 10:
                marketcap = '{}B'.format(round(marketcap / 1000000000, 2))
            elif len(str(marketcap)) >= 7:
                marketcap = '{}M'.format(round(marketcap / 1000000, 2))
            elif len(str(marketcap)) >= 4:
                marketcap = '{}K'.format(round(marketcap / 1000, 2))

            return marketcap

        except:
            return 'N/A'

## Update the Quarter-Ending date of latest report. Gross, Operating, Net, Earnings, Book, Assets, Liabilities, and Equity values are all from the Quarter-End results
@app.callback(Output('quarter-end', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:

            if type(df[df['ticker'] == value]['quarter_end'].values[0]) == str and df[df['ticker'] == value]['quarter_end'].values[0] != 'NaN':
                date = df[df['ticker'] == value]['quarter_end'].values[0]
            else:
                date = 'N/A'

            return date

        except:
            return 'N/A'

## Calculate and Update the Earnings per Share of stock
@app.callback(Output('eps', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):
    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:

            if math.isnan(df[df['ticker'] == value]['net_income'].values[0] / df[df['ticker'] == value]['shares_outstanding'].values[0]) or math.isinf(df[df['ticker'] == value]['net_income'].values[0] / df[df['ticker'] == value]['shares_outstanding'].values[0]):
                return 'N/A'

            else:
                return round(df[df['ticker'] == value]['net_income'].values[0] / df[df['ticker'] == value]['shares_outstanding'].values[0], 2)

        except:
            return 'N/A'

## Calculate and Update the Tangible Book Value per Share of stock
@app.callback(Output('bvs', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            if math.isnan((df[df['ticker'] == value]['total_assets'].values[0] - df[df['ticker'] == value]['total_liabilities'].values[0] - df[df['ticker'] == value]['intangible_assets'].values[0]) / df[df['ticker'] == value]['shares_outstanding'].values[0]):
                bvs = 'N/A'
            else:
                bvs = round((df[df['ticker'] == value]['total_assets'].values[0] - df[df['ticker'] == value]['total_liabilities'].values[0] - df[df['ticker'] == value]['intangible_assets'].values[0]) / df[df['ticker'] == value]['shares_outstanding'].values[0], 2)

            return bvs

        except:
            return 'N/A'

## Calculate and Update Year-over-year Growth in Annual Revenues of stock
@app.callback(Output('revenue-growth', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            if (df[df['ticker'] == value]['revenue_ly'].values[0] == 0 or math.isnan(df[df['ticker'] == value]['revenue_ly'].values[0])) or math.isnan(df[df['ticker'] == value]['revenue_a'].values[0]):
                yoy = 'N/A'
            else:
                yoy = round((df[df['ticker'] == value]['revenue_a'].values[0] - df[df['ticker'] == value]['revenue_ly'].values[0]) / (df[df['ticker'] == value]['revenue_ly'].values[0]) * 100, 2)
            if type(df[df['ticker'] == value]['last_year'].values[0]) == str or type(df[df['ticker'] == value]['year'].values[0]) == str:
                last = df[df['ticker'] == value]['last_year'].values[0][:4]
                year = df[df['ticker'] == value]['year'].values[0][:4]
            else:
                last = 'N/A'
                year = 'N/A'
            return '{}% from {} to {}'.format(yoy, last, year)

        except:
            return 'N/A'

## Calculate and Update Gross Profit and Gross Margin values of stock
@app.callback(Output('gross', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            if math.isnan(df[df['ticker'] == value]['gross_profit'].values[0]):
                gross = 'N/A'
            else:
                gross = int(df[df['ticker'] == value]['gross_profit'].values[0])

            if len(str(gross).replace('-','')) >= 13:
                gross = '{}T'.format(round(gross / 1000000000000, 2))
            elif len(str(gross).replace('-','')) >= 10:
                gross = '{}B'.format(round(gross / 1000000000, 2))
            elif len(str(gross).replace('-','')) >= 7:
                gross = '{}M'.format(round(gross / 1000000, 2))
            elif len(str(gross).replace('-','')) >= 4:
                gross = '{}K'.format(round(gross / 1000, 2))

            if df[df['ticker'] == value]['revenue_q'].values[0] == 0 or math.isnan(df[df['ticker'] == value]['gross_profit'].values[0]):
                margin = 'N/A'
            else:
                margin = round(df[df['ticker'] == value]['gross_profit'].values[0]/df[df['ticker'] == value]['revenue_q'].values[0], 2)

            return '{} / {}'.format(gross, margin)

        except:
            return 'N/A'

## Calculate and Update Operating Profit and Operating Margin values of stock
@app.callback(Output('operating', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:

            if math.isnan(df[df['ticker'] == value]['operating_profit'].values[0]):
                operating = 'N/A'
            else:
                operating = int(df[df['ticker'] == value]['operating_profit'].values[0])

            if len(str(operating).replace('-','')) >= 13:
                operating = '{}T'.format(round(operating / 1000000000000, 2))
            elif len(str(operating).replace('-','')) >= 10:
                operating = '{}B'.format(round(operating / 1000000000, 2))
            elif len(str(operating).replace('-','')) >= 7:
                operating = '{}M'.format(round(operating / 1000000, 2))
            elif len(str(operating).replace('-','')) >= 4:
                operating = '{}K'.format(round(operating / 1000, 2))

            if df[df['ticker'] == value]['revenue_q'].values[0] == 0 or math.isnan(df[df['ticker'] == value]['operating_profit'].values[0]):
                margin = 'N/A'
            else:
                margin = round(df[df['ticker'] == value]['operating_profit'].values[0]/df[df['ticker'] == value]['revenue_q'].values[0], 2)

            return '{} / {}'.format(operating, margin)

        except:
            return 'N/A'

## Calculate and Update Net Income and Net Margin values of stock
@app.callback(Output('net', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:

            if math.isnan(df[df['ticker'] == value]['net_income'].values[0]):
                net = 'N/A'
            else:
                net = int(df[df['ticker'] == value]['net_income'].values[0])

            if len(str(net).replace('-','')) >= 13:
                net = '{}T'.format(round(net / 1000000000000, 2))
            elif len(str(net).replace('-','')) >= 10:
                net = '{}B'.format(round(net / 1000000000, 2))
            elif len(str(net).replace('-','')) >= 7:
                net = '{}M'.format(round(net / 1000000, 2))
            elif len(str(net).replace('-','')) >= 4:
                net = '{}K'.format(round(net / 1000, 2))

            if df[df['ticker'] == value]['revenue_q'].values[0] == 0 or math.isnan(df[df['ticker'] == value]['net_income'].values[0]):
                margin = 'N/A'
            else:
                margin = round(df[df['ticker'] == value]['net_income'].values[0]/df[df['ticker'] == value]['revenue_q'].values[0], 2)

            return '{} / {}'.format(net, margin)

        except:
            return 'N/A'

## Calculate and update the Return on Equity value of the stock
@app.callback(Output('roe', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            net = df[df['ticker'] == value]['net_income'].values[0]
            equity = df[df['ticker'] == value]['shareholders_equity'].values[0]

            if math.isnan(net/equity) or math.isinf(net/equity):
                return 'N/A'

            else:
                return round(net/equity, 2)

        except:
            return 'N/A'

## Calculate and update the Return on Asset value of the stock
@app.callback(Output('roa', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            net = df[df['ticker'] == value]['net_income'].values[0]
            assets = df[df['ticker'] == value]['total_assets'].values[0]

            if math.isnan(net/assets) or math.isinf(net/assets):
                return 'N/A'

            else:
                return round(net/assets, 2)

        except:
            return 'N/A'

## Calculate and update the Debt-to-Equity ratio of the stock
@app.callback(Output('debt-equity', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:

            debt = df[df['ticker'] == value]['total_liabilities'].values[0]
            equity = df[df['ticker'] == value]['shareholders_equity'].values[0]

            if math.isnan(debt) or math.isnan(equity):
                return 'N/A'
            else:
                return round(debt/equity, 2)

        except:
            return 'N/A'

## Calculate and update the Debt-to-Asset ratio of the stock
@app.callback(Output('debt-asset', 'children'), [Input('stock-search-bar', 'value')])
def update_output(value):

    if value is None:
        raise dash.exceptions.PreventUpdate

    else:
        try:
            debt = df[df['ticker'] == value]['total_liabilities'].values[0]
            asset = df[df['ticker'] == value]['total_assets'].values[0]

            if math.isnan(debt) or math.isnan(asset):
                return 'N/A'
            else:
                return round(debt/asset, 2)

        except:
            return 'N/A'

if __name__ == '__main__':

    app.run_server()
