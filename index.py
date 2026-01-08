from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime as dt

from dash_bootstrap_templates import ThemeSwitchAIO
import dash

FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
app = dash.Dash(__name__, external_stylesheets=FONT_AWESOME)
app.scripts.config.serve_locally = True
server = app.server

# ========== Styles ============ #
tab_card = {'height': '100%'}

main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":0.1,
                "title": {"text": None},
                "font" :{"color":"white"},
                "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":10, "r":10, "t":10, "b":10}
}

config_graph={"displayModeBar": False, "showTips": False}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY


# ===== Reading n cleaning File ====== #
df = pd.read_csv('original-system.csv')
df_cru = df.copy()


epic_list = df["issue_key"].unique()
df["issue_key"] = df["issue_key"].fillna("Not Identified")
epic_list = df["issue_key"].unique().tolist()


app.layout = dbc.Container(
    children=[
        dbc.Row([
            dbc.Col(
                html.Div(
                    id="banner",
                    className="banner",
                    children=[html.Img(src=app.get_asset_url("plotly_logo.png"))],
                ),
            ),
            
            dbc.Col(
                ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]), style={'margin-top': '30px', 'align': 'Right'}
            ),
            dbc.Col(
                html.Div(
                    [
                        dbc.Button("Notifications", id="open-fs", color="primary", className="me-md-2"),
                        dbc.Button("Configuration", id="open-conf", className="me-md-2"),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Configuration")),
                                dbc.ModalBody([
                                dbc.Alert("Apply configuration here", color="primary", dismissable=True),
                                ]),
                            ],
                            id="modal-conf",
                            fullscreen=True,
                        ),
                        dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("Alerts about your JIRA Project")),
                                    dbc.ModalBody([
                                    dbc.Alert("This is a primary alert", color="primary", dismissable=True),
                                    dbc.Alert("This is a secondary alert", color="secondary", dismissable=True),
                                    dbc.Alert("This is a success alert! Well done!", color="success", dismissable=True),
                                    dbc.Alert("This is a warning alert... be careful...", color="warning", dismissable=True),
                                    dbc.Alert("This is a danger alert. Scary!", color="danger", dismissable=True),
                                    dbc.Alert("This is an info alert. Good to know!", color="info", dismissable=True),
                                    dbc.Alert("This is a light alert", color="light", dismissable=True),
                                    dbc.Alert("This is a dark alert", color="dark", dismissable=True),
                                    ]),
                                ],
                                id="modal-fs",
                                fullscreen=True,
                            ),

                    ],
                    className="d-grid gap-2 d-md-flex justify-content-md-end", style={'margin-top': '25px'},
                ),
                
            ),
            
            
        ]),
        # row 1
        dbc.Row([
            dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                                dbc.Row(
                                    html.Div(
                                    id="description-card",
                                    children=[
                                        html.H5("Initiative Dashboard"),
                                        html.Div(
                                            id="intro",
                                            children="Figure out How your Team is performing",
                                        ),
                                    ],
                                )
                                ),

                                dbc.Row([
                                    dbc.Col([
                                    html.P("Select Date Interval"),
                                    dcc.DatePickerRange(
                                        id="date-picker-select",
                                        start_date=dt(2014, 1, 1),
                                        end_date=dt(2014, 1, 15),
                                        min_date_allowed=dt(2014, 1, 1),
                                        max_date_allowed=dt(2014, 12, 31),
                                        initial_visible_month=dt(2014, 1, 1),
                                    ),
                                    ])
                                ]),
                                dbc.Row(
                                    dbc.Col([
                                    html.Br(),                                
                                    html.P("Select Epic"),
                                    dcc.Dropdown(
                                        id="epic-select",
                                        options=[{"label": i, "value": i} for i in epic_list],
                                        value=epic_list[0],
                                    ),
                                ])
                        ),
                            dbc.Row(
                            dbc.Col([
                                html.Br(),
                                html.P("Select Initiative"),
                                dcc.Dropdown(
                                    id="admit-select",
                                    options=[{"label": i, "value": i} for i in epic_list],
                                    value=epic_list[0],
                                    multi=True,
                                )


                            ]
                                
                            )

                        ),
                        ])
                    ], style=tab_card)
            ], sm=4, lg=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col(
                                html.Legend('Cycle Time and Throughtput')
                            )
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph1', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph2', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                                
                            ], sm=12, md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph3', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph4', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=3),
                        ]),
                    ])
                ], style=tab_card)
        ], sm=12, lg=9),

    ], className='g-2 my-auto', style={'margin-top': '7px'}),
# Row 2
dbc.Row([
    dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col(
                                html.Legend('Cumulative Flow')
                            )
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph5', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph6', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                                
                            ], sm=12, md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph7', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=4),
                        ]),
                    ])
                ], style=tab_card)
        ], sm=12, lg=12),
], className='g-2 my-auto', style={'margin-top': '7px'}),

# Row 3
dbc.Row([
    dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col(
                                html.Legend('')
                            )
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph9', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph10', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                                
                            ], sm=12, md=6),
                        ]),
                    ])
                ], style=tab_card)
        ], sm=12, lg=12),
], className='g-2 my-auto', style={'margin-top': '7px'}),
dbc.Row([
    dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col(
                                html.Legend('')
                            )
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph11', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph12', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                                
                            ], sm=12, md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph13', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                                
                            ], sm=12, md=4),
                        ]),
                    ])
                ], style=tab_card)
        ], sm=12, lg=12),
]),
dbc.Row([
        dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col(
                                html.Legend('')
                            )
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph14', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                            ], sm=12, md=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='graph15', className='dbc', config=config_graph)
                                        ])
                                    ], style=tab_card),
                                
                            ], sm=12, md=6),
                        ]),
                    ])
                ], style=tab_card)
        ], sm=12, lg=12),
]),

    ], fluid=True, style={'height': '100vh'}
)


@app.callback(
    Output("modal-fs", "is_open"),
    Input("open-fs", "n_clicks"),
    State("modal-fs", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal-conf", "is_open"),
    Input("open-conf", "n_clicks"),
    State("modal-conf", "is_open"),
)
def toggle_modal_conf(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)