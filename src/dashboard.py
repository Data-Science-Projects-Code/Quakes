import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

df = pd.read_pickle('../data/quakes_last_24.pkl')
app = dash.Dash(__name__)

# Add external stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Earthquakes last 24 hours', style={'textAlign': 'center'}),  # Add a title
    dcc.Graph(id='map', style={'height': '700px'}), 
    html.Div(dcc.RangeSlider(
        id='mag-slider',
        min=2.5,
        max=9.0,
        step=0.1,
        value=[2.5, 9.0],
        marks={i: {'label': str(i), 'style': {'transform': 'rotate(45deg)'}}
                    for i in range(3, 10)}
    ), style={'width': '80%', 'margin': 'auto'}),  # Make the slider the length of the map
    dcc.RadioItems(
        id='tsunami-filter',
        options=[{'label': 'All', 'value': 'all'},
                 {'label': 'Tsunami Warning Issued', 'value': 'yes'},
                 {'label': 'No Tsunami Warning', 'value': 'no'}],
        value='all',
    )
], style={'backgroundColor': '#FAFAFA'})  # Change the background color

@app.callback(
    Output('map', 'figure'),
    [Input('mag-slider', 'value'),
     Input('tsunami-filter', 'value')])

def update_map(mag_range, tsunami):
    filtered_df = df[(df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1])]
    
    if tsunami != 'all':
        filtered_df = filtered_df[filtered_df['tsunami'] == (1 if tsunami == 'yes' else 0)]
    
    fig = px.scatter_geo(filtered_df,
        lat = 'latitude',
        lon = 'longitude',
        size = 'mag',
        color = 'tsunami',
        opacity = .3,
        #width = ['orange', 'blue'],
        hover_name = 'place',
        projection = 'natural earth')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

