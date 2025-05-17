# pg1.py
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

dash.register_page(__name__, path='/', title='Airbnb statistics', name='Countries')

age_gender = pd.read_csv('assets/age_gender_bkts.csv')  

country_name_map = {
    'US': 'United States',
    'FR': 'France',
    'IT': 'Italy',
    'DE': 'Germany',
    'GB': 'United Kingdom',
    'ES': 'Spain',
    'CA': 'Canada',
    'AU': 'Australia',
    'NL': 'Netherlands',
    'PL': 'Portugal',
}

x_axis_labels = age_gender.age_bucket.unique()[::-1]
countries = age_gender.country_destination.unique()
country_options = [
    {"label": country_name_map.get(c, c), "value": c} for c in countries
]


def make_figure(selected_country):
    data_male = age_gender[(age_gender["country_destination"] == selected_country) & (age_gender["gender"] == 'male')]
    data_female = age_gender[(age_gender["country_destination"] == selected_country) & (age_gender["gender"] == 'female')]

    base = pd.DataFrame(x_axis_labels, columns=['0'])
    base = base.merge(data_male, how='left', left_on='0', right_on='age_bucket')
    base = base.merge(data_female, how='left', left_on='0', right_on='age_bucket')

    male_vals = base["population_in_thousands_x"].fillna(0)
    female_vals = base["population_in_thousands_y"].fillna(0)

    trace_male = go.Bar(
        x=x_axis_labels,
        y=male_vals,
        name="Male",
        marker_color='steelblue',
        text=[f'<b>{v}</b>' for v in male_vals],  
        textposition='auto'
    )

    trace_female = go.Bar(
        x=x_axis_labels,
        y=female_vals,
        name="Female",
        marker_color='lightcoral',
        text=[f'<b>{v}</b>' for v in female_vals],  # Bold text on bars
        textposition='auto'
    )

    fig = go.Figure(data=[trace_male, trace_female])

    fig.update_layout(
        title='',  
        barmode="group",
        legend=dict(x=0.7, y=1.1, orientation='h'),
        margin=dict(l=40, r=40, t=80, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        autosize=True,

        xaxis=dict(
            title=dict(text='Age Bucket', font=dict(size=14, color='black', family='Arial Black')),
            tickfont=dict(family='Arial Black', size=12, color='black')
        ),
        yaxis=dict(
            title=dict(text='Population (x 1000)', font=dict(size=14, color='black', family='Arial Black')),
            tickfont=dict(family='Arial Black', size=12, color='black')
        )
    )

    return fig



layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("Age & Gender Distribution by Country", style={"color": "#FF5A5F", "font-weight": "bold"})
        ], width=8),

        dbc.Col([
            dcc.Dropdown(
                id='country-dropdown',
                options=country_options,
                value=countries[0],
                clearable=False,
                style={
                    "fontWeight": "bold",
                    "color": "#FF5A5F",
                    "border": "2px solid #FF5A5F",
                },
                placeholder="Select Country",
                className='custom-dropdown'
            )
        ], width=4)
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='age-gender-graph', figure=make_figure(countries[0]), config={'responsive': True})
        ])
    ])
], fluid=True)


@dash.callback(
    Output('age-gender-graph', 'figure'),
    Input('country-dropdown', 'value')
)
def update_figure(selected_country):
    fig = make_figure(selected_country)
    return fig



