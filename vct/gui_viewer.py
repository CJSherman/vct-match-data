import numpy as np

from collections import defaultdict
from matplotlib.figure import Figure
from sqlalchemy.orm import Session
from typing import Union

from .databases import Tournament, Map, Agent, Comp, Team
from .functions import divide


def get_label(item: Union[Tournament, Map, Agent, Comp, Team],
              labels: Union[list[str], str]) -> int:
    """
    Sequentially returns attributes of a database entry, e.g. :attr:`item` of type Map and
    :attr:`labels` = ["tournament_ref", "games"] will return the value of Map.tournament_ref.games

    Parameters
    ----------
    item : Union[Tournament, Map, Agent, Comp, Team]
        Entry in a database.
    labels: Union[list[str], str]
        The attributes to be obtained. If a list is entered they are searched recursively.

    Returns
    -------
    int
        The value of that attribute.
    """
    if not isinstance(labels, list):
        labels = [labels]
    att = item
    for label in labels:
        att = att.__getattribute__(label)
    return att


def order_tournaments(x: list, y: list, labels: list, position: list[bool, bool],
                      tournaments: list[str]) -> tuple[list, list, list]:
    """
    Orders the tournaments in a set of data chronologically
    x : list
    y : list
    labels : list
    position : list[bool, bool]
        Where the Tournaments sit in the data. Index 0 represents the x_axis, index 1 represents the
        split data.
    tournaments : list[str]
        The tournaments in chronological order.

    Returns
    -------
    tuple[list, list, list]
        The modified x, y, and labels lists.
    """

    if position[0]:
        pair = [(x_, y_, labels_) for x_, y_, labels_ in zip(x, y, labels)]
        pair.sort(key=lambda n: tournaments.index(n[0]))
        x = [pair_[0] for pair_ in pair]
        y = [pair_[1] for pair_ in pair]
        labels = [pair_[2] for pair_ in pair]
    if position[1]:
        for i, (y_, labels_) in enumerate(zip(y, labels)):
            pair = [(y__, labels__) for y__, labels__ in zip(y_, labels_)]
            pair.sort(key=lambda n: tournaments.index(n[1]))
            y[i] = [pair_[0] for pair_ in pair]
            labels[i] = [pair_[1] for pair_ in pair]
    return x, y, labels


def select_data(y: list, labels: list, count: int) -> tuple[list, list]:
    """
    Selects the :attr:`n` highest values in each bar.

    Parameters
    ----------
    y : list
    labels : list
    count : int
        The number of stacked bars desired

    Returns
    -------
    tuple[list, list, list]
        The selected x, y and labels data
    """

    for i, (y_, label) in enumerate(zip(y, labels)):
        pair = [(l, n) for n, l in zip(y_, label)]
        pair.sort(key=lambda x: x[1])
        y[i] = [item[1] for item in pair[-count:]]
        labels[i] = [item[0] for item in pair[-count:]]
    return y, labels


def plotter(x: list, y: list, y_label: str, title: str,
            split_labels: list[str], num_splits: int) -> Figure:
    """
    Function to produce a nicely formatted plot using matplotlib.pyplot.

    Parameters
    ----------
    x : list
    y : list
    y_label : str
    title : str
    split_labels : list[str]
        Labels for any stacked bars.
    num_splits : int
        The number of stacked bars.

    Returns
    -------
    Figure
    """

    sep = 2
    x_axis = sep * np.arange(len(x))
    width = sep / (num_splits + 1)
    fig = Figure(figsize=(25, 10), dpi=100)
    ax = fig.add_subplot(111)
    if y_label == "Sidedness":
        ax.set_ylim(-50, 50)
        ax.axline(xy1=(0, 0), slope=0, color="k")
    elif y_label == "Games":
        pass
    else:
        ax.set_ylim(0, 100)

    for i in range(len(y)):
        width = sep / (len(y[i]) + 1)
        for j in range(len(y[i])):
            x_val = x_axis[i] + width * (int(j)-(len(y[i])-1)/2)
            ax.bar(x_val, y[i][j], width)
            if num_splits != 1:
                ax.text(x_val, 0, f" {split_labels[i][j]}", size=9,
                        horizontalalignment="left", verticalalignment="center_baseline",
                        rotation="vertical", rotation_mode="anchor")

    ax.set_xticks(x_axis, x, rotation=30, ha="right")
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot(Tournaments: list[str], Maps: list[str], Comps: list[str], Agents: list[str],
         Teams: list[str], focus: str, x_axis: str, y_axis: str, split: str, count: int,
         session: Session) -> Figure:
    """
    Compiles the data given by the selected options, returns the data plotted by :func:`plotter`

    Parameters
    ----------
    Tournaments : list[str]
    Maps : list[str]
    Comps : list[str]
    Agents : list[str]
    Teams : list[str]
    focus : {"Tournaments", "Maps", "Comps", "Agents", "Teams"}
        The Table from which the data is taken.
    x_axis : str
        The grouping used on the x-axis.
    y_axis : str
        The statistic plotted on the y-axis.
    split : str
        The grouping used across stacked bars.
    count : int
        The number of desired stacked bars.
    session : Session

    Returns
    -------
    Figure
        The :class:`~matplotlib.figure.Figure` showing the data.
    """
    placement = [0, 0]
    label_1 = x_axis[:-1].lower()
    label_2 = split[:-1].lower()
    atts = ["games"]
    title = ""

    if focus == "Tournaments":
        sources = session.query(Tournament).where(Tournament.tournament.in_(Tournaments)).all()
        count = 1
    elif focus == "Maps":
        sources = session.query(Map).where((Map.tournament.in_(Tournaments)) &
                                           (Map.map.in_(Maps))).all()
        atts += [["tournament_ref", "games"], "ct_wins", "t_wins"]
        if len(Maps) == 1:
            title = Maps[0]
    else:
        atts += [["map_ref", "games"], "wins"]
        if focus == "Comps":
            sources = session.query(Comp).where((Comp.tournament.in_(Tournaments)) &
                                                (Comp.map.in_(Maps)) &
                                                (Comp.ref.in_(Comps))).all()
            if len(Comps) == 1:
                title = Comps[0]
        elif focus == "Agents":
            sources = session.query(Agent).where((Agent.tournament.in_(Tournaments)) &
                                                 (Agent.map.in_(Maps)) &
                                                 (Agent.agent.in_(Agents))).all()
            if len(Agents) == 1:
                title = Agents[0]
        elif focus == "Teams":
            sources = session.query(Team).where((Team.tournament.in_(Tournaments)) &
                                                (Team.map.in_(Maps)) &
                                                (Team.team.in_(Teams))).all()
            if len(Teams) == 1:
                title = Teams[0]

    if x_axis == "Tournaments":
        placement[0] = 1
    elif x_axis == "Comps":
        label_1 = "ref"

    if split == "Tournaments":
        placement[1] = 1
    elif split == "Comps":
        label_2 = "ref"

    data = defaultdict(lambda: defaultdict(lambda: [0]*len(atts)))
    for source in sources:
        for i in range(len(atts)):
            data[get_label(source, label_1)][
                 get_label(source, label_2)][i] += get_label(source, atts[i])

    if x_axis == "Tournaments":
        x = Tournaments
        labels = [data[v].keys() for v in x]
    else:
        x = list(data.keys())
        labels = [list(v.keys()) for v in data.values()]

    if y_axis == "Games":
        y = [[[data[map][sub][0]] for sub in data[map].keys()] for map in x]
    elif y_axis == "Pickrate":
        if focus == "Maps":
            y = [[[100 * divide(data[map][sub][0], data[map][sub][1])]
                  for sub in data[map].keys()] for map in x]
        else:
            y = [[[100 * divide(data[map][sub][0], 2*data[map][sub][1])]
                  for sub in data[map].keys()] for map in x]
    elif y_axis == "Sidedness":
        y = [[[100 * divide(data[map][sub][2], data[map][sub][2] + data[map][sub][3], -0.5)]
              for sub in data[map].keys()] for map in x]
    elif y_axis == "Winrate":
        y = [[[100 * divide(data[map][sub][2], data[map][sub][0])]
              for sub in data[map].keys()] for map in x]
    elif y_axis == "Rating":
        y = [[[100 * divide(data[comp][sub][2], data[comp][sub][1])]
              for sub in data[comp].keys()] for comp in x]

    y, labels = select_data(y, labels, count)
    x, y, labels = order_tournaments(x, y, labels, placement, Tournaments)

    if count != 1:
        title = ""

    return plotter(x, y, y_label=y_axis, title=title, split_labels=labels, num_splits=count)
