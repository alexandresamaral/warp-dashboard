import analysis
import status
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime as dt
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_bootstrap_templates import ThemeSwitchAIO
import collections
import flow
import os

# ===== Reading n cleaning File ====== #
DATA_FILE = "original.csv"
df = pd.read_csv("original.csv")
df_cru = df.copy()


FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.PULSE, dbc.icons.BOOTSTRAP]
)
# dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX]
# dash.Dash(__name__, external_stylesheets=[FONT_AWESOME, dbc.themes.LUX, dbc.icons.BOOTSTRAP])


app.scripts.config.serve_locally = True
server = app.server

# ========== Styles ============ #

menu_button_config = {
    "display": "inline-block",
    "outline": 0,
    "cursor": "pointer",
    "text-align": "center",
    "border": "1px solid #babfc3",
    "padding": "11px 24px",
    "min-height": "44px",
    "min-width": "44px",
    "color": "#9F9F9F",
    "background": "#ffffff",
    "border-radius": "4px",
    "font-weight": "500",
    "font-size": "14px",
    "box-shadow": "rgba(0, 0, 0, 0.05) 0px 1px 0px 0px",
    "hover": {
        "background": "#f6f6f7",
        "outline": "1px solid transparent",
    },
}

tab_card = {
    "height": "100%",
    "width": "100%",
    "margin": {"l": 5, "r": 1, "t": 1, "b": 1},
}

main_config = {
    "hovermode": "x unified",
    "legend": {
        "yanchor": "top",
        "y": 0.9,
        "xanchor": "left",
        "x": 0.1,
        "title": {"text": None},
        "font": {"color": "white"},
        "bgcolor": "rgba(0,0,0,0.5)",
    },
    "margin": {"l": 3, "r": 3, "t": 3, "b": 3},
}

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

config_graph = {"displayModeBar": False, "showTips": False}
config_graph_modal = {"displayModeBar": True, "showTips": True}

button_max_style = {
    "cursor": "pointer",
    "outline": 0,
    "display": "inline-block",
    "font-weight": 400,
    "line-height": 1.5,
    "text-align": "center",
    "background-color": "transparent",
    "border": "1px solid transparent",
    "padding": "6px 12px",
    "font-size": "1rem",
    "border-radius": ".25rem",
    "transition": "color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out",
    "color": "#0d6efd",
    "border-color": "#0d6efd",
}

accordion_style = {
    "root": {
        "backgroundColor": dmc.theme.DEFAULT_COLORS["blue"][2],
        "borderRadius": 5,
    },
    "item": {
        "backgroundColor": dmc.theme.DEFAULT_COLORS["blue"][2],
        "border": "1px solid transparent",
        "position": "relative",
        "zIndex": 0,
        "transition": "transform 150ms ease",
        "&[data-active]": {
            "transform": "scale(1.03)",
            "backgroundColor": "white",
            "boxShadow": 5,
            "borderColor": dmc.theme.DEFAULT_COLORS["gray"][2],
            "borderRadius": 5,
            "zIndex": 1,
        },
    },
    "chevron": {
        "&[data-rotate]": {
            "transform": "rotate(-90deg)",
        },
    },
}

title_style = {"fontSize": 14}
title_style_full = {"fontSize": 20}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.COSMO
url_theme2 = dbc.themes.LUMEN

OMIT_ISSUE_TYPES = ("Epic","Subtarefa")
EXCLUDE_WEEKENDS = False
FILTER_ISSUES_UNTIL = "2020-08-01"  # e.g., '2021-12-01', 'today', etc
FILTER_ISSUES_SINCE = "2020-07-15"  # (pandas.to_datetime(FILTER_ISSUES_UNTIL) - pandas.Timedelta(days=365)).strftime('%Y-%m-%d')

SIMULATION_DAYS = 5  # N
SIMULATION_ITEMS = 5  # N
SIMULATIONS = 10
LAST_DAYS = 10

status_df = pd.read_csv('data/status.csv')
print(status_df)

# ========== c Status ======== #
STATUS_ORDER = status_df["status_name"].unique()
print(STATUS_ORDER)


### read data ###
data, dupes, filtered = analysis.read_data(
    DATA_FILE, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
)
print(data)

### process issue data ###
issue_data, (categories, *extra) = analysis.process_issue_data(
    data, exclude_weekends=EXCLUDE_WEEKENDS
)

### calculate cycle data ###
cycle_data = analysis.process_cycle_data(issue_data)
cycle_data = cycle_data.reset_index()
### calculate Throughput per week ###
throughput, throughput_per_week = analysis.process_throughput_data(
    issue_data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
)
### calculate work in progress ###
wip, _ = analysis.process_wip_data(
    issue_data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
)
wip = wip.reset_index()
wip_melted = pd.melt(wip, ["Date"])
wip_melted["value"] = wip_melted["value"].astype(float)
### calculate aging tickets ###
age_data = analysis.process_wip_age_data(
    issue_data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
)

### Monte carlo distribution items and days
distribution_when, samples = analysis.forecast_montecarlo_how_long_items(
         throughput, items=SIMULATION_ITEMS, simulations=SIMULATIONS, window=LAST_DAYS
     )
distribution_how, samples_how = analysis.forecast_montecarlo_how_many_items(
     throughput, days=SIMULATION_DAYS,simulations=SIMULATIONS,window=LAST_DAYS)


# ========== Epic Status ======== #
epic_list = df["project_key"].unique()
df["project_key"] = df["project_key"].fillna("Not Identified")
epic_list = df["project_key"].unique().tolist()


# ========== Status ======== #
status_file_path = "data/status.csv"
data_status = []

# Etapa 1: Tenta carregar os status e sua ordem do `status.csv`.
if os.path.exists(status_file_path) and os.path.getsize(status_file_path) > 0:
    status_data = status.fetch_from_csv("PRJ", status_file_path)
    if status_data:
        data_status = [item['status_name'] for item in status_data]

# Etapa 2: Pega todos os status únicos do dataframe principal para encontrar os que estão faltando.
# Usar dropna() para evitar problemas com valores nulos.
all_statuses = df["status_from_name"].dropna().unique().tolist()

# Etapa 3: Se `status.csv` estava vazio ou não existia, inicializa com os status do dataframe.
if not data_status and all_statuses:
    status.save_to_csv("PRJ", all_statuses, status_file_path)
    data_status = status.fetch_from_csv("PRJ", status_file_path)


# Etapa 4: Verifica se há novos status no dataframe que não estão na lista atual.
new_statuses = [s for s in all_statuses if s not in data_status]

print("------new------")
print(new_statuses)
print("-------all-----")
print(all_statuses)
print("-------data-----")
print(data_status)
print("--- new status")
print(new_statuses)

if new_statuses:
    # Adiciona os novos status ao arquivo. A função `save_to_csv` deve anexar.
    status.save_to_csv("PRJ", new_statuses, status_file_path)
    # Recarrega a lista completa do arquivo para garantir que a ordem está 100% correta.
    reloaded_status_data = status.fetch_from_csv("PRJ", status_file_path)
    if reloaded_status_data:
        data_status = [item['status_name'] for item in reloaded_status_data]


print("carregando lista de issue types")
issue_list = df["issue_type_name"].unique()
df["issue_type_name"] = df["issue_type_name"].fillna("Not Identified")
issue_list = df["issue_type_name"].unique().tolist()

# ========= cards ============#
icon = "bi bi-arrow-up"
color = "primary"


####### get icons #############


def get_icon(icon):
    return DashIconify(icon=icon, height=16, color="#000000")


def create_nav_link(label, href):
    return dmc.NavLink(
        label=label,
        href=href,
        style={"display": "inline-block"},
    )


data_canada = px.data.gapminder().query("country == 'Brazil'")
fig = px.bar(data_canada, x="year", y="pop")

# ========= payouts ========= #


app.layout = dmc.MantineProvider(
    theme={
        "fontFamily": '"Inter", sans-serif',
        "components": {"NavLink": {"styles": {"label": {"color": "#000000"}}}},
    },
    children=[
        dmc.Container(
            [
                dmc.Navbar(
                    p="md",
                    fixed=False,
                    width={"base": 250},
                    hidden=True,
                    hiddenBreakpoint="md",
                    position="right",
                    height="auto",
                    id="sidebar",
                    children=[
                        html.Div(
                            [
                                # dmc.Image(
                                #    src="/assets/BF15.png", alt="superman", width=200
                                # ),
                                html.Br(),
                                html.Br(),
                                dmc.NavLink(
                                    label="Cycle Time",
                                    icon=get_icon(icon="mdi:timezone-outline"),
                                    childrenOffset=28,
                                    opened=False,
                                    children=[
                                        dmc.NavLink(label="Average", id="link_Average"),
                                        dmc.NavLink(label="Scatterplot", id="link_Scatterplot"),
                                        dmc.NavLink(label="Histogram", id="link_Histogram"),
                                    ],
                                ),

                                dmc.NavLink(
                                    label="Throughput",
                                    icon=get_icon(icon="hugeicons:safe-delivery-01"),
                                    childrenOffset=28,
                                    opened=False,
                                    children=[
                                        dmc.NavLink(label="Throughput Week", id="link_tp_week"),
                                    ],
                                ),

                                dmc.NavLink(
                                    label="WIP",
                                    icon=get_icon(icon="carbon:progress-bar"),
                                    childrenOffset=28,
                                    opened=False,
                                    children=[
                                        dmc.NavLink(label="Aging", id="link_Aging"),
                                    ],
                                ),

                                dmc.NavLink(
                                    label="CFD",
                                    icon=get_icon(icon="icon-park-twotone:area-map"),
                                    childrenOffset=28,
                                    opened=False,
                                    children=[
                                        dmc.NavLink(label="Cumulative Flow", id="link_CFD"),
                                    ],
                                ),

                                dmc.NavLink(
                                    label="Montecarlo",
                                    icon=get_icon(icon="carbon:chart-histogram"),
                                    childrenOffset=28,
                                    opened=False,
                                    children=[
                                        dmc.NavLink(label="Montecarlo How Many", id="link_MC_Many"),
                                        dmc.NavLink(label="Montecarlo How Much", id="link_MC_Much"),
                                    ],
                                ),

                                dmc.NavLink(
                                    label="Story Points",
                                    icon=get_icon(icon="mdi:number-3-circle-outline"),
                                    childrenOffset=28,
                                    opened=False,
                                    children=[
                                        dmc.NavLink(label="Percent", id="link_Percent"),
                                        dmc.NavLink(label="Points x Cycle Time", id="link_Points_CT"),
                                        dmc.NavLink(label="Correlation", id="link_Correlation"),
                                    ],
                                ),
                            ],
                            style={"white-space": "wrap"},
                        )
                    ],
                    style={
                        "overflow": "hidden",
                        "transition": "width 0.1s ease-in-out",
                        "background-color": "#ffff",
                        "flexShrink": "0",
                    },
                ),
                dmc.Drawer(
                    title="Dashboard",
                    id="drawer-simple",
                    padding="md",
                    zIndex=10000,
                    size=1200,
                    overlayOpacity=0.1,
                    children=[],
                    style={"background-color": ""},
                    styles={"drawer": {"background-color": "#343a40"}},
                ),
                dmc.Container(
                    [
                        dmc.Header(
                            height=60,
                            children=[
                                dmc.Group(
                                    [
                                        dmc.MediaQuery(
                                            [
                                                dmc.Button(
                                                    DashIconify(
                                                        icon="ci:hamburger-lg",
                                                        width=24,
                                                        height=24,
                                                        color="#000000",
                                                    ),
                                                    variant="subtle",
                                                    p=1,
                                                    id="sidebar-button",
                                                )
                                            ],
                                            smallerThan="md",
                                            styles={"display": "none"},
                                        ),
                                        dmc.MediaQuery(
                                            [
                                                dmc.Button(
                                                    DashIconify(
                                                        icon="ci:hamburger-lg",
                                                        width=24,
                                                        height=24,
                                                        color="#000000",
                                                    ),
                                                    variant="subtle",
                                                    p=1,
                                                    id="drawer-demo-button",
                                                )
                                            ],
                                            largerThan="md",
                                            styles={"display": "none"},
                                        ),
                                        dmc.Image(
                                            src="../assets/BF9.png", alt="superman", width=200
                                        ),

                                        # dmc.Text("Bee Free"),

                                        # dbc.Col(
                                        #     dcc.Dropdown(
                                        #         id="epic-select",
                                        #         options=[
                                        #             {"label": i, "value": i}
                                        #             for i in epic_list
                                        #         ],
                                        #         value=epic_list[0],
                                        #         multi=True,
                                        #         style={
                                        #             "width": "100%",
                                        #             "height": "50%",
                                        #             "margin-top": "10px",
                                        #         },
                                        #         className="me-md-4",
                                        #     ),

                                        #     md=3,
                                        #     style={
                                        #         "margin-top": "0px",
                                        #         "align": "center",
                                        #         "height": "60",
                                        #     },
                                        # ),
                                        dbc.Col(
                                            dmc.MultiSelect(
                                                placeholder="Select Project",
                                                id="framework-multi-select",
                                                data=[
                                                    {"label": i, "value": i}
                                                    for i in epic_list
                                                ],
                                                w=400,
                                                mb=10,
                                            ),
                                            className="d-grid gap-2 d-md-flex justify-content-md-end h-25",
                                        ),

                                        dbc.Col(
                                            [
                                                dmc.ActionIcon(
                                                    DashIconify(
                                                        icon="oui:controls-horizontal",
                                                        width=20,
                                                    ),
                                                    size="lg",
                                                    variant="filled",
                                                    id="open-offcanvas",
                                                    n_clicks=0,
                                                    mb=10,
                                                ),
                                                dbc.Offcanvas(
                                                    [
                                                        dcc.DatePickerRange(
                                                            id="date-picker-select",
                                                            start_date=dt(2020, 6, 1),
                                                            end_date=dt(2020, 8, 30),
                                                            min_date_allowed=dt(
                                                                2020, 6, 1
                                                            ),
                                                            max_date_allowed=dt(
                                                                2020, 6, 1
                                                            ),
                                                            initial_visible_month=dt(
                                                                2020, 8, 30
                                                            ),
                                                            style={
                                                                "font-size": "6px",
                                                                "display": "inline-block",
                                                                "border-radius": "2px",
                                                                "border": "1px solid #ccc",
                                                                "color": "#333",
                                                                "border-spacing": "0",
                                                                "border-collapse": "separate",
                                                                "align": "center",
                                                            },
                                                        ),
                                                        html.Br(),
                                                        dmc.Accordion(
                                                            [
                                                                html.Br(),
                                                                dmc.AccordionItem(
                                                                    [
                                                                        dmc.AccordionControl(
                                                                            "Monte Carlo Simulation",
                                                                            icon=DashIconify(
                                                                                icon="tabler:user",
                                                                                color=dmc.theme.DEFAULT_COLORS[
                                                                                    "blue"
                                                                                ][
                                                                                    6
                                                                                ],
                                                                                width=20,
                                                                            ),
                                                                        ),
                                                                        dmc.AccordionPanel(
                                                                            [
                                                                                html.P(
                                                                                    "Please, informe number of Items to simulate",
                                                                                    style={
                                                                                        "fontSize": 12
                                                                                    },
                                                                                ),
                                                                                dbc.Input(
                                                                                    id="input_tries",
                                                                                    value=10,
                                                                                    placeholder="Only numbers...",
                                                                                    type="number",
                                                                                    min=0,
                                                                                    max=10000,
                                                                                    step=1,
                                                                                ),
                                                                                html.Br(),
                                                                                html.P(
                                                                                    "Please, informe number of Days to simulate",
                                                                                    style={
                                                                                        "fontSize": 12
                                                                                    },
                                                                                ),
                                                                                dbc.Input(
                                                                                    id="input_loops",
                                                                                    value=30,
                                                                                    placeholder="Only numbers...",
                                                                                    type="number",
                                                                                    min=1,
                                                                                    max=1500,
                                                                                    step=1,
                                                                                ),
                                                                                html.Br(),
                                                                                html.P(
                                                                                    "Please, informe number of Tries to simulate",
                                                                                    style={
                                                                                        "fontSize": 12
                                                                                    },
                                                                                ),
                                                                                dbc.Input(
                                                                                    id="input_simulation_tries",
                                                                                    value=1000,
                                                                                    placeholder="Only numbers",
                                                                                    type="number",
                                                                                    min=1,
                                                                                    max=100000,
                                                                                    step=1,
                                                                                ),
                                                                                html.Br(),
                                                                                html.P(
                                                                                    "Please, informe number of the Last Days to simulate",
                                                                                    style={
                                                                                        "fontSize": 12
                                                                                    },
                                                                                ),
                                                                                dbc.Input(
                                                                                    id="input_days",
                                                                                    value=10,
                                                                                    placeholder="only numbers",
                                                                                    type="number",
                                                                                    min=1,
                                                                                    max=1500,
                                                                                    step=1,
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                    value="info",
                                                                ),
                                                                dmc.AccordionItem(
                                                                    [
                                                                        dmc.AccordionControl(
                                                                            "Issue Type",
                                                                            icon=DashIconify(
                                                                                icon="tabler:map-pin",
                                                                                color=dmc.theme.DEFAULT_COLORS[
                                                                                    "red"
                                                                                ][
                                                                                    6
                                                                                ],
                                                                                width=20,
                                                                            ),
                                                                        ),
                                                                        dmc.AccordionPanel(
                                                                            [
                                                                                html.P(
                                                                                    "Set up your excluded Ticket type. Epic is default excluded",
                                                                                    style={
                                                                                        "fontSize": 12
                                                                                    },
                                                                                ),
                                                                                dcc.Dropdown(
                                                                                    id="issue-type-select",
                                                                                    options=[
                                                                                        {
                                                                                            "label": i,
                                                                                            "value": i,
                                                                                        }
                                                                                        for i in issue_list
                                                                                    ],
                                                                                    value= "Subtarefa",
                                                                                    multi=True,
                                                                                    style={
                                                                                        "width": "auto",
                                                                                        "height": "50%",
                                                                                        "margin-bottom": "10px",
                                                                                        "margin-left": "5px",
                                                                                    },
                                                                                    className="me-md-4",
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                    value="addr",
                                                                ),
                                                                dmc.AccordionItem(
                                                                    [
                                                                        dmc.AccordionControl(
                                                                            "Other",
                                                                            icon=DashIconify(
                                                                                icon="tabler:circle-check",
                                                                                color=dmc.theme.DEFAULT_COLORS[
                                                                                    "green"
                                                                                ][
                                                                                    6
                                                                                ],
                                                                                width=20,
                                                                            ),
                                                                        ),
                                                                        dmc.AccordionPanel(
                                                                            [
                                                                                dmc.Switch(
                                                                                    size="sm",
                                                                                    radius="lg",
                                                                                    label="Exclude Weekends",
                                                                                    checked=True,
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                    value="focus",
                                                                ),
                                                            ],
                                                            styles=accordion_style

                                                        ),
                                                        html.Div(
                                                            ThemeSwitchAIO(
                                                                aio_id="theme",
                                                                themes=[
                                                                    url_theme1,
                                                                    url_theme2,
                                                                ],
                                                            ),
                                                            style={
                                                                "margin-top": "15px",
                                                                "align": "center",
                                                            },
                                                        ),
                                                    ],
                                                    id="offcanvas",
                                                    title="Controls",
                                                    is_open=False,
                                                    placement="end",
                                                ),
                                                dbc.Tooltip(
                                                    "Settins: "
                                                    "Select your options to apply filters in your charts",
                                                    target="open-offcanvas",
                                                ),
                                                dmc.ActionIcon(
                                                    DashIconify(
                                                        icon="ic:baseline-notification-add",
                                                        width=20,
                                                    ),
                                                    size="lg",
                                                    variant="filled",
                                                    id="open-fs",
                                                    n_clicks=0,
                                                    mb=10,
                                                ),
                                                dbc.Tooltip(
                                                    "Click here to open Notification",
                                                    target="open-fs",
                                                ),
                                                dmc.ActionIcon(
                                                    DashIconify(
                                                        icon="clarity:settings-line",
                                                        width=20,
                                                    ),
                                                    size="lg",
                                                    variant="filled",
                                                    id="open-conf",
                                                    n_clicks=0,
                                                    mb=10,
                                                ),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            dbc.ModalTitle(
                                                                "Configuration"
                                                            )
                                                        ),
                                                        dbc.ModalBody(
                                                            [

                                                                dmc.Alert(
                                                                        id="status_msg",
                                                                        title="Status Order Update",
                                                                        color="red",
                                                                        
                                                                    ),
                                                                
                                                                dmc.Blockquote(
                                                                    [
                                                                        dmc.CheckboxGroup(
                                                                            id="checkbox-group",
                                                                            label="Select in order your statuses",
                                                                            description="This order will be used in your CFD Chart",
                                                                            withAsterisk=True,
                                                                            mb=10,
                                                                            children=dmc.Group(
                                                                                [dmc.Checkbox(label=k, value=k) for k in
                                                                                 data_status], my=10
                                                                            ),
                                                                            

                                                                        ),
                                                                        dmc.Text(id="checkbox-group-output"),
                                                                    ],
                                                                    icon=DashIconify(icon="codicon:flame", width=30),
                                                                    color="red",
                                                                ),
                                                                
                                                                
                                                               dmc.Group(
                                                                    [
                                                                        dmc.Button(
                                                                            "Save Status Order",
                                                                            leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
                                                                            id="status-order",
                                                                        ),
                                                                    ]
                                                                ),
                                                                html.Br(),
                                                                                                                               
                                                                
                                                                dmc.Stack(
                                                                    children=[
                                                                        dmc.Divider(variant="solid"),

                                                                    ],
                                                                ),
                                                                
                                                                dmc.Alert(
                                                                        id="status_wait_alert",
                                                                        title="Status wait Update",
                                                                        color="red",
                                                                        
                                                                    ),
                                                                
                                                                dmc.Blockquote(
                                                                    [
                                                                        dmc.CheckboxGroup(
                                                                            id="checkbox-group_wait",
                                                                            label="Select Wait statuses in your project",
                                                                            description="This will be used to calculate project efficience",
                                                                            withAsterisk=True,
                                                                            mb=10,
                                                                            children=dmc.Group(
                                                                                [dmc.Checkbox(label=k, value=k) for k in
                                                                                 data_status], my=10
                                                                            ),
                                                                            value=[item['status_name'] for item in status_data if item['wait_status'] == 'True'],

                                                                        ),
                                                                        dmc.Text(id="checkbox-group-output_wait"),
                                                                    ],

                                                                    icon=DashIconify(icon="codicon:flame", width=30),
                                                                    color="red",
                                                                ),
                                                                
                                                                dmc.Group(
                                                                    [
                                                                        dmc.Button(
                                                                            "Save Wait Status",
                                                                            leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
                                                                            id="status-wait",
                                                                        ),
                                                                    ]
                                                                ),
                                                                html.Br(),
                                                                
                                                                dmc.Stack(
                                                                    children=[
                                                                        dmc.Divider(variant="solid"),

                                                                    ],
                                                                ),

                                                                # html.Div(
                                                                #     [
                                                                #         dmc.TransferList(
                                                                #             id="transfer-list-simple",
                                                                #             value=initial_values,
                                                                #         ),
                                                                #         dmc.Text(
                                                                #             id="transfer-list-values-1",
                                                                #             mt=20,
                                                                #         ),
                                                                #         dmc.Text(
                                                                #             id="transfer-list-values-2",
                                                                #             mt=20,
                                                                #         ),
                                                                #     ]
                                                                # ),
                                                            ]
                                                        ),
                                                    ],
                                                    id="modal-conf",
                                                    fullscreen=True,
                                                ),
                                                dbc.Tooltip(
                                                    "Click here to open configuration space",
                                                    target="open-conf",
                                                ),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            dbc.ModalTitle(
                                                                "Alerts about your JIRA Project"
                                                            )
                                                        ),
                                                        dbc.ModalBody(
                                                            [
                                                                dmc.Alert(
                                                                    "Throughtput hate is 3.94",
                                                                    title="Primary",
                                                                    color="blue",
                                                                    withCloseButton=True,
                                                                ),
                                                                html.Br(),
                                                                dmc.Alert(
                                                                    "Your Dashboard is sincronized with JIRA",
                                                                    title="Success",
                                                                    color="gray",
                                                                    withCloseButton=True,
                                                                ),
                                                                html.Br(),
                                                                dmc.Alert(
                                                                    "10% of you tickets don`t have Epics... Check Please...",
                                                                    color="Warning",
                                                                    withCloseButton=True,
                                                                ),
                                                                html.Br(),
                                                                dmc.Alert(
                                                                    "You have 10 bugs",
                                                                    title="Danger",
                                                                    color="red",
                                                                    withCloseButton=True,
                                                                ),
                                                                html.Br(),
                                                                dmc.Alert(
                                                                    "This is an info alert. Good to know!",
                                                                    title="Info",
                                                                    color="green",
                                                                    withCloseButton=True,
                                                                ),
                                                                html.Br(),
                                                                dmc.Alert(
                                                                    "Check your Customer Leadtime, average is higher than usual",
                                                                    title="Info",
                                                                    color="yellow",
                                                                    withCloseButton=True,
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    id="modal-fs",
                                                    fullscreen=True,
                                                ),
                                                dmc.Avatar(
                                                    src="https://avatars.githubusercontent.com/u/91216500?v=4",
                                                    radius="xl",
                                                ),
                                                ### add end groupbutton
                                            ],
                                            className="d-grid gap-2 d-md-flex justify-content-md-end h-25",
                                            style={"margin-top": "5px"},
                                        ),
                                    ]
                                )
                            ],
                            p="10px",
                            style={"backgroundColor": "#ffff"},
                        ),
                        dmc.Container(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    html.Div(
                                                        [
                                                            html.H4(
                                                                [
                                                                    # html.Img(
                                                                    #    src="/assets/line-chart.png",
                                                                    #    height=25,
                                                                    #    className="me-1",
                                                                    # ),
                                                                    "Cycle Time",
                                                                ],
                                                                style={
                                                                    "font-size": "15px"
                                                                },
                                                            ),

                                                            html.H5(
                                                                [
                                                                    dmc.Title(id="ct85", order=2),
                                                                ],
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),

                                                            html.H4(
                                                                "were required to complete",
                                                                style={
                                                                    "font-size": "15px"
                                                                },
                                                            ),
                                                            html.H5(
                                                                [
                                                                    f"{round(85, 2)}%",
                                                                    " of Items",
                                                                ],
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),
                                                        ],
                                                        className=f"border-{color} border-start border-3",
                                                    ),
                                                    className="text-center text-nowrap my-1 p-1",
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    html.Div(
                                                        [
                                                            html.H4(
                                                                [
                                                                    # html.Img(
                                                                    #    src="/assets/kanban1.png",
                                                                    #    height=25,
                                                                    #    className="me-1",
                                                                    # ),
                                                                    "WIP",
                                                                ],
                                                                style={
                                                                    "font-size": "15px"
                                                                },
                                                            ),
                                                            html.H5(
                                                                dmc.Title(id="wip_card", order=2),
                                                                "Items",
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),
                                                            html.H4(
                                                                [
                                                                    "are currently"
                                                                ],
                                                                style={
                                                                    "font-size": "13px"
                                                                },
                                                            ),

                                                            html.H4(
                                                                [
                                                                    "in progress"
                                                                ],
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),
                                                        ],
                                                        className=f"border-success border-start border-3",
                                                    ),
                                                    className="text-center text-nowrap my-1 p-1",
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    html.Div(
                                                        [
                                                            html.H4(
                                                                [
                                                                    # html.Img(
                                                                    #    src="/assets/time-management.png",
                                                                    #    height=25,
                                                                    #    className="me-1",
                                                                    # ),
                                                                    "Monte Carlo How Many",
                                                                ],
                                                                style={
                                                                    "font-size": "15px"
                                                                },
                                                            ),
                                                            html.H4(
                                                                dmc.Title(id="mt_card", order=2),
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),
                                                            html.H4(
                                                                "can be completed in",
                                                                style={
                                                                    "font-size": "12px"
                                                                },
                                                            ),
                                                            html.H5(
                                                                [
                                                                    f"{round(30, 2)} days with a certainty of 85%"
                                                                ],
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),
                                                        ],
                                                        className=f"border-warning border-start border-3",
                                                    ),
                                                    className="text-center text-nowrap my-1 p-1",
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    html.Div(
                                                        [
                                                            html.H4(
                                                                [
                                                                    # html.Img(
                                                                    #    src="/assets/performance.png",
                                                                    #    height=25,
                                                                    #    className="me-1",
                                                                    # ),
                                                                    "Flow Efficiency",
                                                                ],
                                                                style={
                                                                    "font-size": "15px"
                                                                },
                                                            ),
                                                            html.H4(
                                                                [dmc.Title(id="fe_card", order=2)],
                                                                className=f"text-{color}",
                                                                style={
                                                                    "font-size": "20px"
                                                                },

                                                            ),

                                                            html.H5(
                                                                [

                                                                    "Overall"

                                                                ],
                                                                style={
                                                                    "font-size": "12px"
                                                                },
                                                            ),

                                                            html.H5(
                                                                [

                                                                    "Average"

                                                                ],
                                                                style={
                                                                    "font-size": "20px"
                                                                },
                                                            ),
                                                        ],
                                                        className=f"border-{color} border-start border-3",
                                                    ),
                                                    className="text-center text-nowrap my-1 p-1",
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                ### 3nd line ###
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.CardBody(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Card(
                                                                            [
                                                                                dbc.CardBody(
                                                                                    [
                                                                                        dbc.Row(
                                                                                            [
                                                                                                dbc.Col(
                                                                                                    html.H6(
                                                                                                        "Cycle Time",
                                                                                                        style=title_style,
                                                                                                    )
                                                                                                ),
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        dbc.Button(
                                                                                                            className="bi bi-arrows-angle-expand float-end",
                                                                                                            style=button_max_style,
                                                                                                            id="open_full_sc_ct",
                                                                                                            n_clicks=0,
                                                                                                        ),
                                                                                                        dbc.Modal(
                                                                                                            [
                                                                                                                dbc.ModalHeader(
                                                                                                                    dbc.ModalTitle(
                                                                                                                        "Cycle Time",
                                                                                                                        style=title_style_full,
                                                                                                                    )
                                                                                                                ),
                                                                                                                dbc.ModalBody(
                                                                                                                    [
                                                                                                                        dcc.Graph(
                                                                                                                            id="graph25",
                                                                                                                            className="dbc",
                                                                                                                            config=config_graph_modal,
                                                                                                                            style={
                                                                                                                                "width": "95vw",
                                                                                                                                "height": "85vh",
                                                                                                                            },
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                            ],
                                                                                                            id="modal_ct",
                                                                                                            is_open=False,
                                                                                                            fullscreen=True,
                                                                                                        ),
                                                                                                        dbc.Tooltip(
                                                                                                            "Full Screen Modal",
                                                                                                            target="open_full_sc_ct",
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        dbc.Row(
                                                                                            html.Div(
                                                                                                dcc.Graph(
                                                                                                    id="graph5",
                                                                                                    className="dbc",
                                                                                                    config=config_graph,
                                                                                                ),

                                                                                            ), style={'width': '100%',
                                                                                                      'height': '100%'}
                                                                                        ),
                                                                                    ],
                                                                                    # className="border-start border-info border-2",
                                                                                )
                                                                            ],
                                                                            style=tab_card,
                                                                        ),
                                                                    ],
                                                                    sm=12,
                                                                    md=4,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Card(
                                                                            [
                                                                                dbc.CardBody(
                                                                                    [
                                                                                        dbc.Row(
                                                                                            [
                                                                                                dbc.Col(
                                                                                                    html.H6(
                                                                                                        "Cycle Time Scatterplot",
                                                                                                        className="card-text",
                                                                                                        style=title_style,
                                                                                                    ),
                                                                                                ),
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        dbc.Button(
                                                                                                            className="bi bi-arrows-angle-expand float-end",
                                                                                                            style=button_max_style,
                                                                                                            id="open_full_scatter",
                                                                                                            n_clicks=0,
                                                                                                        ),
                                                                                                        dbc.Modal(
                                                                                                            [
                                                                                                                dbc.ModalHeader(
                                                                                                                    dbc.ModalTitle(
                                                                                                                        "Cycle Time Scatterplot",
                                                                                                                        style=title_style_full,
                                                                                                                    )
                                                                                                                ),
                                                                                                                dbc.ModalBody(
                                                                                                                    [
                                                                                                                        dcc.Graph(
                                                                                                                            id="graph27",
                                                                                                                            className="dbc",
                                                                                                                            config=config_graph_modal,
                                                                                                                            style={
                                                                                                                                "width": "95vw",
                                                                                                                                "height": "85vh",
                                                                                                                            },
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                            ],
                                                                                                            id="modal_scatter",
                                                                                                            is_open=False,
                                                                                                            fullscreen=True,
                                                                                                        ),
                                                                                                        dbc.Tooltip(
                                                                                                            "Full Screen Modal",
                                                                                                            target="open_full_scatter",
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                            ]
                                                                                        ),

                                                                                        dbc.Row(
                                                                                            html.Div(
                                                                                                dcc.Graph(
                                                                                                    id="graph7",
                                                                                                    className="dbc",
                                                                                                    config=config_graph,
                                                                                                ),

                                                                                            ), style={'width': '100%',
                                                                                                      'height': '100%'}
                                                                                        ),
                                                                                    ],
                                                                                    # className="border-start border-info border-2",
                                                                                )
                                                                            ],
                                                                            style=tab_card,
                                                                        ),
                                                                    ],
                                                                    sm=12,
                                                                    md=4,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Card(
                                                                            [
                                                                                dbc.CardBody(
                                                                                    [
                                                                                        dbc.Row(
                                                                                            [
                                                                                                dbc.Col(
                                                                                                    html.H6(
                                                                                                        "Cycle Time Histogram",
                                                                                                        className="card-text",
                                                                                                        style=title_style,
                                                                                                    ),
                                                                                                ),
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        dbc.Button(
                                                                                                            className="bi bi-arrows-angle-expand float-end",
                                                                                                            style=button_max_style,
                                                                                                            id="open_full_histogram",
                                                                                                            n_clicks=0,
                                                                                                        ),
                                                                                                        dbc.Modal(
                                                                                                            [
                                                                                                                dbc.ModalHeader(
                                                                                                                    dbc.ModalTitle(
                                                                                                                        "Cycle Time Histogram",
                                                                                                                        style=title_style_full,
                                                                                                                    )
                                                                                                                ),
                                                                                                                dbc.ModalBody(
                                                                                                                    [
                                                                                                                        dcc.Graph(
                                                                                                                            id="graph26",
                                                                                                                            className="dbc",
                                                                                                                            config=config_graph_modal,
                                                                                                                            style={
                                                                                                                                "width": "95vw",
                                                                                                                                "height": "85vh",
                                                                                                                            },
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                            ],
                                                                                                            id="modal_hst",
                                                                                                            is_open=False,
                                                                                                            fullscreen=True,
                                                                                                        ),
                                                                                                        dbc.Tooltip(
                                                                                                            "Full Screen Modal",
                                                                                                            target="open_full_histogram",
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                            ]
                                                                                        ),

                                                                                        dbc.Row(
                                                                                            html.Div(
                                                                                                dcc.Graph(
                                                                                                    id="graph6",
                                                                                                    className="dbc",
                                                                                                    config=config_graph,
                                                                                                ),

                                                                                            ),
                                                                                        ),

                                                                                    ],
                                                                                    # className="border-start border-info border-2",
                                                                                )
                                                                            ],
                                                                            style=tab_card,
                                                                        ),
                                                                    ],
                                                                    sm=12,
                                                                    md=4,
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ],
                                            sm=12,
                                            lg=12,
                                        ),
                                    ],
                                    className="g-2 my-auto",
                                    style={"margin-top": "7px"},
                                ),
                                #################################################################
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.CardBody(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Card(
                                                                            [
                                                                                dbc.CardBody(
                                                                                    [
                                                                                        dbc.Row(
                                                                                            [
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        html.H6(
                                                                                                            "Working In Progress Aging",
                                                                                                            className="card-text",
                                                                                                            style=title_style,
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        dbc.Button(
                                                                                                            className="bi bi-arrows-angle-expand float-end",
                                                                                                            style=button_max_style,
                                                                                                            id="open_full_aging",
                                                                                                            n_clicks=0,
                                                                                                        ),
                                                                                                        dbc.Modal(
                                                                                                            [
                                                                                                                dbc.ModalHeader(
                                                                                                                    dbc.ModalTitle(
                                                                                                                        "Working in Progress Aging",
                                                                                                                        style=title_style_full,
                                                                                                                    )
                                                                                                                ),
                                                                                                                dbc.ModalBody(
                                                                                                                    [
                                                                                                                        dcc.Graph(
                                                                                                                            id="graph32",
                                                                                                                            className="dbc",
                                                                                                                            config=config_graph_modal,
                                                                                                                            style={
                                                                                                                                "width": "90vw",
                                                                                                                                "height": "90vh",
                                                                                                                            },
                                                                                                                        )
                                                                                                                    ]
                                                                                                                ),
                                                                                                            ],
                                                                                                            id="modal_aging",
                                                                                                            is_open=False,
                                                                                                            fullscreen=True,
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        dcc.Graph(
                                                                                            id="graph13",
                                                                                            className="dbc",
                                                                                            config=config_graph,
                                                                                        ),
                                                                                    ],
                                                                                    # className="border-start border-info border-2",
                                                                                )
                                                                            ],
                                                                            style=tab_card,
                                                                        ),
                                                                    ],
                                                                    sm=12,
                                                                    md=4,
                                                                ),
                                                                ############################################################################
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Card(
                                                                            [
                                                                                dbc.CardBody(
                                                                                    [
                                                                                        dbc.Row(
                                                                                            [
                                                                                                dbc.Col(
                                                                                                    html.H6(
                                                                                                        "Cumulative Flow",
                                                                                                        className="card-text",
                                                                                                        style=title_style,
                                                                                                    )
                                                                                                ),
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        dbc.Button(
                                                                                                            className="bi bi-arrows-angle-expand float-end",
                                                                                                            style=button_max_style,
                                                                                                            id="open_full_cfd",
                                                                                                            n_clicks=0,
                                                                                                        ),
                                                                                                        dbc.Modal(
                                                                                                            [
                                                                                                                dbc.ModalHeader(
                                                                                                                    dbc.ModalTitle(
                                                                                                                        [
                                                                                                                            dbc.Row(
                                                                                                                                [
                                                                                                                                    dbc.Col(
                                                                                                                                        [
                                                                                                                                            html.H6(
                                                                                                                                                "Cumulative Flow",
                                                                                                                                                style=title_style_full,
                                                                                                                                            )
                                                                                                                                        ]
                                                                                                                                    ),
                                                                                                                                ]
                                                                                                                            ),
                                                                                                                        ]
                                                                                                                    )
                                                                                                                ),
                                                                                                                dbc.ModalBody(
                                                                                                                    [
                                                                                                                        dbc.Row(
                                                                                                                            [
                                                                                                                                dbc.Col(
                                                                                                                                    [
                                                                                                                                        dbc.Button(
                                                                                                                                            className="bi bi-file-bar-graph-fill",
                                                                                                                                            style=button_max_style,
                                                                                                                                            id="open_full_cfd_category",
                                                                                                                                            n_clicks=0,
                                                                                                                                        ),
                                                                                                                                        dbc.Modal(
                                                                                                                                            [
                                                                                                                                                dbc.ModalHeader(
                                                                                                                                                    dbc.ModalTitle(
                                                                                                                                                        "Category",
                                                                                                                                                        style=title_style_full,
                                                                                                                                                    )
                                                                                                                                                ),
                                                                                                                                                dbc.ModalBody(
                                                                                                                                                    [
                                                                                                                                                        dcc.Graph(
                                                                                                                                                            id="graph9",
                                                                                                                                                            className="dbc",
                                                                                                                                                            config=config_graph_modal,
                                                                                                                                                            style={
                                                                                                                                                                "width": "55vw",
                                                                                                                                                                "height": "50vh",
                                                                                                                                                            },
                                                                                                                                                        )
                                                                                                                                                    ]
                                                                                                                                                ),
                                                                                                                                            ],
                                                                                                                                            id="modal-xl",
                                                                                                                                            size="xl",
                                                                                                                                            is_open=False,
                                                                                                                                        ),
                                                                                                                                    ]
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                        dbc.Row(
                                                                                                                            [
                                                                                                                                dbc.Col(
                                                                                                                                    [
                                                                                                                                        dcc.Graph(
                                                                                                                                            id="graph29",
                                                                                                                                            className="dbc",
                                                                                                                                            config=config_graph_modal,
                                                                                                                                            style={
                                                                                                                                                "width": "90vw",
                                                                                                                                                "height": "90vh",
                                                                                                                                            },
                                                                                                                                        ),
                                                                                                                                    ]
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                                dbc.ModalFooter(
                                                                                                                    dbc.Button(
                                                                                                                        "Close",
                                                                                                                        id="close",
                                                                                                                        className="ms-auto",
                                                                                                                        n_clicks=0,
                                                                                                                    )
                                                                                                                ),
                                                                                                            ],
                                                                                                            id="modal_cfd",
                                                                                                            is_open=False,
                                                                                                            fullscreen=True,
                                                                                                        ),
                                                                                                        dbc.Tooltip(
                                                                                                            "Full Screen Modal",
                                                                                                            target="open_full_cfd",
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        dcc.Graph(
                                                                                            id="graph10",
                                                                                            className="dbc",
                                                                                            config=config_graph,
                                                                                        ),
                                                                                    ],
                                                                                    # className="border-start border-info border-2",
                                                                                )
                                                                            ],
                                                                            style=tab_card,
                                                                        ),
                                                                    ],
                                                                    sm=12,
                                                                    md=4,
                                                                ),
                                                                ############################################################################
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Card(
                                                                            [
                                                                                dbc.CardBody(
                                                                                    [
                                                                                        dbc.Row(
                                                                                            [
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        html.H6(
                                                                                                            "Throughput per week",
                                                                                                            style=title_style,
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                                dbc.Col(
                                                                                                    [
                                                                                                        dbc.Button(
                                                                                                            className="bi bi-arrows-angle-expand float-end",
                                                                                                            style=button_max_style,
                                                                                                            id="open_full_tpw",
                                                                                                            n_clicks=0,
                                                                                                        ),
                                                                                                        dbc.Modal(
                                                                                                            [
                                                                                                                dbc.ModalHeader(
                                                                                                                    dbc.ModalTitle(
                                                                                                                        "Throughput per week",
                                                                                                                        style=title_style_full,
                                                                                                                    )
                                                                                                                ),
                                                                                                                dbc.ModalBody(
                                                                                                                    [
                                                                                                                        dcc.Graph(
                                                                                                                            id="graph33",
                                                                                                                            className="dbc",
                                                                                                                            config=config_graph,
                                                                                                                            style={
                                                                                                                                "width": "90vw",
                                                                                                                                "height": "45vh",
                                                                                                                            },
                                                                                                                        ),
                                                                                                                        dcc.Graph(
                                                                                                                            id="graph4_tp_avg",
                                                                                                                            className="dbc",
                                                                                                                            config=config_graph,
                                                                                                                            style={
                                                                                                                                "width": "95vw",
                                                                                                                                "height": "45vh",
                                                                                                                            },
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                            ],
                                                                                                            id="modal_tpw",
                                                                                                            is_open=False,
                                                                                                            fullscreen=True,
                                                                                                        ),
                                                                                                    ]
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                        dcc.Graph(
                                                                                            id="graph3_tp_week",
                                                                                            className="dbc",
                                                                                            config=config_graph,
                                                                                        ),
                                                                                    ],
                                                                                    # className="border-start border-info border-2",
                                                                                )
                                                                            ],
                                                                            style=tab_card,
                                                                        ),
                                                                    ],
                                                                    sm=12,
                                                                    md=4,
                                                                ),
                                                                ############################################################################
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ],
                                            sm=12,
                                            lg=12,
                                        ),
                                    ],
                                    className="g-2 my-auto",
                                    style={"margin-top": "7px"},
                                ),
                                ##############################################################################
                                dbc.Row(
                                    [
                                        dbc.Accordion(
                                            [
                                                dbc.AccordionItem(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            [
                                                                                                dbc.Card(
                                                                                                    [
                                                                                                        dbc.CardBody(
                                                                                                            [
                                                                                                                dbc.Row(
                                                                                                                    [
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                html.H6(
                                                                                                                                    "Monte Carlo Simulation",
                                                                                                                                    style=title_style,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                dbc.Button(
                                                                                                                                    className="bi bi-arrows-angle-expand float-end",
                                                                                                                                    style=button_max_style,
                                                                                                                                    id="open_full_mc1",
                                                                                                                                    n_clicks=0,
                                                                                                                                ),
                                                                                                                                dbc.Modal(
                                                                                                                                    [
                                                                                                                                        dbc.ModalHeader(
                                                                                                                                            dbc.ModalTitle(
                                                                                                                                                "Monte Carlo Simulation",
                                                                                                                                                style=title_style_full,
                                                                                                                                            )
                                                                                                                                        ),
                                                                                                                                        dbc.ModalBody(
                                                                                                                                            [
                                                                                                                                                dcc.Graph(
                                                                                                                                                    id="graph43",
                                                                                                                                                    className="dbc",
                                                                                                                                                    config=config_graph,
                                                                                                                                                    style={
                                                                                                                                                        "width": "90vw",
                                                                                                                                                        "height": "90vh",
                                                                                                                                                    },
                                                                                                                                                )
                                                                                                                                            ]
                                                                                                                                        ),
                                                                                                                                    ],
                                                                                                                                    id="modal_mc1",
                                                                                                                                    is_open=False,
                                                                                                                                    fullscreen=True,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                                dcc.Graph(
                                                                                                                    id="graph14",
                                                                                                                    className="dbc",
                                                                                                                    config=config_graph,
                                                                                                                ),
                                                                                                            ],
                                                                                                            # className="border-start border-info border-2",
                                                                                                        )
                                                                                                    ],
                                                                                                    style=tab_card,
                                                                                                ),
                                                                                            ],
                                                                                            sm=12,
                                                                                            md=6,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            [
                                                                                                dbc.Card(
                                                                                                    [
                                                                                                        dbc.CardBody(
                                                                                                            [
                                                                                                                dbc.Row(
                                                                                                                    [
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                html.H6(
                                                                                                                                    "Monte Carlo Simulation Items",
                                                                                                                                    className="card-text",
                                                                                                                                    style=title_style,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                dbc.Button(
                                                                                                                                    className="bi bi-arrows-angle-expand float-end",
                                                                                                                                    style=button_max_style,
                                                                                                                                    id="open_full_mc2",
                                                                                                                                    n_clicks=0,
                                                                                                                                ),
                                                                                                                                dbc.Modal(
                                                                                                                                    [
                                                                                                                                        dbc.ModalHeader(
                                                                                                                                            dbc.ModalTitle(
                                                                                                                                                "Monte Carlo Simulation Items",
                                                                                                                                                style=title_style_full,
                                                                                                                                            )
                                                                                                                                        ),
                                                                                                                                        dbc.ModalBody(
                                                                                                                                            [
                                                                                                                                                dcc.Graph(
                                                                                                                                                    id="graph44",
                                                                                                                                                    className="dbc",
                                                                                                                                                    config=config_graph,
                                                                                                                                                    style={
                                                                                                                                                        "width": "90vw",
                                                                                                                                                        "height": "90vh",
                                                                                                                                                    },
                                                                                                                                                )
                                                                                                                                            ]
                                                                                                                                        ),
                                                                                                                                    ],
                                                                                                                                    id="modal_mc2",
                                                                                                                                    is_open=False,
                                                                                                                                    fullscreen=True,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                                dcc.Graph(
                                                                                                                    id="graph15",
                                                                                                                    className="dbc",
                                                                                                                    config=config_graph,
                                                                                                                ),
                                                                                                            ],
                                                                                                            # className="border-start border-info border-2",
                                                                                                        )
                                                                                                    ],
                                                                                                    style=tab_card,
                                                                                                ),
                                                                                            ],
                                                                                            sm=12,
                                                                                            md=6,
                                                                                        ),
                                                                                    ]
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ],
                                                                    sm=12,
                                                                    lg=12,
                                                                ),
                                                            ],
                                                            className="g-2 my-auto",
                                                            style={
                                                                "margin-top": "7px"
                                                            },
                                                        ),
                                                    ],
                                                    title="Montecarlo Simulation",
                                                ),
                                                dbc.AccordionItem(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            [
                                                                                                dbc.Card(
                                                                                                    [
                                                                                                        dbc.CardBody(
                                                                                                            [
                                                                                                                dbc.Row(
                                                                                                                    [
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                html.H6(
                                                                                                                                    "% Issue Points",
                                                                                                                                    className="card-text",
                                                                                                                                    style=title_style,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                dbc.Button(
                                                                                                                                    className="bi bi-arrows-angle-expand float-end",
                                                                                                                                    style=button_max_style,
                                                                                                                                    id="open_full_pip",
                                                                                                                                    n_clicks=0,
                                                                                                                                ),
                                                                                                                                dbc.Modal(
                                                                                                                                    [
                                                                                                                                        dbc.ModalHeader(
                                                                                                                                            dbc.ModalTitle(
                                                                                                                                                "% Issue Points",
                                                                                                                                                style=title_style_full,
                                                                                                                                            )
                                                                                                                                        ),
                                                                                                                                        dbc.ModalBody(
                                                                                                                                            [
                                                                                                                                                dbc.Row(
                                                                                                                                                    [
                                                                                                                                                        dbc.Col(
                                                                                                                                                            dcc.Graph(
                                                                                                                                                                id="graph2_issue_points",
                                                                                                                                                                className="dbc",
                                                                                                                                                                responsive=True,
                                                                                                                                                                config=config_graph_modal,
                                                                                                                                                                style={
                                                                                                                                                                    "width": "45vw",
                                                                                                                                                                    "height": "60vh",
                                                                                                                                                                },
                                                                                                                                                            ),
                                                                                                                                                        ),
                                                                                                                                                        dbc.Col(
                                                                                                                                                            dcc.Graph(
                                                                                                                                                                id="graph21",
                                                                                                                                                                className="dbc",
                                                                                                                                                                responsive=True,
                                                                                                                                                                config=config_graph_modal,
                                                                                                                                                                style={
                                                                                                                                                                    "width": "45vw",
                                                                                                                                                                    "height": "60vh",
                                                                                                                                                                },
                                                                                                                                                            )
                                                                                                                                                        ),
                                                                                                                                                    ]
                                                                                                                                                ),
                                                                                                                                            ]
                                                                                                                                        ),
                                                                                                                                    ],
                                                                                                                                    id="modal_pip",
                                                                                                                                    is_open=False,
                                                                                                                                    fullscreen=True,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                                dcc.Graph(
                                                                                                                    id="graph1_issue_type",
                                                                                                                    className="dbc",
                                                                                                                    config=config_graph,
                                                                                                                ),
                                                                                                            ],
                                                                                                            # className="border-start border-info border-2",
                                                                                                        )
                                                                                                    ],
                                                                                                    style=tab_card,
                                                                                                ),
                                                                                            ],
                                                                                            sm=12,
                                                                                            md=4,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            [
                                                                                                dbc.Card(
                                                                                                    [
                                                                                                        dbc.CardBody(
                                                                                                            [
                                                                                                                dbc.Row(
                                                                                                                    [
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                html.H6(
                                                                                                                                    "Cycle Time x Points",
                                                                                                                                    className="card-text",
                                                                                                                                    style=title_style,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                dbc.Button(
                                                                                                                                    className="bi bi-arrows-angle-expand float-end",
                                                                                                                                    style=button_max_style,
                                                                                                                                    id="open_full_ctp",
                                                                                                                                    n_clicks=0,
                                                                                                                                ),
                                                                                                                                dbc.Modal(
                                                                                                                                    [
                                                                                                                                        dbc.ModalHeader(
                                                                                                                                            dbc.ModalTitle(
                                                                                                                                                "Cycle Time x Points",
                                                                                                                                                style=title_style_full,
                                                                                                                                            )
                                                                                                                                        ),
                                                                                                                                        dbc.ModalBody(
                                                                                                                                            [
                                                                                                                                                dcc.Graph(
                                                                                                                                                    id="graph22",
                                                                                                                                                    className="dbc",
                                                                                                                                                    config=config_graph_modal,
                                                                                                                                                )
                                                                                                                                            ]
                                                                                                                                        ),
                                                                                                                                    ],
                                                                                                                                    id="modal_ctp",
                                                                                                                                    is_open=False,
                                                                                                                                    fullscreen=True,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                                dcc.Graph(
                                                                                                                    id="graph12",
                                                                                                                    className="dbc",
                                                                                                                    config=config_graph,
                                                                                                                ),
                                                                                                            ],
                                                                                                            # className="border-start border-info border-2",
                                                                                                        )
                                                                                                    ],
                                                                                                    style=tab_card,
                                                                                                ),
                                                                                            ],
                                                                                            sm=12,
                                                                                            md=4,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            [
                                                                                                dbc.Card(
                                                                                                    [
                                                                                                        dbc.CardBody(
                                                                                                            [
                                                                                                                dbc.Row(
                                                                                                                    [
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                html.H6(
                                                                                                                                    "Cycle Time and Story Points",
                                                                                                                                    className="card-text",
                                                                                                                                    style=title_style,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                        dbc.Col(
                                                                                                                            [
                                                                                                                                dbc.Button(
                                                                                                                                    className="bi bi-arrows-angle-expand float-end",
                                                                                                                                    style=button_max_style,
                                                                                                                                    id="open_full_ctb",
                                                                                                                                    n_clicks=0,
                                                                                                                                ),
                                                                                                                                dbc.Modal(
                                                                                                                                    [
                                                                                                                                        dbc.ModalHeader(
                                                                                                                                            dbc.ModalTitle(
                                                                                                                                                "Cycle Time and Story Points",
                                                                                                                                                style=title_style_full,
                                                                                                                                            )
                                                                                                                                        ),
                                                                                                                                        dbc.ModalBody(
                                                                                                                                            [
                                                                                                                                                dcc.Graph(
                                                                                                                                                    id="graph20",
                                                                                                                                                    className="dbc",
                                                                                                                                                    config=config_graph_modal,
                                                                                                                                                    style={
                                                                                                                                                        "width": "55vw",
                                                                                                                                                        "height": "50vh",
                                                                                                                                                    },
                                                                                                                                                )
                                                                                                                                            ]
                                                                                                                                        ),
                                                                                                                                    ],
                                                                                                                                    id="modal_ctb",
                                                                                                                                    is_open=False,
                                                                                                                                    fullscreen=True,
                                                                                                                                ),
                                                                                                                            ]
                                                                                                                        ),
                                                                                                                    ]
                                                                                                                ),
                                                                                                                dcc.Graph(
                                                                                                                    id="graph11_points_ct",
                                                                                                                    className="dbc",
                                                                                                                    config=config_graph,
                                                                                                                ),
                                                                                                            ],
                                                                                                            # className="border-start border-info border-2",
                                                                                                        )
                                                                                                    ],
                                                                                                    style=tab_card,
                                                                                                ),
                                                                                            ],
                                                                                            sm=12,
                                                                                            md=4,
                                                                                        ),
                                                                                    ]
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ],
                                                                    sm=12,
                                                                    lg=12,
                                                                ),
                                                            ],
                                                            className="g-2 my-auto",
                                                            style={
                                                                "margin-top": "7px"
                                                            },
                                                        ),
                                                    ],
                                                    title="Points",
                                                ),
                                            ],
                                            start_collapsed=True,
                                        ),
                                    ],
                                    className="g-2 my-auto",
                                    style={"margin-top": "7px"},
                                ),
                                dbc.Row([
                                    html.Br(),
                                    html.Br(),
                                    html.Br(),
                                ]),

                            ], style={
                                "background-color": "#ffffff",
                                "width": "100%",
                                "margin": "0",
                                "maxWidth": "100%",
                                "overflow": "hidden",
                                "flexShrink": "1",
                            }

                        ),

                        html.Div(
                            dbc.Container(
                                [
                                    dmc.Footer(
                                        height=30,
                                        fixed=True,
                                        children=[],
                                        style={"backgroundColor": "#ffffff"},
                                    )
                                ]
                            )
                        ),
                    ],
                    id="page-container",
                    p=0,
                    fluid=True,
                    style={
                        "background-color": "#f4f6f9",
                        "width": "100%",
                        "margin": "0",
                        "maxWidth": "100%",
                        "overflow": "hidden",
                        "flexShrink": "1",
                    },
                ),
            ],
            size="100%",
            p=0,
            m=0,
            style={"display": "flex", "maxWidth": "100vw", "overflow": "hidden"},
        ),
        html.Div(),
    ],
)


# =============== CAll BACKS ============== #


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


@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


### Callback to full screen Modal ###

def toggle_modal_total(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open


def toggle_modal_full(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


app.callback(
    Output("modal_ct", "is_open", allow_duplicate=True),
    Input("open_full_sc_ct", "n_clicks"),
    Input("close", "n_clicks"),
    Input("link_Average", "n_clicks"),
    [State("modal_ct", "is_open")],
    prevent_initial_call=True
)(toggle_modal_total)

app.callback(
    Output("modal_hst", "is_open", allow_duplicate=True),
    Input("open_full_histogram", "n_clicks"),
    Input("close", "n_clicks"),
    Input("link_Histogram", "n_clicks"),
    [State("modal_hst", "is_open")],
    prevent_initial_call=True
)(toggle_modal_total)

app.callback(
    Output("modal_scatter", "is_open", allow_duplicate=True),
    Input("open_full_scatter", "n_clicks"),
    Input("close", "n_clicks"),
    Input("link_Scatterplot", "n_clicks"),
    [State("modal_scatter", "is_open")],
    prevent_initial_call=True
)(toggle_modal_total)

app.callback(
    Output("modal_cfd", "is_open", allow_duplicate=True),
    Input("open_full_cfd", "n_clicks"),
    Input("close", "n_clicks"),
    Input("link_CFD", "n_clicks"),
    [State("modal_cfd", "is_open")],
    prevent_initial_call=True
)(toggle_modal_total)

app.callback(
    Output("modal-xl", "is_open"),
    Input("open_full_cfd_category", "n_clicks"),
    State("modal-xl", "is_open"),
)(toggle_modal)

app.callback(
    Output("modal_aging", "is_open"),
    Input("open_full_aging", "n_clicks"),
    Input("link_Aging", "n_clicks"),
    State("modal_aging", "is_open"),
)(toggle_modal_full)

app.callback(
    Output("modal_tpw", "is_open"),
    Input("open_full_tpw", "n_clicks"),
    Input("link_tp_week", "n_clicks"),
    State("modal_tpw", "is_open"),
)(toggle_modal_full)

app.callback(
    Output("modal_mc1", "is_open"),
    Input("open_full_mc1", "n_clicks"),
    Input("link_MC_Many", "n_clicks"),
    State("modal_mc1", "is_open"),
)(toggle_modal_full)

app.callback(
    Output("modal_mc2", "is_open"),
    Input("open_full_mc2", "n_clicks"),
    Input("link_MC_Much", "n_clicks"),
    State("modal_mc2", "is_open"),
)(toggle_modal_full)

app.callback(
    Output("modal_pip", "is_open"),
    Input("open_full_pip", "n_clicks"),
    Input("link_Percent", "n_clicks"),
    State("modal_pip", "is_open"),
)(toggle_modal_full)

app.callback(
    Output("modal_ctp", "is_open"),
    Input("open_full_ctp", "n_clicks"),
    Input("link_Points_CT", "n_clicks"),
    State("modal_ctp", "is_open"),
)(toggle_modal_full)

app.callback(
    Output("modal_ctb", "is_open"),
    Input("open_full_ctb", "n_clicks"),
    Input("link_Correlation", "n_clicks"),
    State("modal_ctb", "is_open"),
)(toggle_modal_full)


#### Callback Mantine #####
@app.callback(
    Output("sidebar", "width"),
    Input("sidebar-button", "n_clicks"),
    State("sidebar", "width"),
    prevent_initial_call=True,
)
def drawer_demo(n, width):
    if n:
        if width["base"] == 300:
            return {"base": 70}
        else:
            return {"base": 300}
    else:
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output("drawer-simple", "opened"),
    Input("drawer-demo-button", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_dem(n_clicks):
    return True


### Callback list status ###

@app.callback(Output("checkbox-group-output", "children"),
              [Input("framework-multi-select", "value"), Input("checkbox-group", "value")]
              )
def checkbox(projects, value):
    print(projects)
    print(value)
    if value is not None:
        for v in value:
            status.update_csv("PRJ", v, False, status_file_path)
            print(value) 
        return ", ".join(value) if value else None        
    


@app.callback(Output("checkbox-group-output_wait", "children"), Input("checkbox-group_wait", "value"))
def checkbox_wait(value):
    return ", ".join(value) if value else None



@app.callback(Output('status_msg', 'children'), [Input("status-order", "n_clicks"), Input("checkbox-group", "value")])
def update_status_order(n_clicks, value):
    print(value)
    print(n_clicks)    
    if value is not None and n_clicks is not None:
        status.delete_from_csv("PRJ",status_file_path)
        status.save_to_csv("PRJ", value, status_file_path)
        status_list_display = html.Ul([html.Li(i) for i in value])
        return [html.P("List Updated successfull"), status_list_display]


  
@app.callback(
    Output('status_wait_alert', 'children'),
    [Input("status-wait", "n_clicks")],
    [State("checkbox-group_wait", "value")]
)
def update_status_wait(n_clicks, selected_statuses):
    if n_clicks is None or selected_statuses is None:
        raise dash.exceptions.PreventUpdate

    try:
        df_status = pd.read_csv(status_file_path)
        
        # Primeiro, defina todos os 'wait_status' como False para o projeto
        df_status.loc[df_status['project_key'] == 'PRJ', 'wait_status'] = False
        
        # Em seguida, defina como True apenas os status selecionados
        df_status.loc[(df_status['project_key'] == 'PRJ') & (df_status['status_name'].isin(selected_statuses)), 'wait_status'] = True
        
        df_status.to_csv(status_file_path, index=False)
        
        return f"Wait statuses updated successfully for: {', '.join(selected_statuses)}"
    except Exception as e:
        return f"An error occurred: {e}"

  

### Callback graphs ###
@app.callback(
    Output("graph1_issue_type", "figure"),
    Output("graph2_issue_points", "figure"),
    Output("graph3_tp_week", "figure"),
    Output("graph4_tp_avg", "figure"),
    Output("graph5", "figure"),
    Output("graph6", "figure"),
    Output("graph7", "figure"),
    Output("graph9", "figure"),
    Output("graph10", "figure"),
    Output("graph11_points_ct", "figure"),
    Output("graph12", "figure"),
    Output("graph13", "figure"),
    Output("graph14", "figure"),
    Output("graph15", "figure"),
    Output("graph20", "figure"),
    Output("graph21", "figure"),
    Output("graph22", "figure"),
    Output("graph25", "figure"),
    Output("graph26", "figure"),
    Output("graph27", "figure"),
    Output("graph29", "figure"),
    Output("graph32", "figure"),
    Output("graph33", "figure"),
    Output("graph43", "figure"),
    Output("graph44", "figure"),
    Output("ct85", "children"),
    Output("wip_card", "children"),
    Output("mt_card", "children"),
    Input("date-picker-select", "start_date"),
    Input("date-picker-select", "end_date"),
    Input("input_tries", "value"),
    Input("input_loops", "value"),
    Input("input_simulation_tries", "value"),
    Input("input_days", "value"),
    Input("framework-multi-select", "value"),
    [Input("issue-type-select", "value")],
    prevent_initial_call=True
)
def graph_issue(
        dateStart,
        dateEnd,
        simulation_items,
        loops_days,
        simulation_loops,
        last_days,
        project_keys,
        issue_type,
):
    SIMULATION_DAYS = loops_days  # N
    SIMULATION_ITEMS = simulation_items  # N
    SIMULATIONS = simulation_loops
    LAST_DAYS = last_days
    PROJECTS = project_keys

    # OMIT_ISSUE_TYPES = ('Epic',)
    OMIT_ISSUE_TYPES = issue_type
    EXCLUDE_WEEKENDS = True

    FILTER_ISSUES_SINCE = dateStart
    FILTER_ISSUES_UNTIL = dateEnd

    print("SIMULATION_DAYS" + str(SIMULATION_DAYS))
    print("SIMULATION_ITEMS" + str(SIMULATION_ITEMS))  
    print("SIMULATIONS" + str(SIMULATIONS))
    print("LAST_DAYS" + str(LAST_DAYS))
    print("PROJECTS" + str(PROJECTS))
    print("SIMULATION_DAYS" + str(SIMULATION_DAYS))
    
    print("OMIT_ISSUE_TYPES" + str(OMIT_ISSUE_TYPES))
    print("EXCLUDE_WEEKENDS" + str(EXCLUDE_WEEKENDS))
    print("FILTER_ISSUES_SINCE" + str(FILTER_ISSUES_SINCE))
    print("FILTER_ISSUES_UNTIL" + str(FILTER_ISSUES_UNTIL))


    
    ### read data ###
    print("read data")
    data, dupes, filtered = analysis.read_data(
        DATA_FILE,
        exclude_types=OMIT_ISSUE_TYPES,
        since=FILTER_ISSUES_SINCE,
        until=FILTER_ISSUES_UNTIL,
        projects=PROJECTS,
    )
    print("process issue data")
    ### process issue data ###
    issue_data, (categories, *extra) = analysis.process_issue_data(
        data, exclude_weekends=EXCLUDE_WEEKENDS
    )
    print("calculate cycle data")
    ### calculate cycle data ###
    cycle_data = analysis.process_cycle_data(issue_data)
    cycle_data = cycle_data.reset_index()
    print("calculate throughput data")
    ### calculate Throughput per week ###
    throughput, throughput_per_week = analysis.process_throughput_data(
        issue_data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
    )
    print("calculate work in progress")
    ### calculate work in progress ###
    wip, _ = analysis.process_wip_data(
        issue_data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
    )
    wip = wip.reset_index()
    wip_melted = pd.melt(wip, ["Date"])
    wip_melted["value"] = wip_melted["value"].astype(float)
    
    print("calcuate aging tickets")
    ### calculate aging tickets ###
    age_data = analysis.process_wip_age_data(
        issue_data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
    )
    wip_inp = age_data['Stage'].count()
    wip_inp = str(wip_inp) + " Items"

    print("monte carlo simulations")
    ### Monte carlo distribution items and days
    print("Distribution How Long Items")
    print(throughput)
    print("Sumulações:" + str(SIMULATIONS))
    print(LAST_DAYS)
    
    distribution_when, samples = analysis.forecast_montecarlo_how_long_items(
         throughput, items=SIMULATION_ITEMS, simulations=SIMULATIONS, window=LAST_DAYS
     )
    print("Distribution How Many Items")
    distribution_how, samples_how = analysis.forecast_montecarlo_how_many_items(throughput, days=SIMULATION_DAYS,
                                                                                 simulations=SIMULATIONS,
                                                                                 window=LAST_DAYS)

    ## Figure 1 ##
    fig = px.pie(
        issue_data,
        values="issue_points",
        names="issue_points",
        color="issue_points",
        color_discrete_map={
            "Bug": "red",
            "Task": "blue",
            "Story": "green",
            "Epic": "purple",
        },
    )

    fig.update_layout(
        margin=dict(l=15, r=15, t=20, b=15),
    )
    fig.update_layout(showlegend=True)

    fig21 = go.Figure(fig)

    ## Figure 2 ##
    issue_type_count = issue_data.groupby("issue_type").count()
    itc = issue_type_count
    itc_aux = itc.reset_index()

    fig2 = px.pie(itc_aux, values="issue_points", width=800, height=700)

    fig2.update_layout(
        margin=dict(l=15, r=15, t=20, b=15),
    )

    ###################################################################

    wip_avg = "{:.2f}".format(wip["Average"].max())

    fig3 = px.histogram(throughput_per_week, x="Throughput", nbins=20).update_layout(
        xaxis_title="Throughput (per week)", yaxis_title="Frequency"
    )
    fig3.update_layout(
        xaxis=dict(
            dtick=(1),
            tickfont=dict(size=10),
        )
    )

    fig3.update_layout(
        yaxis=dict(
            dtick=(1),
            tickfont=dict(size=10),
        )
    )

    fig3.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )

    fig33 = go.Figure(fig3)

    fig3.update_layout(xaxis_title=None, yaxis_title=None)

    cy = float(wip_avg)

    throughput_per_week_aux = throughput_per_week.reset_index()
    throughput_annotation_text = throughput_per_week_aux["Average"].max()

    fig4 = px.line(
        throughput_per_week_aux,
        x="Date",
        y=["Throughput", "Moving Average (4 weeks)", "Average"],
    )

    fig4.update_layout(xaxis=dict(dtick=(86400000.0 * 7), tickformat="%d %B %Y"))

    fig4.add_scatter(
        x=[throughput_per_week_aux["Date"].max()],
        y=[throughput_per_week_aux["Average"].max()],
        marker=dict(color="green", size=30),
        name="Median",
        text=throughput_annotation_text,
        mode="lines+text",
    ).update_layout(xaxis_title="Week", yaxis_title="Items Completed")

    # Figure 5  ################################################################
    # aux_tittle = "Cycle Time Since..: {}".format(FILTER_ISSUES_SINCE)
    average_annotation_text = "{:.2f}".format(cycle_data["Average"].max())

    fig5 = px.line(
        cycle_data,
        x="Complete Date",
        y=["Cycle Time", "Moving Average (10 items)", "Average"],
    )

    fig5.update_layout(
        xaxis=dict(
            dtick=(86400000.0 * 7),
            tickformat="%d %b",
            tickfont=dict(size=10),
        )
    )

    fig5.add_scatter(
        x=[cycle_data["Complete Date"].max()],
        y=[cycle_data["Average"].max()],
        marker=dict(color="green", size=10),
        name="Median",
        text=average_annotation_text,
        mode="lines+text",
    )

    fig5.update_layout(
        font=dict(size=10),
        legend=dict(
            yanchor="top",
            y=0.90,
            xanchor="left",
            x=0.05,
        ),
    )

    fig5.update_layout(
        {
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    fig5.update_xaxes(showgrid=False, zeroline=False)
    fig5.update_yaxes(showgrid=True, zeroline=True)
    fig5.update_layout(showlegend=True)
    fig5.update_layout(xaxis_title="Complete date", yaxis_title="Cycle Time")

    fig25 = go.Figure(fig5)

    fig5.update_layout(
        margin=dict(l=15, r=15, t=15, b=15),
    )

    fig5.update_layout(yaxis_title=None, xaxis_title=None)

    # Figure 6 ################################################################
    # histogram_title = "Cycle Time Histogram Since {}".format(FILTER_ISSUES_SINCE)
    fig6 = px.histogram(cycle_data, x="Cycle Time", nbins=20).update_layout(
        xaxis_title="Days", yaxis_title="Frequency"
    )
    fig6.update_layout(
        xaxis=dict(
            dtick=(2),
            tickfont=dict(size=10),
        )
    )
    fig6.update_layout(
        yaxis=dict(
            dtick=(5),
            tickfont=dict(size=10),
        )
    )

    fig6.update_xaxes(tickangle=0)

    fig26 = go.Figure(fig6)

    fig6.update_layout(
        margin=dict(l=15, r=15, t=15, b=15),
    )

    fig6.update_layout(yaxis_title=None, xaxis_title=None)

    # Figure 7 ###########################################################
    for v in (0.25, 0.5, 0.75, 0.85, 0.95):
        pertencil = cycle_data["Cycle Time"].quantile(v)
        perc = pertencil
        valor = " (" + "{:.2f}".format(pertencil) + ")"

    # scatter_title = "Cycle Time Scatterplot..: " + FILTER_ISSUES_SINCE + " and " + FILTER_ISSUES_UNTIL
    df = cycle_data
    fig7 = px.scatter(
        df, x="Complete Date", y=["Cycle Time", "Issue Type"], color="Issue Type"
    ).update_layout(yaxis_title="Cycle Time")

    for v in (0.25, 0.5, 0.75, 0.85, 0.95):
        pertencil = cycle_data["Cycle Time"].quantile(v)
        valor = " (" + "{:.2f}".format(pertencil) + ")"
        textPlot = str("{:.2f}".format(v * 100)) + str("%") + str(valor)

        fig7.add_hline(y=pertencil, line_width=0.5, line_dash="dash", line_color="blue")

        fig7.add_scatter(
            x=[cycle_data["Complete Date"].max()],
            y=[pertencil],
            name=textPlot,
            text=textPlot,
            mode="lines+text",
            marker_size=10,
        ).update_traces(
            textposition="top left", textfont_size=10, textfont_color="blue"
        )

    ct_percentil = round(cycle_data["Cycle Time"].quantile(0.85))
    ct_85 = str(ct_percentil) + " Days or Less"

    fig7.update_layout(
        xaxis=dict(dtick=(86400000.0 * 7), tickformat="%d %b", tickfont=dict(size=10))
    )

    fig7.update_xaxes(tickangle=45)

    fig7.update_layout(showlegend=False)

    fig27 = go.Figure(fig7)

    fig27.update_layout(showlegend=True)

    fig7.update_layout(
        margin=dict(l=15, r=5, t=15, b=15),
    )
    fig7.update_layout(xaxis_title=None, yaxis_title=None)

    # ############## CFD ############ #
    f = analysis.process_flow_category_data(
        data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
    )

    f.reset_index()
    fig8 = px.area(f, y=["Done", "In Progress", "To Do"]).update_layout(
        xaxis_title="Timeline", yaxis_title="Items", height=500
    )

    fig8.update_layout(
        xaxis=dict(dtick=(86400000.0 * 3), tickformat="%d %b", tickfont=dict(size=10))
    )

    fig8.update_layout(xaxis_title="", yaxis_title="")

    ##############################################################################################
    f = analysis.process_flow_data(
        data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
    )
    my_list = STATUS_ORDER
    for item in my_list.copy():
        try  :
            if not (item in f):
                my_list.remove(item)
        except:
            print("Error processing item: " + str(item))

    STATUS_LISTA_AUX = my_list
    print("lista de status no callback")
    print(STATUS_LISTA_AUX)

    f = analysis.process_flow_data(
        data, since=FILTER_ISSUES_SINCE, until=FILTER_ISSUES_UNTIL
    )
    f.reset_index()

    fig9 = px.area(f, y=STATUS_LISTA_AUX).update_layout(
        xaxis_title="Timeline", yaxis_title="Items", height=500
    )

    fig9.update_layout(
        xaxis=dict(dtick=(86400000.0 * 3), tickformat="%d %b", tickfont=dict(size=10))
    )

    fig9.update_layout(
        modebar_add=[
            "drawline",
            "drawopenpath",
            "drawclosedpath",
            "drawcircle",
            "drawrect",
            "eraseshape",
        ]
    )

    fig9.update_xaxes(showgrid=False, zeroline=False, tickangle=45)
    fig9.update_yaxes(showgrid=True, zeroline=True)

    fig9.update_layout(showlegend=False)

    fig29 = go.Figure(fig9)
    fig29.update_layout(showlegend=True)

    fig9.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )

    fig9.update_layout(xaxis_title=None, yaxis_title=None)

    #############################################################
    ct_median = age_data
    ct_media_round = ct_median.round(2)

    fig10 = px.sunburst(
        ct_media_round,
        path=["issue_type", "issue_points", "Age in Stage"],
        values="Age in Stage",
        color="issue_type",
        color_discrete_map={
            "Bug": "red",
            "Task": "blue",
            "Story": "green",
            "Epic": "purple",
        },
    )

    fig20 = go.Figure(fig10)
    fig20.update_layout(width=1800, height=700)
    fig10.update_layout(xaxis_title="", yaxis_title="")

    #############################################################
    fig11 = px.scatter(
        issue_data,
        x="issue_points",
        y=["cycle_time_days"],
        color="issue_points",
        trendline="ols",
        size="issue_points",
        hover_data=["issue_points"],
    ).update_layout(xaxis_title="Points", yaxis_title="Cycle Time (Days)")

    fig11.update_layout(showlegend=False)
    fig11.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )

    fig22 = go.Figure(fig11)
    fig22.update_layout(showlegend=True, width=1800, height=700)

    fig22.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
    )

    fig11.update_layout(xaxis_title=None, yaxis_title=None)

    # ################## ############## #
    # scatter_title_aging = "Current Work in Progess Aging..: " + FILTER_ISSUES_SINCE + " and " + FILTER_ISSUES_UNTIL

    fig12 = px.scatter(
        age_data, x="last_issue_status", y=["Age in Stage"]
    ).update_layout(xaxis_title="Status", yaxis_title="Days", autosize=True)

    p50Text = "50%  (" + "{:.2f}".format(age_data["P50"].max()) + " days" + ")"
    p75Text = "75%  (" + "{:.2f}".format(age_data["P75"].max()) + " days" + ")"
    p85Text = "85%  (" + "{:.2f}".format(age_data["P85"].max()) + " days" + ")"
    p95Text = "95%  (" + "{:.2f}".format(age_data["P95"].max()) + " days" + ")"
    p99Text = "99%  (" + "{:.2f}".format(age_data["P99"].max()) + " days" + ")"

    fig12.add_hline(
        y=age_data["P50"].max(), line_width=0.8, line_dash="dash", line_color="red"
    )
    fig12.add_hline(
        y=age_data["P75"].max(), line_width=0.8, line_dash="dash", line_color="orange"
    )
    fig12.add_hline(
        y=age_data["P85"].max(), line_width=0.8, line_dash="dash", line_color="green"
    )
    fig12.add_hline(
        y=age_data["P95"].max(), line_width=0.8, line_dash="dash", line_color="blue"
    )
    fig12.add_hline(
        y=age_data["P99"].max(), line_width=0.8, line_dash="dash", line_color="purple"
    )

    fig12.add_scatter(
        x=["last_issue_status"],
        y=[age_data["P50"].max()],
        marker=dict(color="red", size=10),
        name="50%",
        text=p50Text,
        mode="lines+text",
        textposition="top left",
        textfont_color="red",
    ).update_traces(textfont_size=10)
    fig12.add_scatter(
        x=["last_issue_status"],
        y=[age_data["P75"].max()],
        marker=dict(color="orange", size=10),
        name="75%",
        text=p75Text,
        mode="lines+text",
        textposition="top left",
        textfont_color="orange",
    ).update_traces(textfont_size=10)
    fig12.add_scatter(
        x=["last_issue_status"],
        y=[age_data["P85"].max()],
        marker=dict(color="green", size=10),
        name="85%",
        text=p85Text,
        mode="lines+text",
        textposition="top left",
        textfont_color="green",
    ).update_traces(textfont_size=10)
    fig12.add_scatter(
        x=["last_issue_status"],
        y=[age_data["P95"].max()],
        marker=dict(color="blue", size=10),
        name="95%",
        text=p95Text,
        mode="lines+text",
        textposition="top left",
        textfont_color="blue",
    ).update_traces(textfont_size=10)
    fig12.add_scatter(
        x=["last_issue_status"],
        y=[age_data["P99"].max()],
        marker=dict(color="purple", size=10),
        name="99%",
        text=p99Text,
        mode="lines+text",
        textposition="top left",
        textfont_color="purple",
    ).update_traces(textfont_size=10)

    fig12.update_layout(yaxis=dict(dtick=(5), tickfont=dict(size=10)))

    fig12.update_layout(xaxis=dict(tickfont=dict(size=10)))

    fig12.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )

    fig12.update_xaxes(tickangle=0)
    fig12.update_layout(showlegend=False)

    fig32 = go.Figure(fig12)

    fig32.update_layout(legend=dict(
        yanchor="top",
        y=0.90,
        xanchor="left",
        x=1
    ))
    fig32.update_layout(showlegend=True)
    fig12.update_layout(xaxis_title=None, yaxis_title=None)

    # ############ ################

    monte_carlo_items = f"Simulation {SIMULATIONS} Runs"

    fig13 = px.bar(
        df, x=distribution_when["Days"], y=distribution_when["Frequency"]
    ).update_layout(
        # title=monte_carlo_items,
        xaxis_title=f"Completion Days for {SIMULATION_ITEMS} Items",
        yaxis_title="Frequency",
    )

    fig13 = px.bar(distribution_how, x="Items", y="Probability").update_layout(xaxis_title="Completion Days",
                                                                               yaxis_title="Frequency")

    fig13.add_hline(y=0.5, line_width=0.8, line_dash="dash", line_color="red")
    fig13.add_hline(y=25, line_width=0.8, line_dash="dash", line_color="orange")
    fig13.add_hline(y=50, line_width=0.8, line_dash="dash", line_color="blue")
    fig13.add_hline(y=75, line_width=0.8, line_dash="dash", line_color="green")
    fig13.add_hline(y=85, line_width=0.8, line_dash="dash", line_color="purple")
    fig13.add_hline(y=95, line_width=0.8, line_dash="dash", line_color="pink")

    p05 = "{:.2f}".format(samples_how.Items.quantile(0.95))

    p05hline = f"5%  ({p05} Items)"
    p25hline = f"25% ({(samples_how.Items.quantile(0.85))} Items)"
    p50hline = f"50% ({(samples_how.Items.quantile(0.75))} Items)"
    p75hline = f"75% ({(samples_how.Items.quantile(0.50))} Items)"
    p85hline = f"85% ({(samples_how.Items.quantile(0.25))} Items)"
    p95hline = f"95% ({(samples_how.Items.quantile(0.05))} Items)"

    mt_card = str(round(samples_how.Items.quantile(0.25))) + " Items or more"

    fig13.add_scatter(x=[distribution_how["Items"].max() - 10], y=[0.5], marker=dict(color='red', size=30), name="5%",
                      text=p05hline, mode='lines+text', textposition='middle left')
    fig13.add_scatter(x=[distribution_how["Items"].max() - 10], y=[25], marker=dict(color='orange', size=30),
                      name="25%", text=p25hline, mode='lines+text', textposition='top left')
    fig13.add_scatter(x=[distribution_how["Items"].max() - 10], y=[50], marker=dict(color='blue', size=30), name="50%",
                      text=p50hline, mode='lines+text', textposition='top left')
    fig13.add_scatter(x=[distribution_how["Items"].max() - 10], y=[75], marker=dict(color='green', size=30), name="75%",
                      text=p75hline, mode='lines+text', textposition='top left')
    fig13.add_scatter(x=[distribution_how["Items"].max() - 10], y=[85], marker=dict(color='purple', size=30),
                      name="85%", text=p85hline, mode='lines+text', textposition='top left')
    fig13.add_scatter(x=[distribution_how["Items"].max() - 10], y=[95], marker=dict(color='pink', size=30), name="95%",
                      text=p95hline, mode='lines+text', textposition='top left')

    fig13.update_layout(xaxis=dict(dtick=(1)))

    fig13.update_layout(xaxis=dict(tickfont=dict(size=10)))

    fig13.update_layout(
        margin=dict(l=5, r=5, t=25, b=5),
    )

    fig43 = go.Figure(fig13)
    fig13.update_layout(xaxis_title=None, yaxis_title=None)

    # ############ ################

    fig14 = px.bar(
        df, x=distribution_when["Days"], y=distribution_when["Probability"]
    ).update_layout(
        # title=prob_monte_carlo_simulation,
        xaxis_title="Completion Days",
        yaxis_title="Frequency",
    )
    fig14.add_hline(y=0.5, line_width=0.8, line_dash="dash", line_color="red")
    fig14.add_hline(y=25, line_width=0.8, line_dash="dash", line_color="orange")
    fig14.add_hline(y=50, line_width=0.8, line_dash="dash", line_color="blue")
    fig14.add_hline(y=75, line_width=0.8, line_dash="dash", line_color="green")
    fig14.add_hline(y=85, line_width=0.8, line_dash="dash", line_color="purple")
    fig14.add_hline(y=95, line_width=0.8, line_dash="dash", line_color="pink")

    p05hline = f"5%  ({(round(samples.Days.quantile(0.05)))} days)"
    p25hline = f"25% ({(round(samples.Days.quantile(0.25)))} days)"
    p50hline = f"50% ({(round(samples.Days.quantile(0.50)))} days)"
    p75hline = f"75% ({(round(samples.Days.quantile(0.75)))} days)"
    p85hline = f"85% ({(round(samples.Days.quantile(0.85)))} days)"
    p95hline = f"95% ({(round(samples.Days.quantile(0.95)))} days)"

    fig14.add_scatter(
        x=[0],
        y=[0.5],
        marker=dict(color="red", size=30),
        name="5%",
        text=p05hline,
        mode="lines+text",
        textposition="top right",
    )
    fig14.add_scatter(
        x=[0],
        y=[25],
        marker=dict(color="orange", size=30),
        name="25%",
        text=p25hline,
        mode="lines+text",
        textposition="top right",
    )
    fig14.add_scatter(
        x=[0],
        y=[50],
        marker=dict(color="blue", size=30),
        name="50%",
        text=p50hline,
        mode="lines+text",
        textposition="top right",
    )
    fig14.add_scatter(
        x=[0],
        y=[75],
        marker=dict(color="green", size=30),
        name="75%",
        text=p75hline,
        mode="lines+text",
        textposition="top right",
    )
    fig14.add_scatter(
        x=[0],
        y=[85],
        marker=dict(color="purple", size=30),
        name="85%",
        text=p85hline,
        mode="lines+text",
        textposition="top right",
    )
    fig14.add_scatter(
        x=[0],
        y=[95],
        marker=dict(color="pink", size=30),
        name="95%",
        text=p95hline,
        mode="lines+text",
        textposition="top right",
    )

    fig14.update_layout(xaxis=dict(dtick=(1), tickfont=dict(size=10)))

    fig14.update_layout(yaxis=dict(dtick=(10), tickfont=dict(size=10)))

    fig14.update_layout(
        {
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    fig14.update_layout(
        margin=dict(l=5, r=5, t=25, b=5),
    )

    fig14.update_xaxes(showgrid=False, zeroline=False)
    fig14.update_yaxes(showgrid=False, zeroline=True)

    fig14.update_layout(showlegend=False)
    fig14.update_layout(xaxis_range=[-0.2, distribution_when["Days"].max() + 1])

    fig44 = go.Figure(fig14)
    fig44.update_layout(showlegend=True)
    fig14.update_layout(xaxis_title=None, yaxis_title=None)

    print("Fim do callback")
    # ########### #################
    # ct_85 = "30 Days or Less"
    # wip_inp = "15 Items"
    # mt_card = "45 Items or more"
    # eff_card = "68%"

    return (
        fig,
        fig2,
        fig3,
        fig4,
        fig5,
        fig6,
        fig7,
        fig8,
        fig9,
        fig10,
        fig11,
        fig12,
        fig13,
        fig14,
        fig20,
        fig21,
        fig22,
        fig25,
        fig26,
        fig27,
        fig29,
        fig32,
        fig33,
        fig43,
        fig44,
        ct_85,
        wip_inp,
        mt_card,
    )



@app.callback(
    Output('fe_card', 'children'),
    Input('framework-multi-select', 'value')
)
def update_flow_efficiency_card(selected_project):
    efficiency = analysis.calculate_flow_efficiency('data/status.csv', project_key='PRJ')
    return f"{efficiency:.2f}%"


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)