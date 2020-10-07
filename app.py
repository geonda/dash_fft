import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

from scipy.signal import find_peaks
from pyorbital.orbital import Orbital

import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import datetime
import plotly


plotly_template = pio.templates["plotly_dark"]
pio.templates.default = "plotly_dark"


satellite = Orbital('TERRA')

app = dash.Dash(__name__, external_stylesheets=[
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "/assets/style.css",dbc.themes.DARKLY
])


app.layout = html.Div(
    html.Div([
        html.H1("watch Terra satellite",
        style={"margin-left": "10px",
                "margin-top": "40px",
                "margin-bottom": "40px"}),

        dcc.Graph(id='live-update-graph'),

        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        ),
        html.Div(id='live-update-text',
                style={"margin-left": "10px",
                        "margin-top": "40px"}),
        html.Div(id='live-update-text-2',
                style={"margin-left": "10px",
                        "margin-top": "20px"}),
    ])
)

server = app.server

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    lon, lat, alt = satellite.get_lonlatalt(datetime.datetime.now())
    style = {'padding': '5px', 'fontSize': '25px'}
    return [
        html.Span('Longitude: {0:.2f}'.format(lon), style=style),
        html.Span('Latitude: {0:.2f}'.format(lat), style=style),
        html.Span('Altitude: {0:0.2f}'.format(alt), style=style)
    ]

@app.callback([Output('live-update-graph', 'figure'),Output('live-update-text-2', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    satellite = Orbital('TERRA')
    data = {
        'time': [],
        'Latitude': [],
        'Longitude': [],
        'Altitude': []
    }

    # Collect some data
    for i in range(360):
        time = datetime.datetime.now() - datetime.timedelta(seconds=i*100)
        lon, lat, alt = satellite.get_lonlatalt(
            time
        )
        data['Longitude'].append(lon)
        data['Latitude'].append(lat)
        data['Altitude'].append(alt)
        data['time'].append(time)

    # Create the graph with subplots
    fig = make_subplots(rows=1, cols=2, column_widths=[0.7, 0.3])
    fig['layout']['margin'] = {
        'l': 10, 'r': 10, 'b': 10, 't': 10
    }
    fig['layout']['legend'] = {'x': 1, 'y': 1, 'xanchor': 'right'}

    fig.append_trace({
        'x': data['time'],
        'y': data['Altitude'],
        'name': 'Altitude',
        'mode': 'lines+markers',
        'type': 'scatter'

    }, 1, 1)
    fig.update_xaxes(title_text="time, hh:mm:ss", row=1, col=1)
    fig.update_yaxes(title_text="Altitude, m? ",  row=1, col=1)


    fftfreq = np.fft.fftfreq(np.linspace(0,360*100,360).shape[-1])
    fft = abs(np.imag(np.fft.fft(np.array(data['Altitude']))))
    min =  0
    max = int(len(fftfreq)/2)

    fig.append_trace({
        'x': fftfreq[min:max] ,
        'y': fft[min:max],
        'text': data['time'],
        'name': 'FFT(Altitude)',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 2)
    fig.update_xaxes(title_text="frequency, ?", range=[0, 0.1], row=1, col=2)
    fig.update_yaxes(title_text="FFT(Altitude)", row=1, col=2)

    peaks, _ = find_peaks(fft[min:max], height=200)
    style = {'padding': '5px', 'fontSize': '25px'}

    f1,f2=fftfreq[peaks]

    return fig,[html.Span('First Frequency: {0:.2f}'.format(f1), style=style),
        html.Span('Second Frequency: {0:.2f}'.format(f2), style=style)]



if __name__ == "__main__":
    app.run_server(debug=True)
