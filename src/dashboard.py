import pandas as pd
import numpy as np
import geopandas as gpd
import shapely.geometry
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

df = pd.read_pickle('../data/quakes_last_24.pkl')
geo_df = gpd.read_file('../data/GeoJSON/PB2002_boundaries.json')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Worldwide Earthquakes over the Last 24 Hours', style={'textAlign': 'center'}),
    html.Div([
        html.H2('World View', style={'textAlign': 'center'}),
        dcc.Graph(id='map', style={'height': '700px', 'padding': '2px'}),
        html.Div(dcc.RangeSlider(
            id='mag-slider',
            min=2.5,
            max=9.0,
            step=0.1,
            value=[2.5, 9.0],
            marks={i: {'label': str(i), 'style': {'transform': 'rotate(0deg)', 'font-size': '20px'}}
                        for i in range(3, 10)},
            included=False
        ), style={'width': '100%', 'margin': 'auto', 'padding': '2px'}),  
        html.Div([
            dcc.RadioItems(
                id='tsunami-filter',
                options=[{'label': 'All', 'value': 'all'},
                         {'label': 'Tsunami Warning Issued', 'value': 'yes'},
                         {'label': 'No Tsunami Warning', 'value': 'no'}],
                value='all',
                inline=True
            ),
            dcc.RadioItems(
                id='boundary-toggle',
                options=[{'label': 'Show Boundary', 'value': 'show'},
                         {'label': 'Hide Boundary', 'value': 'hide'}],
                value='show',
                inline=True
            )
        ], style={'padding': '2px'})
    ], style={'width': '66%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '2px'}),


    html.Div([
        html.H2('Details', style={'textAlign': 'center'}),
        dcc.RadioItems(
            id='sort-by',
            options=[{'label': 'Sort by Magnitude', 'value': 'mag'},
                     {'label': 'Sort by Time', 'value': 'datetime'}],
            value='datetime',
            inline=True
        ),
        dcc.RadioItems(
            id='sort-order',
            options=[{'label': 'Ascending', 'value': 'asc'},
                     {'label': 'Descending', 'value': 'desc'}],
            value='desc',
            inline=True
        ),
        html.Div(id='quake-details', style={'overflow': 'auto', 'height': '670px', 'padding':'10px'})
    ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '2px'})
], style={'backgroundColor': '#FAFAFA'})


@app.callback(
    Output('map', 'figure'),
    [Input('mag-slider', 'value'),
     Input('tsunami-filter', 'value'),
     Input('boundary-toggle', 'value')])
def update_map(mag_range, tsunami, boundary):
    filtered_df = df[(df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1])]
    if tsunami != 'all':
        filtered_df = filtered_df[filtered_df['tsunami warning'] == (1 if tsunami == 'yes' else 0)]
    
    fig = px.scatter_geo(filtered_df,
        lat = 'latitude',
        lon = 'longitude',
        size = 'mag',
        color = 'tsunami warning',
        opacity = .3,
        color_discrete_sequence = ['orange', 'blue'],
        hover_name = 'place',
        projection = 'natural earth')

    if boundary == 'show':
        lats = []
        lons = []
        names = []

        for feature, name in zip(geo_df.geometry, geo_df.LAYER):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name]*len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)

        fig.add_trace(go.Scattergeo(lat=lats, lon=lons, mode='lines', line=dict(width=1, color='black')))

    return fig

@app.callback(
    Output('quake-details', 'children'),
    [Input('sort-by', 'value'),
     Input('sort-order', 'value')])
def update_quake_details(sort_by, sort_order):
    sorted_df = df.sort_values(sort_by, ascending=(sort_order == 'asc'))
    return html.Ul([html.Li(f"{row['place']}, {row['datetime']}, {row['mag']}") for _, row in sorted_df.iterrows()])


if __name__ == '__main__':
    app.run_server(port=8010, debug=True)
