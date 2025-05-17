# pg2.py

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input

dash.register_page(__name__, path='/top-actions', title='Top Actions', name='Top Actions')

# === DATA LOAD ===
sessions = pd.read_csv('assets/sessions.csv')  # Make sure sessions.csv is in assets folder

# First Plot: Top 15 Most Common Actions
action_counts = sessions['action'].value_counts().reset_index()
action_counts.columns = ['action', 'count']
action_counts_top_15 = action_counts.head(15).copy()
action_counts_top_15['formatted_count'] = action_counts_top_15['count'].apply(lambda x: f"{x:,}")

# Second Plot: Top 20 Actions by Average Time Spent (in hh:mm)
action_time = sessions.groupby('action')['secs_elapsed'].mean().reset_index()
action_time_sorted = action_time.sort_values(by='secs_elapsed', ascending=False).head(20)
action_time_sorted['hours'] = action_time_sorted['secs_elapsed'] // 3600  
action_time_sorted['minutes'] = (action_time_sorted['secs_elapsed'] % 3600) // 60  
action_time_sorted['time_formatted'] = action_time_sorted['hours'].astype(int).astype(str) + ":" + \
                                        action_time_sorted['minutes'].astype(int).astype(str).str.zfill(2)

# === FUNCTION TO MAKE THE FIRST FIGURE ===
def make_figure_first():
    fig = px.bar(action_counts_top_15, x='action', y='count')
    fig.update_traces(
        text=action_counts_top_15['formatted_count'],
        textposition='outside',
        marker_color='#FF5A5F'  # Airbnb red bars
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

# === FUNCTION TO MAKE THE SECOND FIGURE ===
def make_figure_second():
    fig = px.bar(action_time_sorted, x='action', y='secs_elapsed', 
                 labels={'secs_elapsed': 'Average Time (Seconds)', 'action': 'Action'})

    for i, row in action_time_sorted.iterrows():
        fig.add_annotation(
            x=row['action'], 
            y=row['secs_elapsed'], 
            text=row['time_formatted'],  # Show time in hh:mm format
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
    fig.update_traces(
        marker_color='#FF5A5F',  # Airbnb red bars
    )
    fig.update_xaxes(tickfont=dict(size=12, family='Arial', color='black'))
    fig.update_yaxes(tickfont=dict(size=12, family='Arial', color='black'))
    return fig

# === DASH LAYOUT ===
layout = dbc.Container([
    dbc.Row([  # Header
        dbc.Col([  # Title
            html.H3(id='plot-title', style={"color": "#FF5A5F", "font-weight": "bold", "text-align": "center"})
        ], width=12),  # Title column
    ]),

    html.Hr(),  # Horizontal line

    dbc.Row([  # Dropdown and plot
        dbc.Col([  # Dropdown container
            dcc.Dropdown(
                id='dropdown',
                options=[
                    {'label': 'Actions', 'value': 'first'},  # Changed text to 'Actions'
                    {'label': 'Average Duration', 'value': 'second'}  # Changed text to 'Average Duration'
                ],
                value='first',  # Default value
                style={"width": "250px", "float": "right", "margin-right": "20px", "textAlign": "left"}  # Aligned text to the left
            )
        ], width=12, style={"text-align": "right"}),  # Align dropdown to right

        dbc.Col([  # Graph container
            dcc.Graph(id='top-actions-graph', figure=make_figure_first(), config={'responsive': True})
        ], width=12)
    ])
], fluid=True)


# === CALLBACK TO UPDATE THE PLOT BASED ON DROPDOWN SELECTION ===
@dash.callback(
    [Output('top-actions-graph', 'figure'),
     Output('plot-title', 'children')],  # Output for title as well
    Input('dropdown', 'value')
)
def update_plot(selected_value):
    if selected_value == 'first':
        return make_figure_first(), "Top 15 Most Common User Actions"
    else:
        return make_figure_second(), "Top 20 Actions by Average Time Spent (hh:mm)"
