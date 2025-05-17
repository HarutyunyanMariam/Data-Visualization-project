import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import datetime
import plotly.graph_objects as go

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB])

server = app.server

toggle_button = dbc.Button(
    "☰",
    color="danger",
    className="ms-2 sidebar-toggle",  
    id="toggle-button",
    n_clicks=0,
    style={"float": "left"}
)

sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page["name"], className="ms-2")
            ],
            href=page["path"],
            active="exact"
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className="bg-light sidebar-nav", 
    id="sidebar"
)

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(toggle_button, width=1),

        dbc.Col(
            dbc.Row([
                dbc.Col(
                    html.Img(
                        src="assets/Airbnb_Logo.png",
                        style={"height": "100px", "width": "auto"}
                    ),
                    width="auto"
                ),
                dbc.Col(
                    html.H1(
                        "Main insights for Airbnb bookings",
                        style={
                            "color": "#FF5A5F",
                            "font-family": "Arial, sans-serif",
                            "font-size": "65px",
                            "font-weight": "bold",
                            "text-align": "center",
                            "width": "100%",
                            "margin": "auto"
                        }
                    ),
                    className="d-flex align-items-center justify-content-center"
                )
            ], align="center"),
            width=11
        )
    ]),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(sidebar, width=2, id="sidebar-col"),
            dbc.Col(dash.page_container, width=10, id="content-col")
        ]
    )

], fluid=True)


@app.callback(
    Output("sidebar-col", "width"),
    Output("content-col", "width"),
    Output("sidebar-col", "style"),
    Input("toggle-button", "n_clicks"),
    State("sidebar-col", "width"),
)
def toggle_sidebar(n_clicks, sidebar_width):
    if n_clicks:
        if sidebar_width == 2:
            return 0, 12, {"display": "none"}
        else:
            return 2, 10, {}

    return sidebar_width, 10, {}

if __name__ == '__main__':
    app.run(debug=True)
