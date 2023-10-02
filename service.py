from math import floor, pow, log
from platform import uname
from plotly.graph_objects import Figure, Pie, Bar, Table
from plotly.subplots import make_subplots
from psutil import virtual_memory, cpu_percent, disk_partitions, disk_usage


HOLE_PIE_SIZE = .3
PULL_PIE_SIZE = .08
PIE_TEXTINFO = "value"
SHOW_LEGEND = False
MARKER_LINE_COLOR = "#000000"
MARKER_LINE_WIDTH = 2
PIE_SPEC = {"type": "pie"}


def convert_size(size_bytes: float) -> str:
    """
    parametrs:
        size_bytes: bytes to be converted
        place: flag for base of degree in math.pow

    return:
        string with converted value and size name (format like "14 KB")
    """

    base = 1024

    if size_bytes != 0:
        try:

            SIZE_NAMES = ("B", "KB", "MB", "GB", "TB", "PB")
            i = int(floor(log(size_bytes, 1024)))
            converted_size = round(size_bytes / pow(base, i), 2)

            return f"{converted_size} {SIZE_NAMES[i]}"

        except Exception as e:

            print(f"Oops... Something went wrong -> {e}")
            return "0 B"
    else:
        return "0 B"


def get_system() -> Figure:
    """
    return:
        plotly.graph_objects.Figure with system information Table
    """

    table = uname()._asdict()

    fig = Figure(data=[
        Table(
            columnwidth=[25, 100],
            header=dict(
                align=["center", "center"],
                values=["Parametrs", ""]
            ),
            cells=dict(
                height=40,
                align=["center", "center"],
                values=[list(table.keys()), list(table.values())]
            )
        )
    ])

    fig.update_layout(
        title="System Information",
        title_x=0.5,
    )

    return fig


def get_ram() -> Figure:
    """
    return:
        plotly.graph_objects.Figure with RAM usage Pie diagram
    """

    memory = virtual_memory()
    total = convert_size(memory.total)
    used = memory.percent

    total_GB = float(total.split(" ")[0])
    free_GB = round(total_GB - (total_GB*used/100), 2)
    used_GB = round(total_GB * used / 100, 2)

    fig = Figure(data=[
        Pie(
            labels=["Free", "Used"],
            values=[free_GB, used_GB],
            hole=HOLE_PIE_SIZE,
            pull=PULL_PIE_SIZE
        )
    ])

    fig.update_traces(
        hoverinfo="label+percent",
        textfont_size=20,
        texttemplate="%{value} GB",
        marker=dict(line=dict(
            color="#000000",
            width=2
        )),
        textinfo=PIE_TEXTINFO,
        showlegend=SHOW_LEGEND
    )

    fig.update_layout(
        title=f" Total RAM: {total}",
        title_x=0.5,
        margin=dict(l=0, r=0, t=60, b=20),
    )

    return fig


def get_cpu() -> Figure:
    """
    return:
        plotly.graph_objects.Figure with two columns sublots (Average CPU usage Pie diagram, Bar per kernel diagram)
    """

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[PIE_SPEC, {"type": "bar"}]],
        column_widths=[0.3, 0.7]
    )

    cpus = cpu_percent(percpu=True)
    av = cpu_percent()
    cpus.sort()

    fig.add_trace(
        Bar(
            x=[f"{i+1}'s" for i in range(len(cpus))],
            y=cpus,
            text=[f"{i} %" for i in cpus],
            hoverinfo="none",
            marker_line_width=MARKER_LINE_WIDTH,
            marker_line_color=MARKER_LINE_COLOR
        ),
        row=1,
        col=2
    )

    fig.add_trace(
        Pie(
            values=[100.0 - av, av],
            labels=["Free CPU", "Used CPU"],
            title="Mean",
            hoverinfo="label",
            texttemplate="%{value}%",
            textfont_size=20,
            pull=PULL_PIE_SIZE,
            hole=HOLE_PIE_SIZE,
            marker_line_width=MARKER_LINE_WIDTH,
            textinfo=PIE_TEXTINFO,
            marker_line_color=MARKER_LINE_COLOR
        ),
        row=1,
        col=1
    )

    fig.update_layout(
        title_text="CPU Usage",
        showlegend=SHOW_LEGEND
    )

    return fig


def get_disk() -> Figure:
    """
    return:
        plotly.graph_objects.Figure with n disk sublots (Pie diagrma for every physical or logical disk)
    """

    list_of_disks = []

    for i in disk_partitions():

        if "snap" not in i.mountpoint and "boot" not in i.mountpoint:

            hdd = disk_usage(i.mountpoint)

            list_of_disks.append({
                "mountpoint": i.mountpoint,
                "total_size": convert_size(hdd.total),
                "free_space": convert_size(hdd.free).split(" "),
                "used_space": convert_size(hdd.used).split(" ")
            })

    fig = make_subplots(
        rows=1,
        cols=len(list_of_disks),
        specs=[[PIE_SPEC for i in range(len(list_of_disks))]],
        column_titles=[i["mountpoint"] for i in list_of_disks]
    )

    for i in list_of_disks:

        fig.add_trace(
            Pie(
                labels=["Used", "Free"],
                values=[i["used_space"][0], i["free_space"][0]],
                hoverinfo="label+percent+name",
                textfont_size=12,
                texttemplate="%{value} GB",
                name=i["total_size"],
                hole=HOLE_PIE_SIZE,
                pull=PULL_PIE_SIZE,
                marker_line_width=MARKER_LINE_WIDTH,
                textinfo=PIE_TEXTINFO,
                marker_line_color=MARKER_LINE_COLOR
            ),
            row=1,
            col=list_of_disks.index(i)+1
        )

    fig.update_annotations(textangle=-90)

    fig.update_layout(
        title_text="Disk space",
        margin_t=210,
        showlegend=SHOW_LEGEND
    )

    return fig
