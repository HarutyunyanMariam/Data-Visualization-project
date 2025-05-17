import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Output, Input
import numpy as np
from scipy.stats import gaussian_kde
from functools import lru_cache


dash.register_page(__name__, path='/account-booking-distribution', title='Account & Booking Distribution', name='Account & Booking Distribution')

@lru_cache(maxsize=1)
def load_age_gender_data():
    return pd.read_csv('assets/train_users_2.csv') 

users = load_age_gender_data()

users['date_account_created'] = pd.to_datetime(users['date_account_created'], errors='coerce')
users['date_first_booking'] = pd.to_datetime(users['date_first_booking'], errors='coerce')

months_account_created = users['date_account_created'].dropna().dt.month_name().str[:3]
months_first_booking = users['date_first_booking'].dropna().dt.month_name().str[:3]

counts_account = months_account_created.value_counts()
counts_booking = months_first_booking.value_counts()

percent_account = counts_account / counts_account.sum() * 100
percent_booking = counts_booking / counts_booking.sum() * 100

users['signup_method'] = users['signup_method'].fillna('NaN')
counts_signup = users['signup_method'].value_counts()
percent_signup = counts_signup / users.shape[0] * 100

counts_device = users['first_device_type'].fillna('NaN').value_counts(dropna=False)
percent_device = counts_device / users.shape[0] * 100

users['gender'] = users['gender'].fillna('NaN')
counts_gender = users['gender'].value_counts()
percent_gender = counts_gender / users.shape[0] * 100

filtered_users = users[(users['age'] < 120) & (users['age'].notnull())]
hist_data_age = filtered_users['age']
kde = gaussian_kde(hist_data_age, bw_method=0.3)
x_range_age = np.linspace(hist_data_age.min(), hist_data_age.max(), 1000)
kde_values_age = kde(x_range_age)

counts_country = users['country_destination'].fillna('NaN').value_counts(dropna=False)
percent_country = counts_country / users.shape[0] * 100

counts_app = users['signup_app'].fillna('NaN').value_counts(dropna=False)
percent_app = counts_app / users.shape[0] * 100

counts_affiliate = users['affiliate_provider'].fillna('NaN').value_counts(dropna=False).head(10)
percent_affiliate = counts_affiliate / users.shape[0] * 100

def make_figure(x_labels, counts, percents, title, xaxis_title=''):
    fig = go.Figure(go.Bar(
        x=x_labels,
        y=counts,
        text=[f"{count:,} ({perc:.1f}%)" for count, perc in zip(counts, percents)],
        textposition='outside',
        marker_color='#FF5A5F',
        textfont=dict(size=14)
    ))

    fig.update_layout(
        title={'text': title, 'x': 0.5},
        xaxis_title=xaxis_title,
        yaxis_title='Count',
        margin=dict(l=20, r=20, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        autosize=True,
        showlegend=False,
        font=dict(size=14),
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16))
    )
    return fig


def make_age_figure():
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=hist_data_age,
        nbinsx=60,
        name='Age Distribution',
        opacity=0.6,
        marker=dict(color='skyblue'),
        histnorm='probability density'
    ))

    fig.add_trace(go.Scatter(
        x=x_range_age,
        y=kde_values_age,
        mode='lines',
        name='KDE',
        line=dict(color='red', width=2)
    ))

    fig.update_layout(
        title='Age Distribution with KDE (Age ≤ 120)',
        xaxis_title='Age',
        yaxis_title='Density',
        bargap=0.1,
        title_x=0.5,
        xaxis=dict(tickmode='linear', tick0=0, dtick=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        font=dict(size=14),
        margin=dict(l=20, r=20, t=60, b=60)
    )

    return fig

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H3("", style={"color": "#FF5A5F", "font-weight": "bold", "text-align": "center"}), width=12)
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label("Select Plot:", style={"font-weight": "bold", "margin-top": "8px"}), width="auto"),
                dbc.Col(dcc.Dropdown(
                    id='plot-selector',
                    options=[
                        {'label': 'Account Creation Month', 'value': 'account'},
                        {'label': 'Booking Date Month', 'value': 'booking'},
                        {'label': 'Signup Method', 'value': 'signup'},
                        {'label': 'First Device Type', 'value': 'device'},
                        {'label': 'Gender Distribution', 'value': 'gender'},
                        {'label': 'Age Distribution (≤120)', 'value': 'age'},
                        {'label': 'Destination Country', 'value': 'country'},
                        {'label': 'Signup App', 'value': 'app'},
                        {'label': 'Affiliate Providers', 'value': 'affiliate'}
                    ],
                    value='account',
                    clearable=False,
                    style={'minWidth': '260px'}
                ), width="auto"),
                dbc.Col(html.Label("Compare:", style={"font-weight": "bold", "margin-left": "15px", "margin-top": "8px"}), width="auto"),
                dbc.Col(dcc.Dropdown(
                    id='compare-selector',
                    options=[
                        {'label': 'None', 'value': 'none'},
                        {'label': 'Account vs Booking', 'value': 'account_booking'},
                        {'label': 'Age vs Gender', 'value': 'age_gender'}
                    ],
                    value='none',
                    clearable=False,
                    style={'minWidth': '220px'}
                ), width="auto")
            ], align="center", justify="end", style={"margin-bottom": "10px"})
        ], width=12)
    ]),

    dbc.Row(id='graph-row', children=[
        dbc.Col(dcc.Graph(id='distribution-graph', config={'responsive': True}, style={'width': '100%', 'height': '80vh'}), width=12)
    ])
], fluid=True)

@dash.callback(
    Output('graph-row', 'children'),
    [Input('plot-selector', 'value'),
     Input('compare-selector', 'value')]
)
def update_graph(selected, compare):
    if compare == 'account_booking':
        fig1 = make_figure(counts_account.index.tolist(), counts_account.values, percent_account.values,
                           'Account Creation Month Distribution', 'Month')
        fig2 = make_figure(counts_booking.index.tolist(), counts_booking.values, percent_booking.values,
                           'Booking Date Month Distribution', 'Month')

        return [
            dbc.Col(dcc.Graph(figure=fig1, config={'responsive': True}, style={'height': '80vh'}), width=6),
            dbc.Col(dcc.Graph(figure=fig2, config={'responsive': True}, style={'height': '80vh'}), width=6)
        ]

    elif compare == 'age_gender':
        fig1 = make_age_figure()
        fig2 = make_figure(counts_gender.index.tolist(), counts_gender.values, percent_gender.values,
                           'Gender Distribution', 'Gender')

        return [
            dbc.Col(dcc.Graph(figure=fig1, config={'responsive': True}, style={'height': '80vh'}), width=6),
            dbc.Col(dcc.Graph(figure=fig2, config={'responsive': True}, style={'height': '80vh'}), width=6)
        ]

    else:
        if selected == 'account':
            fig = make_figure(counts_account.index.tolist(), counts_account.values, percent_account.values,
                              'Account Creation Month Distribution', 'Month')
        elif selected == 'booking':
            fig = make_figure(counts_booking.index.tolist(), counts_booking.values, percent_booking.values,
                              'Booking Date Month Distribution', 'Month')
        elif selected == 'signup':
            fig = make_figure(counts_signup.index.tolist(), counts_signup.values, percent_signup.values,
                              'Signup Method Distribution', 'Signup Method')
        elif selected == 'device':
            fig = make_figure(counts_device.index.tolist(), counts_device.values, percent_device.values,
                              'First Device Type Distribution', 'First Device Type')
        elif selected == 'gender':
            fig = make_figure(counts_gender.index.tolist(), counts_gender.values, percent_gender.values,
                              'Gender Distribution', 'Gender')
        elif selected == 'age':
            fig = make_age_figure()
        elif selected == 'country':
            fig = make_figure(counts_country.index.tolist(), counts_country.values, percent_country.values,
                              'Destination Country Distribution', 'Destination Country')
        elif selected == 'app':
            fig = make_figure(counts_app.index.tolist(), counts_app.values, percent_app.values,
                              'Signup App Distribution', 'Signup App')
        elif selected == 'affiliate':
            fig = make_figure(counts_affiliate.index.tolist(), counts_affiliate.values, percent_affiliate.values,
                              'Affiliate Provider Distribution', 'Affiliate Provider')

        return [dbc.Col(dcc.Graph(figure=fig, config={'responsive': True}, style={'height': '80vh'}), width=12)]
