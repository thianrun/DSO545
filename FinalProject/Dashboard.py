

# data manipulation
import pandas as pd
import ast
import numpy as np

# plotly 
import plotly.express as px
import plotly.graph_objects as go 

# dashboards
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import date
import datetime

# app = JupyterDash(__name__, external_stylesheets = [dbc.themes.CYBORG])
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.CYBORG])


# Import data
ted_talk = pd.read_csv('ted_main.csv')
ted_talk['film_date'] = pd.to_datetime(ted_talk['film_date'],unit = 's')
ted_talk['published_date'] = pd.to_datetime(ted_talk['film_date'],unit = 's')

# Exclude data that film date before year 2002 and the film date do not aligned with event name
ted_talk = ted_talk[ted_talk['film_date'].dt.year >= 2002].reset_index(drop = True)
ted_talk = ted_talk[~((ted_talk['event'] == 'TEDSalon NY2011') & (ted_talk['film_date'] == '2010-11-18'))].reset_index(drop = True)

# Create new variables for the table
ted_talk["interaction"] = round((ted_talk["comments"] / ted_talk["views"]) * 100, 2)
ted_talk["ratings_list"] = ted_talk["ratings"].apply(lambda x:ast.literal_eval(x))

# function to get the total number of rating for each talk
def get_total(x):
    count=0
    for i in x:
        count+=i["count"]
    return count

# Table / DataFrame
ted_talk['total_num_rating'] = ted_talk['ratings_list'].apply(lambda x: get_total(x))
ted_talk['year'] = ted_talk['film_date'].dt.year
year_list = np.append(['All'],ted_talk['year'].sort_values().unique())
# year_list = ted_talk['year'].sort_values().unique()
interaction_df = ted_talk.sort_values("interaction", ascending = False)[["name","interaction","main_speaker","views"]][ted_talk.views > ted_talk.views.mean()].nlargest(10, "interaction").sort_values("interaction", ascending=False)
interaction_year = ted_talk.groupby('year')['interaction'].mean().reset_index()


#############################################

max_occupation=pd.DataFrame(ted_talk["speaker_occupation"].value_counts().sort_values(ascending=False).nlargest(8))
max_occupation = max_occupation.reset_index()
max_occupation.rename(columns={'index':'Speaker Occupation','speaker_occupation':'Count'},inplace=True)

# get the list inside the string dtype as a list
def get_funny_ratings(x):
    for i in x:
        if i["name"]=="Funny":
            return i["count"]
ted_talk["funny_ratings"]=ted_talk["ratings_list"].apply(lambda x: get_funny_ratings(x))
ted_talk["funny_ratio"]=round((ted_talk["funny_ratings"]/ted_talk["total_num_rating"])*100,2)
funny=ted_talk[(ted_talk.total_num_rating>ted_talk.total_num_rating.mean())]\
.nlargest(10,"funny_ratio").sort_values("funny_ratio",ascending=True)
def confuse(x):
    for i in x:
        if i["name"]=="Confusing":
            return i["count"]
# make a column with the ratio of confusing rating to the total ratings number
ted_talk["confuse_ratio"]=round((ted_talk["ratings_list"].apply(lambda x: confuse(x))/ ted_talk["total_num_rating"])*100,2)
confuse_ratio=ted_talk[(ted_talk.total_num_rating>ted_talk.total_num_rating.mean())]\
.nlargest(8,"confuse_ratio").sort_values("confuse_ratio",ascending=True)

top_occupations = list(max_occupation['Speaker Occupation'])
top_8_occupations = ted_talk[ted_talk['speaker_occupation'].isin(top_occupations)]
Analysis_by_rating_name = pd.read_csv('Analysis_by_rating_name.csv')
Analysis_by_rating_name.set_index('speaker_occupation', inplace=True)

df_top30 = ted_talk[['title','views','ratings', 'tags']].sort_values('views', ascending = False).head(30)
df_top30["tags"] = df_top30["tags"].apply(lambda x: ast.literal_eval(x))
tags = df_top30["tags"].explode().value_counts().head(10)
# display(df_top30["tags"].explode().value_counts(normalize=True).head(10))

ted_talk['duration_hr']=ted_talk['duration']/(60*60)
ted_talk['duration_hr']=ted_talk['duration_hr'].astype(float)
ted_talk['duration_hr']=ted_talk['duration_hr'].round(decimals=2)

def get_top10(feature):
    popular_talks = ted_talk[['title', 'main_speaker', 'views','comments','film_date', 'published_date','duration','duration_hr', 'tags']].sort_values(by=feature,ascending=False).set_index(feature).reset_index().head(10)
    return popular_talks

df_view = pd.DataFrame(ted_talk.groupby(['duration_hr']).agg('views').mean()).reset_index()
# print(df)
#ratings
df_top30_views = ted_talk[['title','views','ratings']].sort_values('views', ascending = False).head(30)
import ast
df_top30_views["ratings"] = df_top30_views["ratings"].apply(lambda x: ast.literal_eval(x))

ratings_list = []
for x in df_top30_views["ratings"]:
    d = (pd.json_normalize(x)
    .drop(columns="id")
    .set_index(keys="name")
     .T)
    ratings_list.append(d)

ratings_df = pd.concat(ratings_list)
ratings_df.reset_index(drop=True, inplace=True)
ratings = pd.DataFrame(ratings_df.sum()).reset_index()
#ratings.transpose()
ratings = ratings.rename(columns={'name': 'name', 0: 'views'})
ratings = ratings.sort_values("views").head(8)

#events
ted = ted_talk['event']
ted_talk['TED or TEDx'] = ted.str.startswith('TED20')*1
ted_talk['TED'] = ['Official TED' if i ==1 else 'TEDx' for i in ted_talk['TED or TEDx']]
Tedx = ted_talk.groupby('TED').agg('views').mean()

###########################################################
# Card Description
c_total_talk = ted_talk['event'].nunique()
c_text1 = 'talks over '+str(ted_talk['year'].nunique())+' years'
c_med_views = round(ted_talk['views'].median())
c_text2 = 'views per talk (median)'
c_med_comments = round(ted_talk['total_num_rating'].median())
c_text3 = 'comments per talk (median)'

############
fig_top8occ = px.bar(max_occupation, x= 'Count', y='Speaker Occupation',
             title="Highest 8 Occupations with Number of Talks",
             color_discrete_sequence = ['red']*len(max_occupation),
             template='plotly_dark')
############
fig_funny =px.bar(funny,x="main_speaker",y="funny_ratio",color="speaker_occupation",
          title="Highest 10 Ted Talks with Funny_ratings Ratio and their Occupations",
           color_discrete_sequence = px.colors.sequential.Reds,
          template='plotly_dark' ,
           hover_data={"name":True},
           labels={"name":"Talk_name "},
           text="funny_ratio"
          )

############
fig_confusing =px.bar(confuse_ratio,x="main_speaker",y="confuse_ratio",color="speaker_occupation",
          title="Highest 8 Ted Talks with Confuse_ratio Ratings > 6 & their Occupations",
          labels={"name":"tedtalk name"},
          text="confuse_ratio",
          #colorscale='Reds',
          color_discrete_sequence = px.colors.sequential.Reds,
          template='plotly_dark'
          )

############
# df_occ = px.data.tips()
fig_regression = px.scatter(top_8_occupations, x="total_num_rating", y="views", trendline="ols", color ='speaker_occupation',color_discrete_sequence=px.colors.sequential.Reds_r, template ='plotly_dark')
fig_regression.update_layout(
    title="Regression Plot of Views vs. Ratings for Top 8 Occupations",
    xaxis_title="Total Ratings",
    yaxis_title="Views",
    legend_title="Top Occupations(By Count)"
    )
############

fig_heatmap = px.imshow(Analysis_by_rating_name
,title="Heatmap for Top 15 Occupations vs Count of Ratings/Tags"
,color_continuous_scale='Reds'
,template ='plotly_dark'
)
###########################################################################################

#Line chart for Engagement Tab
title_line_en = 'Interaction over years'
fig_line_engagement = px.line(interaction_year, x = 'year', y= 'interaction',
       title= title_line_en,
       height = 300
      )
fig_line_engagement.update_layout(
    template= 'plotly_dark')
fig_line_engagement.update_traces(line_color='red')
fig_line_engagement.update_yaxes(showgrid=False,visible=True,title="Interaction")
fig_line_engagement.update_xaxes(visible=True,title="Year")

##########################################################################################

#descriptors
fig1 = px.bar(tags, x=tags.index, y=tags.values,width=600,height=400, color_discrete_sequence = ['red'], text=tags.values)
fig1.update_layout(
    title = 'Top Topics among the Highest-Viewed Talks', 
    yaxis_title = 'Topic',
    plot_bgcolor = 'black'
    )
fig1.update_yaxes(showgrid=False,visible=True)
fig1.update_layout(
    template= 'plotly_dark')

#duration
fig2 = px.line(df_view, x= "duration_hr", y='views', title='Duration of Top Viewed Talks', color_discrete_sequence = ['red'])
fig2.update_layout(
    xaxis_title = 'Talk Duration (hour)', 
    yaxis_title = 'View Count',
    plot_bgcolor = 'black'
    )
fig2.update_yaxes(showgrid=False,visible=True)
fig2.update_layout(
    template= 'plotly_dark')

#description

fig3 = px.bar(ratings, x='views', y='name', color_discrete_sequence = ['red'], text = 'views')
fig3.update_layout(
    title = 'Top Descriptions for the Highest Viewed Talks', 
    yaxis_title = 'Description'
    #plot_bgcolor = 'black'
    )
fig3.update_xaxes(showgrid=False,visible=True)
fig3.update_layout(
    template= 'plotly_dark')

#events
fig4 = px.bar(Tedx, x=Tedx.index, y='views', color_discrete_sequence = ['red'], text = 'views')
fig4.update_layout(
    title = 'Number of Views for TED versus TEDx Talks', 
    yaxis_title = 'View Count'
    #plot_bgcolor = 'black'
)
fig4.update_yaxes(showgrid=False,visible=True)
fig4.update_layout(
    template= 'plotly_dark')

# Tab Style
tab_style = {
    'backgroundColor': '#3f3f3f',
    'border-style': 'none',
    'borderTop': '1px solid #d6d6d6',  
    'font-size': '20px'
}

tab_selected_style = {
    'border-style': 'none',
    'borderTop': '4px solid #ff0000',
    'backgroundColor': 'black',
    'color': 'white',
    'fontWeight': 'bold',
    'font-size': '20px'
}

app.layout = html.Div([
    html.Div([
        html.H4(children = [html.Span('Analysis of '),html.Span('TED',style = {'color':'red', 'fontWeight':'bold'}),html.Span(' Talks Over Years')]),
        html.H6("TED is a nonprofit organization dedicated to spreading ideas in the form of short and powerful talks. This dashboard represents the analysis of TED Talks in term of engagement, views, and speaker's occupations."),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                dbc.CardBody([
                        html.H3('{:,}'.format(c_total_talk), style = {'text-align':"center"}),
                        html.P(c_text1,style = {'text-align':"center", 'margin-bottom': '0px'})
                            ]),
                    ])
                    ,width=4),
                dbc.Col(
                dbc.Card([
                dbc.CardBody([
                        html.H3('{:,}'.format(c_med_views), style = {'text-align':"center"}),
                        html.P(c_text2,style = {'text-align':"center", 'margin-bottom': '0px'})
                            ]),
                    ])
                    ,width=4),
                            dbc.Col(
                dbc.Card([
                dbc.CardBody([
                        html.H3('{:,}'.format(c_med_comments), style = {'text-align':"center"}),
                        html.P(c_text3,style = {'text-align':"center", 'margin-bottom': '0px'})
                            ]),
                    ])
                    ,width=4)
                ])
            ], style = {'margin' : '10px 20px 15px 20px'}),
    dcc.Tabs(
        ([ dcc.Tab(label = 'Engagement', children = ([
    # top left drop menu and radio items together in one division
            dbc.Row([
                dbc.Col(
                    html.Div([    
                        html.H5('Top 10 interaction from 2002 - 2017',style = {'font-size': '20px','fontWeight': 'bold'}),
                        dash_table.DataTable(
                        id='interaction-table',
                        columns=[{"name": i, "id": j} for j,i in zip(interaction_df.columns,['Talk Name', 'Interaction', 'Main Speaker','Views'])],
                        data=interaction_df.to_dict('records'),
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white',
                            'textAlign': 'center',
                            'fontWeight':'bold',
                            'font-size':'14px'
                        },
                        style_data={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white'
                        },
                        style_cell =
                            {
                                'textAlign': 'center',
                                'font-family':'sans-serif',
                                'margin': 'auto',
                                'font-size':'14px'
                            }
                        ,
                        style_cell_conditional=[
                            {
                                'if': {'column_id': c},
                                'textAlign': 'left'
                            } for c in ['name', 'main_speaker']
                        ]
                        )
                        ])
                    , width = 6),
            dbc.Col( children = [
            # top right drop menu and radio items together in one division
            html.Div([
                    dcc.Graph(id = 'interaction-line', figure = fig_line_engagement
                            ,style={'height':'300px'})   
            ]),
                    html.Label('Select Year', style = {'color': 'white'}),
                    dcc.Dropdown(
                        id='year-engagement',
                        options=[{'label': i, 'value': i} for i in year_list],
                        value= 'All',
                        clearable = False
                    )
            ]
            ,width = 6)
            ], style = {'margin-top':'15px','margin-left':'15px','margin-right':'10px'}),
            dcc.Loading(
                    children=[html.Div([dcc.Graph(id='box-comment')])],
                    type="circle",
                    color="red"
            ),
            dcc.Loading(
                    children=[html.Div([dcc.Graph(id='percent-comment')])],
                    type="circle",
                    color="red"
            ),
            dcc.Loading(
                    children=[html.Div([dcc.Graph(id='word-comment')], style = {'margin-left':'15px','margin-right':'10px'})],
                    type="circle",
                    color="red"
            )
        ])
        ,style=tab_style, selected_style = tab_selected_style
        ),
###End of Tab 1
        dcc.Tab(label = 'Views',children = [
                html.Div(children=[
                html.H5('''
                    The Highest-Viewed TED Talks
                ''', style = {'margin-left': '25px','margin-top': '15px'}),
                dbc.Row([
                        dbc.Col(dcc.Graph(
                            figure=fig1
                        )),
                        dbc.Col(
                            dcc.Graph( 
                            figure=fig4)
                        )
                ]),
                dcc.Graph(
                    figure=fig2), 
                dcc.Graph(
                    figure=fig3
                    ,style = {'margin-left': '25px'})
                    ])
            ],style=tab_style, selected_style = tab_selected_style),
###End of Tab 2
        dcc.Tab(label = 'Occupations',children = [
            dcc.Graph(figure=fig_top8occ,style = {'margin-left': '25px'}) ,
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_funny), width = 6) ,
                dbc.Col(dcc.Graph(figure=fig_confusing), width = 6)
                ]),
            dcc.Graph(figure=fig_regression),
            dcc.Graph(figure=fig_heatmap, style={
            'height': 800,
            'width': 800,
            "margin": "auto"
            })
            ],style=tab_style, selected_style = tab_selected_style)
        ])
    )
])

@app.callback(
    Output('box-comment', 'figure'),
    Output('percent-comment', 'figure'),
    Output('word-comment', 'figure'),
    Input('year-engagement', 'value')
)
def update_box_comment(year):
    if year == 'All':
        comment = ted_talk.iloc[:,:]
        title_e1 = 'Number of comments over years'
        interaction=ted_talk.sort_values("interaction", ascending = False)[["name","interaction","main_speaker","views"]]\
        [ted_talk.views > ted_talk.views.mean()].nlargest(10, "interaction").sort_values("interaction", ascending=False)
        title_e2 = 'Percent of Comments for highest 10 talks over years'
        ted_talk_year = ted_talk.iloc[:,:]
        title_e3 = "Words that are mentioned the most in each talks over years"
    else:
        comment = ted_talk[ted_talk['year'] == int(year)]['comments']
        title_e1 = 'Number of comments in ' + str(year)
        title_e2 = 'Percent of Comments for highest 10 talks in '+ str(year)
        interaction=ted_talk[ted_talk.year == int(year)].sort_values("interaction", ascending = False)[["name","interaction","main_speaker","views"]]\
        [ted_talk.views > ted_talk.views.mean()].nlargest(10, "interaction").sort_values("interaction", ascending=False)
        ted_talk_year = ted_talk[ted_talk['year'] == int(year)].reset_index(drop = True)
        title_e3 = "Words that are mentioned the most in each talks in " + str(year)

    fig_e1 = px.box(comment, x = 'comments',
        title= title_e1,
        )
    fig_e1.update_layout(
        template= 'plotly_dark')
    fig_e1.update_traces(marker_color='red')


    fig_e2 = px.bar(interaction, x = "name", y="interaction",
        title= title_e2,
        color_discrete_sequence = ['red'],
        hover_data={"name":True,"main_speaker":True},
            text="interaction",
        )
    fig_e2.update_layout(
        template= 'plotly_dark')
    fig_e2.update_yaxes(showgrid=False,visible=False,title="percent of commencts")
    fig_e2.update_xaxes(tickfont_size=9, title = "The official name of the TED Talk")
    fig_e2.update_traces(textposition="inside", textfont_size=13)
    
    
    for i in range(len(ted_talk_year)):
        if i == 0:
            rating_e = pd.DataFrame(ted_talk_year.ratings_list[i])
            rating_e['Total'] = ted_talk_year.loc[i,'total_num_rating']
        else:
            temp = pd.DataFrame(ted_talk_year.ratings_list[i])
            temp['Total'] = ted_talk_year.loc[i,'total_num_rating']
            rating_e = rating_e.append(temp)

    rating_e['ratio'] = (rating_e['count']/rating_e['Total'])*100
    best_words = rating_e.groupby('name')['ratio'].mean().round(2).sort_values(ascending = False).reset_index()

    fig_e3 = go.Figure()
    # Draw points
    fig_e3.add_trace(go.Scatter(y = best_words["name"], 
                          x = best_words["ratio"],
                          mode = 'markers',
                          marker_color ='red',
                          marker_size  = 15))
    # Draw lines
    for i in range(0, len(best_words)):
               fig_e3.add_shape(type='line',
                              x0 = 0, y0 = i,
                              x1 = best_words["ratio"][i],
                              y1 = i,
                              line=dict(color='red', width = 5))
    # Set title
    fig_e3.update_layout(template= 'plotly_dark', title_text = title_e3)
    # Set x-axes range
    fig_e3.update_xaxes(showgrid=False, title = 'Ratio in percentage')
    fig_e3.update_yaxes(showgrid=False, title = "Words", color = '#fff')

    return fig_e1, fig_e2, fig_e3


if __name__ == '__main__':
    app.run_server(debug=True)
    
# if __name__ == '__main__':
#     app.run_server(mode='inline', height= 300, width = '80%',port=3033)