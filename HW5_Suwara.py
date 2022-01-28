# data manipulation
from dash.html.Figure import Figure
import pandas as pd

# plotly 
import plotly.graph_objects as go

# dashboards
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#Prepare Data
population = pd.read_csv('population.csv')
StatesCodes = pd.read_csv('statecodes.csv')
pop_with_code = population.merge(StatesCodes,how = 'left', left_on = 'state', right_on = 'State').drop('State',axis = 1)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

# app.layout = html.Div([
#     html.Div([html.H1('Population of the US States over the Years')])
#     ,html.Div([dcc.Graph(id = 'pop_graph')])
#     ,html.Div([dcc.Slider(
#          id = 'year_slider'
#         ,min= 1960
#         ,max= 2012
#         ,step= 5
#         ,marks = {i: {'label':str(i), 'style': {'font-size': 15}} for i in range(1960,2011,5)}
#         ,value = 2010
#         )
#     ])
#         ])

app.layout = html.Div([
    html.H1('Population of the US States over the Years')
    ,dcc.Graph(id = 'pop_graph', style={'height':'60vh'})
    ,dcc.Slider(
         id = 'year_slider'
        ,min= 1960
        ,max= 2012
        ,step= 5
        ,marks = {i: {'label':str(i), 'style': {'font-size': 15}} for i in range(1960,2011,5)}
        ,value = 2010
        )
        ])

@app.callback(
    Output('pop_graph', 'figure'),
    Input('year_slider', 'value')
)
def update_graph(value):
    fig = go.Figure(data=go.Choropleth(
                     locations = pop_with_code[pop_with_code['Year'] == value]['Code']
                    ,locationmode= "USA-states"
                    ,z = pop_with_code[pop_with_code['Year'] == value]['Population']
                    ,colorscale = 'Reds'
                    ,colorbar_title = 'Population'
                    )
                )
    fig.update_layout(
                    geo_scope='usa'
                  )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)