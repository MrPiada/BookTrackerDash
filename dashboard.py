from datetime import datetime, timedelta
import pandas as pd
from openpyxl import load_workbook
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import dash
from dash import dcc
from dash import html

import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

pio.templates.default = "gridon"

file_excel = "data/Books.xlsx"
df = pd.read_excel(file_excel, sheet_name="Shelf")
df = df.drop('Cover', axis=1)


status_colors = ['green', 'yellow', 'blue', 'red']
status_counts = df['Status'].value_counts()
status_piechart = go.Figure(data=[go.Pie(labels=status_counts.index,
                                         values=status_counts.values)])
status_piechart.update_traces(
    hoverinfo='label+percent',
    textinfo='value',
    textfont_size=30,
    marker=dict(
        colors=status_colors,
        line=dict(
            color='#000000',
             width=2)))



df_copy = df.copy()
today = datetime.today().date()
df_copy['End'].fillna(today, inplace=True)
reading_gantt = px.timeline(df_copy[df_copy['Start'].notna()],
                            x_start='Start',
                            x_end='End',
                            y='Title',
                            color='Category',
                            hover_data=['Author',
                                        'Type',
                                        'Sub-Category',
                                        'Language',
                                        'Status'])
reading_gantt.update_yaxes(categoryorder="total ascending")
reading_gantt.update_layout(
    xaxis_title="",
    yaxis_title="",
    title="",
    showlegend=True,
    margin=dict(l=250)
)
# Modifica la larghezza delle barre
reading_gantt.update_traces(marker=dict(line=dict(width=2)))


color_discrete_map = {category: px.colors.qualitative.Plotly[i % len(
    px.colors.qualitative.Plotly)] for i, category in enumerate(df['Category'].unique())}
categories_treemap = px.treemap(df,
                                # Utilizza 'Category' come macro-categoria e
                                # 'Sub-Category' come sotto-categoria
                                path=['Category', 'Sub-Category', 'Title'],
                                values='Evaluation',  # Valori da rappresentare nel treemap
                                color='Category',  # Colore basato sulla colonna 'Status'
                                color_discrete_map=color_discrete_map,
                                maxdepth=2,
                                title='')  # Titolo del grafico
categories_treemap.update_traces(marker=dict(cornerradius=5))


read = df[df['Status'] == 'Read']
evaluations_treemap = px.treemap(read,
                                 # Utilizza solo 'Category' e 'Sub-Category'
                                 # come livelli
                                 path=['Category', 'Sub-Category', 'Title'],
                                 values='Evaluation',  # Valori da rappresentare nel treemap
                                 color='Evaluation',  # Colore basato sulla media di 'Evaluation'
                                 color_continuous_scale=[
                                     [0, 'red'], [0.5, 'white'], [1, 'green']],
                                 maxdepth=3,
                                 title=''
                                 )
evaluations_treemap.update_traces(marker=dict(cornerradius=5))
evaluations_treemap.update_traces(marker=dict(line=dict(width=0)))


# Crea un'applicazione Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.SKETCHY],
    title='Book tracker')

app.layout = html.Div([
    dbc.Tabs([
        dcc.Tab(label='Overview',
                children=[
                    html.Div([
                        dcc.Graph(id='status_piechart',
                                  figure=status_piechart,
                                  style={'height': 650}),
                    ])
                ]),
        dcc.Tab(label='Roadmap',
                children=[
                    html.Div([
                        dcc.Graph(id='reading_gantt',
                                  figure=reading_gantt,
                                  style={'height': 650}),
                    ])
                ]),
        dcc.Tab(label='Shelf',
                children=[
                    dcc.Graph(id='categories_treemap',
                              figure=categories_treemap,
                              style={'height': 650}),
                ]),
        dcc.Tab(label='Evaluations',
                children=[
                    dcc.Graph(id='evaluations_treemap',
                              figure=evaluations_treemap,
                              style={'height': 650}),
                ]),
    ])
])


# Esegui l'applicazione Dash
if __name__ == '__main__':
    app.run_server(debug=True)
