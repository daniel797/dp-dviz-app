

# main.py
# =============================================================================
# common
import os
import json
from typing import List
# requirements
from dotenv import load_dotenv
import requests
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
# -----------------------------------------------------------------------------

load_dotenv('./.env')

def country_info_dframe(country_name: str, year: str) -> pd.DataFrame:
    host = os.environ['HOST_API']
    url = f'{host}/countries/{country_name}/years/{year}'
    headers = {'Content-type': 'application/json'}
    
    print(f'[INFO] url: {url}')
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    return pd.DataFrame(data)

def fig_dashboard_plots(df: pd.DataFrame) -> tuple:
    df['ma'] = df['last'].rolling(2).mean()
    
    fig_ts = px.line(df, x='month', y=['last', 'open', 'max', 'min'])
    fig_bv = px.bar(df, x='var', color='var')
    fig_cp = go.Figure(data=[
        go.Candlestick(x=df['month'], open=df['open'], high=df['max'], low=df['min'], close=df['last'], showlegend=False),
        go.Scatter(
            x=df['month'], y=df['ma'], showlegend=False,
            line={'color': 'blue', 'width': 1},
            marker={'size': 0}
        )
    ])
    fig_cp.update_layout(xaxis_rangeslider_visible=False)
    return fig_ts, fig_bv, fig_cp

# => app dashboard
app = Dash(__name__)
server = app.server

df = country_info_dframe(def_country := 'colombia', def_year := 2018)
fig_ts, fig_bv, fig_cp = fig_dashboard_plots(df)

squared_style = {'width': '50%', 'display': 'inline-block'}
country_options = [
    {'label': 'Perú', 'value': 'peru'},
    {'label': 'México', 'value': 'mexico'},
    {'label': 'Argentina', 'value': 'argentina'},
    {'label': 'Chile', 'value': 'chile'},
    {'label': 'Colombia', 'value': 'colombia'}
]
year_options = [2018, 2019, 2020, 2021]

app.layout = html.Div(children=[
    html.H1(dcc.Dropdown(
        options=country_options,
        value=def_country, 
        id='country-list'
    )),
    html.H1(dcc.Dropdown(
        options=year_options,
        value=def_year,
        id='year-list'
    )),
    html.Div(id='description', children=''),
    html.Button('Submit', id='submit-button', n_clicks=0),
    dcc.Graph(id='candleplot', figure=fig_cp),
    dcc.Graph(id='timeseries', figure=fig_ts, style=squared_style),
    dcc.Graph(id='barvertical', figure=fig_ts, style=squared_style)
])

@app.callback(
    Output('description', 'children'),
    Input('submit-button', 'n_clicks'),
    State('country-list', 'value'),
    State('year-list', 'value')
)
def update_output_descrip(n_clicks, cvalue: str, yvalue: str):
    return f'Tipo de cambio mensual. Serie de tiempo para {cvalue.capitalize()} el {yvalue}.'

@app.callback(
    Output('timeseries', 'figure'),
    Output('barvertical', 'figure'),
    Output('candleplot', 'figure'),
    Input('submit-button', 'n_clicks'),
    State('country-list', 'value'),
    State('year-list', 'value')
)
def update_output_plots(n_clicks, cvalue: str, yvalue: str):
    df = country_info_dframe(cvalue, yvalue)
    fig_ts, fig_bv, fig_cp = fig_dashboard_plots(df)
    return fig_ts, fig_bv, fig_cp

if __name__ == '__main__':
    app.run_server(debug=True)
