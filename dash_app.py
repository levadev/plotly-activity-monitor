from dash_bootstrap_components import Row, Col
from dash import Dash, Input, Output
from dash.dcc import Graph, Interval
from dash.html import Div
from service import get_system, get_cpu, get_disk, get_ram
import json
import plotly.io as pio

with open("assets/quartz.json") as f:
    template = json.load(f)
pio.templates["QUARTZ"] = template
pio.templates.default = "QUARTZ"

app = Dash(
    __name__,
    title="Monitor",
    update_title=False,
)


style = {
    "marginTop": "10px",
    "marginBottom": "10px",
    "border": "1px",
    "borderRadius": "45px",
    "overflow": "hidden",
    "boxShadow": "0 20px 30px rgba(0,0,0,0.4)"
}


config = {"displayModeBar": False}


app.layout = Div([

    Row([
        Col([
            Graph(
                id="graph_ram",
                figure=get_ram(),
                style=style,
                config=config
            )
        ]),

        Col([
            Graph(
                id="graph_system",
                figure=get_system(),
                style=style,
                config=config
            )
        ])
    ],
        className="first_row"
    ),

    Row([
        Col([
            Graph(
                id="graph_cpu",
                figure=get_cpu(),
                style=style,
                config=config
            )
        ])
    ]),

    Row([
        Col([
            Graph(
                figure=get_disk(),
                style=style,
                config=config
            )
        ])
    ]),

    Interval(
        id="interval",
        interval=10*1000,  # in milliseconds
        # interval=0.8*1000,  # in milliseconds
        n_intervals=0
    )
],
    className="main_div"
)


@app.callback(
    # component_id, component_property
    Output("graph_ram", "figure"),
    Output("graph_cpu", "figure"),
    Input("interval", "n_intervals")
)
def update_ram(sec):
    return get_ram(), get_cpu()


if __name__ == "__main__":
    app.run_server()
