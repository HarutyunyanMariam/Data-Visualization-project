import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input, State

dash.register_page(__name__, path='/top-actions', title='Top Actions', name='Top Actions')

# Load preprocessed CSVs (faster than filtering original dataset)
action_counts_df = pd.read_csv('assets/action_counts_top_15.csv')
action_time_df = pd.read_csv('assets/action_time_top_20.csv')

def make_figure_first(top_n):
    df = action_counts_df.head(top_n).copy()
    fig = px.bar(df, x='action', y='count')
    fig.update_traces(
        text=df['formatted_count'],
        textposition='outside',
        marker_color='#FF5A5F'
    )
    fig.update_layout(
        xaxis_title='<b>Action</b>',
        yaxis_title='<b>Frequency</b>',
        margin=dict(l=40, r=40, t=40, b=40),
        autosize=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
    )
    fig.update_xaxes(tickfont=dict(size=12, family='Arial', color='black'))
    fig.update_yaxes(tickfont=dict(size=12, family='Arial', color='black'))
    return fig

def make_figure_second(top_n):
    df = action_time_df.head(top_n).copy()
    fig = px.bar(df, x='action', y='secs_elapsed',
                 labels={'secs_elapsed': 'Average Time (Seconds)', 'action': 'Action'})

    for _, row in df.iterrows():
        fig.add_annotation(
            x=row['action'],
            y=row['secs_elapsed'],
            text=row['time_formatted'],
            showarrow=False,
            font=dict(size=12, color="black", family="Arial"),
            align="center",
            bgcolor="white"
        )

    fig.update_layout(
        xaxis_title='<b>Action</b>',
        yaxis_title='<b>Average Time (Seconds)</b>',
        margin=dict(l=40, r=40, t=40, b=40),
        autosize=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
    )
    fig.update_traces(marker_color='#FF5A5F')
    fig.update_xaxes(tickfont=dict(size=12, family='Arial', color='black'))
    fig.update_yaxes(showticklabels=False, title_font=dict(size=14, family='Arial', color='black'))
    return fig

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3(id='plot-title', style={"color": "#FF5A5F", "font-weight": "bold", "text-align": "center"})
        ], width=12),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Number of top actions:", style={"margin-right": "10px"}),
                dcc.Input(
                    id='top-n-input',
                    type='number',
                    value=10,
                    min=1,
                    max=50,
                    step=1,
                    style={"width": "80px", "margin-right": "30px"}
                ),
                html.Label("Chart type:", style={"margin-right": "10px"}),
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': 'Actions', 'value': 'first'},
                        {'label': 'Average Duration', 'value': 'second'}
                    ],
                    value='first',
                    style={"width": "200px", "display": "inline-block"}
                )
            ], style={"display": "flex", "justify-content": "flex-end", "align-items": "center"})
        ], width=12, style={"margin-bottom": "20px"}),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='top-actions-graph', config={'responsive': True})
        ], width=12)
    ])
], fluid=True)

@dash.callback(
    [Output('top-actions-graph', 'figure'),
     Output('plot-title', 'children')],
    [Input('dropdown', 'value'),
     Input('top-n-input', 'value')]
)
def update_plot(selected_value, top_n):
    if top_n is None or top_n < 1:
        top_n = 10
    if selected_value == 'first':
        return make_figure_first(top_n), f"Top {top_n} Most Common User Actions"
    else:
        return make_figure_second(top_n), f"Top {top_n} Actions by Average Time Spent (hh:mm)"
