import numpy as np
import matplotlib.pyplot as plt

from sqlalchemy.orm import session
from collections import Counter

from .databases import Tournament, Map, Agent, Comp, Team
from .functions import choice_check, divide, int_input


# TODO fix viewers
def view_maps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
              session: session.Session) -> str:
    """Function to retrieve text map data. Data can be sorted by map or tournament.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session

    Returns
    -------
    str
        The Data."""

    tournaments_or_maps = choice_check("How do you want to view Map stats?\n" +
                                       "a) By Maps\n" +
                                       "b) By Tournaments\n",
                                       ["a", "b"])

    if tournaments_or_maps == "a":  # by maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        # list of maps that were played in the chosen tournament
        maps = session.query(Map).where((Map.tournament == Tournaments[tournament_choice-1]) &
                                        (Map.map != "Overall")).order_by(Map.games.desc()).all()
        output = "Map{:7s}Picks{:>5s}Pickrate{:>2s}Sidedness\n".format("", "", "")
        for map in maps:
            pickrate = divide(map.games, map.tournament_ref.games)
            sidedness = divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5)
            output += "{:<10s}{:>5.0f}{:>12.2f}%{:>10.2f}%\n".format(
                map.map, map.games, 100*pickrate, 100*sidedness)

    elif tournaments_or_maps == "b":  # by tournaments
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        # list of map objects that were of the chosen map
        maps = session.query(Map).where((Map.tournament != "Overall") &
                                        (Map.map == Maps[map_choice-1])).all()
        output = "Tournament{:10s}Pickrate{:>2s}Sidedness\n".format("", "")
        for map in maps:
            pickrate = divide(map.games, map.tournament_ref.games)
            sidedness = divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5)
            output += "{:<20s}{:>7.2f}%{:>10.2f}%\n".format(
                map.tournament, 100*pickrate, 100*sidedness)

    return output


def view_comps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
               session: session.Session) -> str:
    """Function to retrieve text comp data. Data can be sorted by comp, map or tournament.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session

    Returns
    -------
    str
        The Data."""

    tournaments_maps_or_comps = choice_check("How do you want to view Comp stats?\n" +
                                             "a) By Comps\n" +
                                             "b) By Maps\n" +
                                             "c) By Tournaments\n",
                                             ["a", "b", "c"])

    if tournaments_maps_or_comps == "a":  # by comps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        # object of the chosen map
        map = session.query(Map).where((Map.tournament == Tournaments[tournament_choice-1]) &
                                       (Map.map == Maps[map_choice-1])).first()
        # list of comps played in the chosen tournament on the chosen map
        comps = session.query(Comp).where((Comp.tournament == Tournaments[tournament_choice-1]) &
                                          (Comp.map == Maps[map_choice-1])).\
            order_by((Comp.wins/map.games).desc()).all()

        output = "{:<50s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for comp in comps:
            pickrate = divide(comp.games, 2*comp.map_ref.games)
            winrate = divide(comp.wins, comp.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:<10s}{:<10s}{:<10s}{:<10s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                comp.agent_1, comp.agent_2, comp.agent_3, comp.agent_4, comp.agent_5,
                100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_comps == "b":  # by maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        # list of comps played in the chosen tournament
        Comps_list = [comp.ref for comp in session.query(Comp).where(
            Comp.tournament == Tournaments[tournament_choice-1]).all()]
        Comps = list(set(Comps_list))
        Comps = sorted(Comps, key=Counter(Comps_list).get, reverse=True)
        comp_msg = ""
        for n, comp in enumerate(Comps):
            comp_msg += f"{n+1}) {comp}\n"
        comp_choice = int(choice_check("What Comp do you want to view?\n" + comp_msg,
                                       np.arange(1, len(Comps)+1)))
        # list comp objects of the chosen comp and tournament
        comps = session.query(Comp).where(
            (Comp.tournament == Tournaments[tournament_choice-1]) &
            (Comp.ref == Comps[comp_choice-1])).order_by((Comp.wins/Comp.games).desc()).all()
        output = "Map{:7s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for comp in comps:
            pickrate = divide(comp.games, 2*comp.map_ref.games)
            winrate = divide(comp.wins, comp.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                comp.map, 100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_comps == "c":  # by tournaments
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        # list of comps played on the chosen map
        Comps_list = [comp.ref for comp in session.query(Comp).where(
            Comp.map == Maps[map_choice-1]).all()]
        Comps = list(set(Comps_list))
        Comps = sorted(Comps, key=Counter(Comps_list).get, reverse=True)
        comp_msg = ""
        for n, comp in enumerate(Comps):
            comp_msg += f"{n+1}) {comp}\n".format(n+1, comp)
        comp_choice = int(choice_check("What Comp do you want to view?\n" + comp_msg,
                                       np.arange(1, len(Comps)+1)))
        # list of comp objects of the chosen comp and map
        comps = session.query(Comp).where(
            (Comp.tournament != "Overall") &
            (Comp.map == Maps[map_choice-1]) &
            (Comp.ref == Comps[comp_choice-1])).all()
        output = "Tournament{:10s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for comp in comps:
            pickrate = divide(comp.games, 2*comp.map_ref.games)
            winrate = divide(comp.wins, comp.games)
            rating = pickrate * winrate * 200
            output += "{:<20s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                comp.tournament, 100*pickrate, 100*winrate, rating)
    return output


def view_agents(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
                Agents: list[str], agent_msg: str, session: session.Session) -> str:
    """Function to retrieve text agent data. Data can be sorted by agent, map or tournament.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    Agents : list[str]
    agent_msg : str
        String containing all available agents, numbered.
    session : session.Session

    Returns
    -------
    str
        The Data."""

    tournaments_maps_or_agents = choice_check("How do you want to view Agent stats?\n" +
                                              "a) By Agents\n" +
                                              "b) By Maps\n" +
                                              "c) By Tournaments\n",
                                              ["a", "b", "c"])

    if tournaments_maps_or_agents == "a":  # by agents
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        # object of the chosen map
        map = session.query(Map).where((Map.tournament == Tournaments[tournament_choice-1]) &
                                       (Map.map == Maps[map_choice-1])).first()
        # list of agents played in the chosen tournament on the chosen map
        agents = session.query(Agent).where(
            (Agent.tournament == Tournaments[tournament_choice-1]) &
            (Agent.map == Maps[map_choice-1])).order_by((Agent.wins/map.games).desc()).all()
        output = "Agent{:7s}Pickrate{:3s}Winrate{:4s}Rating\n".format("", "", "")
        for agent in agents:
            pickrate = divide(agent.games, 2*agent.map_ref.games)
            winrate = divide(agent.wins, agent.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>9.2f}%{:>9.2f}%{:>10.0f}\n".format(
                agent.agent, 100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_agents == "b":  # by maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        # list of agent objects of the chosen agent and tournament
        agents = session.query(Agent).where(
            (Agent.tournament == Tournaments[tournament_choice-1]) &
            (Agent.map != "") &
            (Agent.agent == Agents[agent_choice-1])).order_by((Agent.wins/Agent.games).desc()).all()
        output = "Map{:7s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for agent in agents:
            pickrate = divide(agent.games, 2*agent.map_ref.games)
            winrate = divide(agent.wins, agent.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                agent.map, 100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_agents == "c":  # tournaments
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        # list of agent objects of the chosen agent and map
        agents = session.query(Agent).where(
            (Agent.tournament != "Overall") &
            (Agent.map == Maps[map_choice-1]) &
            (Agent.agent == Agents[agent_choice-1])).all()
        output = "Tournament{:10s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for agent in agents:
            pickrate = divide(agent.games, 2*agent.map_ref.games)
            winrate = divide(agent.wins, agent.games)
            rating = pickrate * winrate * 200
            output += "{:<20s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                agent.tournament, 100*pickrate, 100*winrate, rating)
    return output


def view_teams(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
               Teams: list[str], team_msg: str, session: session.Session) -> str:
    """Function to retrieve text team data. Data can be sorted by agent, map or tournament.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    Teams : list[str]
    team_msg : str
        String containing all available teams, numbered.
    session : session.Session

    Returns
    -------
    str
        The Data."""

    tournaments_maps_or_teams = choice_check("How do you want to view Team stats?\n" +
                                             "a) By Teams\n" +
                                             "b) By Maps\n" +
                                             "c) By Tournaments\n",
                                             ["a", "b", "c"])

    if tournaments_maps_or_teams == "a":  # by teams
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        # object of the chosen map
        map = session.query(Map).where(
            (Map.tournament == Tournaments[tournament_choice-1]) &
            (Map.map == Maps[map_choice-1])).first()
        # list of teams in the chosen tournament on the chosen map
        teams = session.query(Team).where(
            (Team.tournament == (Tournaments[tournament_choice-1])) &
            (Team.map == Maps[map_choice-1])).order_by((Team.wins/map.games).desc()).all()
        output = "Team{:9s}Matches{:3s}Winrate{:4s}Rating\n".format("", "", "")
        for team in teams:
            pickrate = divide(team.games, 2*team.map_ref.games)
            winrate = divide(team.wins, team.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>10d}{:>9.2f}%{:>10.0f}\n".format(
                team.team, team.games, 100*winrate, rating)

    elif tournaments_maps_or_teams == "b":  # by maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        team_choice = int(choice_check("What Team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        # list of team objects of the chosen team and tournament
        teams = session.query(Team).where(
            (Team.tournament == Tournaments[tournament_choice-1]) &
            (Team.map != "") &
            (Team.team == Teams[team_choice-1])).order_by((Team.wins/Team.games).desc()).all()
        output = "Map{:7s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for team in teams:
            pickrate = divide(team.games, 2*team.map_ref.games)
            winrate = divide(team.wins, team.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                team.map, 100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_teams == "c":  # tournaments
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        team_choice = int(choice_check("What Team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        # list of team objects of the chosen team and map
        teams = session.query(Team).where(
            (Team.tournament != "Overall") &
            (Team.map == Maps[map_choice-1]) & 
            (Team.team == Teams[team_choice-1])).all()
        output = "Tournament{:10s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for team in teams:
            pickrate = divide(team.games, 2*team.map_ref.games)
            winrate = divide(team.wins, team.games)
            rating = pickrate * winrate * 200
            output += "{:<20s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                team.tournament, 100*pickrate, 100*winrate, rating)

    return output


def plotter(x: list, y: list, label: str, title: str, labels: list[str] = None, n=1):
    """Function to produce a nicely formatted plot using matplotlib.pyplot.

    Parameters
    ----------
    x : list
    y : list
    label : str
        The y-axis label.
    title : str
    labels : list[str], default: None
        Labels for any stacked bars.
    n : int, default: 1
        The number of stacked bars."""

    sep = 2
    x_axis = sep * np.arange(len(x))
    width = sep / (n + 1)
    plt.figure(figsize=(20, 10))
    if label == "Sidedness":
        plt.ylim(-50, 50)
        plt.plot(x_axis, np.zeros(len(x_axis)), "k-")
    elif label in ["Matches", "Wins"]:
        pass
    else:
        plt.ylim(0, 100)
    for i in range(len(x)*n):
        plt.bar(x_axis[int(i/n)] + width * (int(i % n)-(n-1)/2), y[int(i/n)][i % n], width)
        if labels:
            if label in ["Matches", "Wins"]:
                plt.text(x_axis[int(i/n)] + width * (int(i % n)-(n-1)/2), 0.1,
                         labels[int(i/n)][i % n], rotation="vertical", size=10,
                         horizontalalignment="center")
            else:
                plt.text(x_axis[int(i/n)] + width * (int(i % n)-(n-1)/2), 1,
                         labels[int(i/n)][i % n], rotation="vertical", size=10,
                         horizontalalignment="center")
    plt.xticks(x_axis, x, rotation=15, ha="right")
    plt.title(title)
    plt.ylabel(label)
    plt.tight_layout()
    plt.show()


def plot_maps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
              session: session.Session):
    """Function to retrieve plot map data. X-axis can be Maps or tournaments. Y-axis can be
    Pickrate or sidedness.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session"""

    dependent = choice_check("Choose Dependent Variable\n" +
                             "a) Tournaments\n" +
                             "b) Maps\n",
                             ["a", "b"])
    independent = choice_check("Choose Independent Variable\n" +
                               "a) Pickrate\n" +
                               "b) Sidedness\n",
                               ["a", "b"])

    if dependent == "a":  # x=Tournaments
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        maps = session.query(Map).where((Map.map == Maps[map_choice-1]) &
                                        (Map.tournament != "Overall")).all()

        x = [map.tournament for map in maps]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(map.games, map.tournament_ref.games)] for map in maps]
            label = "Pickrate"
        elif independent == "b":  # y=Sidedness
            y = [[100 * divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5)] for map in maps]
            label = "Sidedness"

        plotter(x, y, label, Maps[map_choice-1])

    elif dependent == "b":  # x=Maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg, np.arange(1, len(Tournaments)+1)))
        maps = session.query(Map).\
            where(Map.tournament == Tournaments[tournament_choice-1]).all()

        x = [map.map for map in maps]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(map.games, map.tournament_ref.games)] for map in maps]
            label = "Pickrate"
        elif independent == "b":  # y=Sidedness
            y = [[100 * divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5)] for map in maps]
            label = "Sidedness"

        plotter(x, y, label, Tournaments[tournament_choice-1])


def plot_comps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
               session: session.Session):
    """Function to retrieve plot comp data. X-axis can be Maps or tournaments. Y-axis can be
    Pickrate, Winrate or Rating.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session"""

    dependent = choice_check("Choose Dependent Variable\n" +
                             "a) Tournaments\n" +
                             "b) Maps\n",
                             ["a", "b"])
    independent = choice_check("Choose Independent Variable\n" +
                               "a) Pickrate\n" +
                               "b) Winrate\n" +
                               "c) Rating\n",
                               ["a", "b", "c"])

    comp_choice = int_input("How Many Comps Should Be Shown In Plots? (Default is 3)\n" +
                            "Note: If this number is too large no data will be shown")

    if dependent == "a":  # x=Tournaments"
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        tournaments = session.query(Map).where((Map.tournament != "Overall") &
                                               (Map.map == Maps[map_choice-1])).all()
        labels = []
        y = []
        x = []
        for tournament in tournaments:
            comp_search = session.query(Comp).where((Comp.tournament == tournament.tournament) &
                                                    (Comp.map == Maps[map_choice-1]))
            if independent == "a":  # y=Pickrate
                comps = comp_search.order_by(Comp.games.desc()).all()
                comps = comps[:comp_choice]
                y_ = [100 * divide(comp.games, 2*comp.map_ref.games) for comp in comps]
                label = "Pickrate"
            elif independent == "b":  # y=Winrate
                comps = comp_search.order_by(Comp.wins.desc()).all()
                comps = comps[:comp_choice]
                y_ = [100 * divide(comp.wins, comp.games) for comp in comps]
                label = "Winrate"
            elif independent == "c":  # y=Rating
                comps = comp_search.order_by(Comp.wins.desc()).all()
                comps = comps[:comp_choice]
                y_ = [100 * divide(comp.wins, comp.map_ref.games) for comp in comps]
                label = "Rating"
            if len(y_) < comp_choice:
                continue
            y.append(y_)
            labels.append([comp.ref for comp in comps])
            x.append(tournament.tournament)

        plotter(x, y, label, Maps[map_choice-1], labels, n=comp_choice)

    elif dependent == "b":  # x=Maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" + 
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        maps = session.query(Map).where(Map.tournament == Tournaments[tournament_choice-1]).all()
        labels = []
        y = []
        x = []
        for map in maps:
            comp_search = session.query(Comp).where(
                (Comp.tournament == Tournaments[tournament_choice-1]) &
                (Comp.map == map.map))
            if independent == "a":  # y=Pickrate
                comps = comp_search.order_by(Comp.games.desc()).all()
                comps = comps[:comp_choice]
                y_ = [100 * divide(comp.games, 2*comp.map_ref.games) for comp in comps]
                label = "Pickrate"
            elif independent == "b":  # y=Winrate
                comps = comp_search.order_by(Comp.wins.desc()).all()
                comps = comps[:comp_choice]
                y_ = [100 * divide(comp.wins, comp.games) for comp in comps]
                label = "Winrate"
            elif independent == "c":  # y=Rating
                comps = comp_search.order_by(Comp.wins.desc()).all()
                comps = comps[:comp_choice]
                y_ = [100 * divide(comp.wins, comp.map_ref.games) for comp in comps]
                label = "Rating"
            if len(y_) < comp_choice:
                continue
            y.append(y_)
            labels.append([comp.ref for comp in comps])
            x.append(map.map)
        plotter(x, y, label, Tournaments[tournament_choice-1], labels, n=comp_choice)


def plot_agents_tournaments(Maps: list, map_msg: str, Agents: list, agent_msg: str,
                            independent: str, session: session.Session):
    """Function to retrieve plot agent data where the X-axis is tournaments. Y-axis can be
    Pickrate, Winrate or Rating. Plots can be focuses around a specific map, a specific agent or
    a specific agent on a specific map

    Parameters
    ----------
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    Agents : list[str]
    agent_msg : str
        String containing all available agents, numbered.
    session : session.Session"""

    title = choice_check("Choose Plot Focus\n" +
                         "a) Map\n" +
                         "b) Agent\n" +
                         "c) Agent on a Given Map\n",
                         ["a", "b", "c"])
    
    if title == "a":  # Title=Map
        agent_choice = int_input("How Many Agents Should Be Shown In Plots? (Default is 5)\n" +
                                 "Note: If this number is too large no data will be shown")
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        tournaments = session.query(Map).where((Map.tournament != "Overall") &
                                               (Map.map == Maps[map_choice-1])).all()
        labels = []
        y = []
        x = []
        for tournament in tournaments:
            agent_search = session.query(Agent).where((Agent.tournament == tournament.tournament) &
                                                      (Agent.map == tournament.map))
            if independent == "a":  # y=Pickrate
                agents = agent_search.order_by(Agent.games.desc()).all()
                agents = agents[:agent_choice]
                y_ = [100 * divide(agent.games, 2*agent.map_ref.games) for agent in agents]
                label = "Pickrate"
            elif independent == "b":  # y=Winrate
                agents = agent_search.order_by(Agent.wins.desc()).all()
                agents = agents[:agent_choice]
                y_ = [100 * divide(agent.wins, agent.games) for agent in agents]
                label = "Winrate"
            elif independent == "c":  # y=Rating
                agents = agent_search.order_by(Agent.wins.desc()).all()
                agents = agents[:agent_choice]
                y_ = [100 * divide(agent.wins, agent.map_ref.games) for agent in agents]
                label = "Rating"
            if len(y_) < agent_choice:
                continue
            y.append(y_)
            labels.append([agent.agent for agent in agents])
            x.append(tournament.tournament)
        plotter(x, y, label, Maps[map_choice-1], labels, agent_choice)

    elif title == "b":  # Title=Agent
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        agents = session.query(Agent).where((Agent.map == "") &
                                            (Agent.agent == Agents[agent_choice-1])).all()
        x = [agent.tournament for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.tournament_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.tournament_ref.games)] for agent in agents]
            label = "Rating"
        plotter(x, y, label, Agents[agent_choice-1])

    elif title == "c":  # Title=AgentOnMap
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        map_choice = int(choice_check(f"What Map do you want to view {Agents[agent_choice-1]} on?\n"
                                      + map_msg, np.arange(1, len(Maps)+1)))
        agents = session.query(Agent).where((Agent.map == Maps[map_choice-1]) &
                                            (Agent.agent == Agents[agent_choice-1])).all()
        x = [agent.tournament for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.map_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.map_ref.games)]
                 for agent in agents]
            label = "Rating"
        plotter(x, y, label, f"{Agents[agent_choice-1]} on {Maps[map_choice-1]}")


def plot_agents_maps(Tournaments: list, tournament_msg: str, Agents: list, agent_msg: str,
                     independent: str, session):
    """Function to retrieve plot agent data where the X-axis is maps. Y-axis can be
    Pickrate, Winrate or Rating. Plots can be focuses around a specific map, a specific agent or
    a specific agent on a specific map

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session"""

    title = choice_check("Choose Plot Focus\n" +
                         "a) Map\n" +
                         "b) Agent\n" +
                         "c) Agent on a Given Map\n",
                         ["a", "b", "c"])
    if title == "a":  # Title=Tournament
        agent_choice = int_input("How Many Agents Should Be Shown In Plots? (Default is 5)\n" +
                                 "Note: If this number is too large no data will be shown")
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg, np.arange(1, len(Tournaments)+1)))
        maps = session.query(Map).where(Map.tournament == Tournaments[tournament_choice-1]).all()
        labels = []
        y = []
        x = []
        for map in maps:
            agent_search = session.query(Agent).where((Agent.tournament == map.tournament) &
                                                      (Agent.map == map.map))
            if independent == "a":  # y=Pickrate
                agents = agent_search.order_by(Agent.games.desc()).all()
                agents = agents[:agent_choice]
                y_ = [100 * divide(agent.games, 2*agent.map_ref.games) for agent in agents]
                label = "Pickrate"
            elif independent == "b":  # y=Winrate
                agents = agent_search.order_by(Agent.wins.desc()).all()
                agents = agents[:agent_choice]
                y_ = [100 * divide(agent.wins, agent.games) for agent in agents]
                label = "Winrate"
            elif independent == "c":  # y=Rating
                agents = agent_search.order_by(Agent.wins.desc()).all()
                agents = agents[:agent_choice]
                y_ = [100 * divide(agent.wins, agent.map_ref.games) for agent in agents]
                label = "Rating"
            if len(y_) < agent_choice:
                continue
            y.append(y_)
            labels.append([agent.agent for agent in agents])
            x.append(map.map)
        plotter(x, y, label, Tournaments[tournament_choice-1], labels, n=agent_choice)

    elif title == "b":  # Title=Agent
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        agents = session.query(Agent).\
            where((Agent.tournament == "Overall") &
                  (Agent.map != "") &
                  (Agent.agent == Agents[agent_choice-1])).order_by(Agent.map).all()
        x = [agent.map for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.map_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.map_ref.games)] for agent in agents]
            label = "Rating"
        plotter(x, y, label, Agents[agent_choice-1])

    elif title == "c":  # Title=AgentOnTournament
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        tournament_choice = int(choice_check("What Tournament do you want to view " +
                                             f"{Agents[agent_choice-1]} on?\n" + tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        agents = session.query(Agent).\
            where((Agent.tournament == Tournaments[tournament_choice-1]) &
                  (Agent.map != "") &
                  (Agent.agent == Agents[agent_choice-1])).all()
        print(agents)
        x = [agent.map for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.map_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.map_ref.games)] for agent in agents]
            label = "Rating"
        plotter(x, y, label, f"{Agents[agent_choice-1]} on {Tournaments[tournament_choice-1]}")


def plot_agents_agents(Tournaments: list, tournament_msg: str, Maps: list, map_msg: str,
                       independent: str, session):
    """Function to retrieve plot agent data where the X-axis is agents. Y-axis can be
    Pickrate, Winrate or Rating. Plots can be focuses around a specific map, specific tournament or
    specific map on a specific tournament.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session"""

    title = choice_check("Choose Plot Focus\n" +
                         "a) Map\n" +
                         "b) Tournament\n" +
                         "c) Map in a Given Tournament\n",
                         ["a", "b", "c"])
    if title == "a":   # Title=Map
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        agents = session.query(Agent).\
            where((Agent.tournament == "Overall") &
                  (Agent.map == Maps[map_choice-1])).order_by(Agent.agent).all()
        x = [agent.agent for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.map_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.map_ref.games)] for agent in agents]
            label = "Rating"
        plotter(x, y, label, Maps[map_choice-1])

    elif title == "b":   # Title=Tournament
        tournament_choice = int(choice_check("What Agent do you want to view?\n" +
                                             tournament_msg, np.arange(1, len(Tournaments)+1)))
        agents = session.query(Agent).where((Agent.tournament == Tournaments[tournament_choice-1]) &
                                            (Agent.map == "")).order_by(Agent.agent).all()
        x = [agent.agent for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.tournament_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.tournament_ref.games)] for agent in agents]
            label = "Rating"
        plotter(x, y, label, Tournaments[tournament_choice-1])

    elif title == "c":  # Title=MapOnTournament
        map_choice = int(choice_check("What Agent do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        tournament_choice = int(choice_check("What Tournament do you want to view " +
                                             f"{Maps[map_choice-1]} on?\n" + tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        agents = session.query(Agent).where(
            (Agent.tournament == Tournaments[tournament_choice-1]) &
            (Agent.map == Maps[map_choice-1])).all()
        x = [agent.agent for agent in agents]
        if independent == "a":  # y=Pickrate
            y = [[100 * divide(agent.games, 2*agent.map_ref.games)] for agent in agents]
            label = "Pickrate"
        elif independent == "b":  # y=Winrate
            y = [[100 * divide(agent.wins, agent.games)] for agent in agents]
            label = "Winrate"
        elif independent == "c":  # y=Rating
            y = [[100 * divide(agent.wins, agent.map_ref.games)] for agent in agents]
            label = "Rating"
        plotter(x, y, label, f"{Maps[map_choice-1]} on {Tournaments[tournament_choice-1]}")


def plot_agents(Tournaments: list, tournament_msg: str, Maps: list, map_msg: str, Agents: list,
                agent_msg: str, session: session.Session):
    """Function to retrieve plot agent data. X-axis can be Maps, tournaments or agents. Y-axis can
    be Pickrate, Winrate or Rating.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    Agents : list[str]
    agent_msg : str
        String containing all available agents, numbered.
    session : session.Session"""

    dependent = choice_check("Choose Dependent Variable\n" +
                             "a) Tournaments\n" +
                             "b) Maps\n" +
                             "c) Agents\n",
                             ["a", "b", "c"])
    independent = choice_check("Choose Independent Variable\n" +
                               "a) Pickrate\n" +
                               "b) Winrate\n" +
                               "c) Rating\n",
                               ["a", "b", "c"])

    if dependent == "a":  # x=Tournaments
        plot_agents_tournaments(Maps, map_msg, Agents, agent_msg, independent, session)

    elif dependent == "b":  # x=Maps
        plot_agents_maps(Tournaments, tournament_msg, Agents, agent_msg, independent, session)

    elif dependent == "c":  # x=Agents
        plot_agents_agents(Tournaments, tournament_msg, Maps, map_msg, independent, session)


def plot_teams_tournaments(Maps: list, map_msg: str, Teams: list, team_msg: str, independent: str,
                           session: session.Session):
    """Function to retrieve plot agent data where the X-axis is tournaments. Y-axis can be
    Pickrate, Winrate or Rating. Plots can be focuses around a specific map, a specific team or
    a specific team on a specific map

    Parameters
    ----------
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    Teams : list[str]
    team_msg : str
        String containing all available teams, numbered.
    session : session.Session"""

    title = choice_check("Choose Plot Focus\n" +
                         "a) Map\n" +
                         "b) Team\n" +
                         "c) Team on a Given Map\n",
                         ["a", "b", "c"])

    if title == "a":  # Title=Map
        team_choice = int_input("How Many Teams Should Be Shown In Plots? (Default is 3)\n" +
                                "Note: If this number is too large no data will be shown")
        map_choice = int(choice_check("What Map do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        tournaments = session.query(Map).where((Map.tournament != "Overall") &
                                               (Map.map == Maps[map_choice-1])).all()
        labels = []
        y = []
        x = []
        for tournament in tournaments:
            team_search = session.query(Team).where((Team.tournament == tournament.tournament) &
                                                    (Team.map == tournament.map))
            # TODO Work out team rating/pickrate
            if independent == "a":  # y=Matches
                teams = team_search.order_by(Team.games.desc()).all()
                teams = teams[:team_choice]
                y_ = [team.games for team in teams]
                label = "Matches"
            elif independent == "b":  # y=Wins
                teams = session.query(Team).where(Team.map_id == tournament.id).\
                    order_by(Team.wins.desc()).all()
                teams = teams[:team_choice]
                y_ = [team.wins for team in teams]
                label = "Wins"
            elif independent == "c":  # y=Winrate
                teams = session.query(Team).where(Team.map_id == tournament.id).\
                    order_by(Team.wins.desc()).all()
                teams = teams[:team_choice]
                y_ = [100 * divide(team.wins, team.games) for team in teams]
                label = "Winrate"
            if len(y_) < team_choice:
                continue
            y.append(y_)
            labels.append([team.team for team in teams])
            x.append(tournament.tournament)
        plotter(x, y, label, Maps[map_choice-1], labels, n=team_choice)

    elif title == "b":  # Title=Team
        team_choice = int(choice_check("What team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        teams = session.query(Team).where((Team.map == "") &
                                          (Team.team == Teams[team_choice-1])).all()
        x = [team.tournament for team in teams]
        if independent == "a":  # y=Matches
            y = [[team.games] for team in teams]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[team.wins] for team in teams]
            label = "Wins"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(team.wins, team.games)] for team in teams]
            label = "Winrate"
        plotter(x, y, label, Teams[team_choice-1])

    elif title == "c":  # Title=TeamOnMap
        team_choice = int(choice_check("What team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        map_choice = int(choice_check(f"What Map do you want to view {Teams[team_choice-1]} on?\n" +
                                      map_msg, np.arange(1, len(Maps)+1)))
        tournaments = session.query(Team).where((Team.team == Teams[team_choice-1]) &
                                                (Team.map == Maps[map_choice-1])).all()
        x = [tournament.tournament for tournament in tournaments]
        if independent == "a":  # y=Matches
            y = [[tournament.games] for tournament in tournaments]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[tournament.wins] for tournament in tournaments]
            label = "Wins"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(tournament.wins, tournament.games)] for tournament in tournaments]
            label = "Winrate"
        plotter(x, y, label, f"{Teams[team_choice-1]} on {Maps[map_choice-1]}")


def plot_teams_maps(Tournaments: list, tournament_msg: str, Teams: list, team_msg: str,
                    independent: str, session):
    """Function to retrieve plot team data where the X-axis is maps. Y-axis can be
    Pickrate, Winrate or Rating. Plots can be focuses around a specific map, a specific team or
    a specific team on a specific map

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Teams : list[str]
    team_msg : str
        String containing all available teams, numbered.
    session : session.Session"""

    title = choice_check("Choose Plot Focus\n" +
                         "a) Map\n" +
                         "b) Team\n" +
                         "c) Team on a Given Map\n",
                         ["a", "b", "c"])
    if title == "a":  # Title=Tournament
        team_choice = int_input("How Many Teams Should Be Shown In Plots? (Default is 3)\n" +
                                "Note: If this number is too large no data will be shown")
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg, np.arange(1, len(Tournaments)+1)))
        maps = session.query(Map).where(Map.tournament == Tournaments[tournament_choice-1]).all()
        labels = []
        y = []
        x = []
        for map in maps:
            team_search = session.query(Team).where((Team.tournament == map.tournament) &
                                                    (Team.map == map.map))
            if independent == "a":  # y=Matches
                teams = team_search.order_by(Team.games.desc()).all()
                teams = teams[:team_choice]
                y_ = [team.games for team in teams]
                label = "Matches"
            elif independent == "b":  # y=Wins
                teams = team_search.order_by(Team.wins.desc()).all()
                teams = teams[:team_choice]
                y_ = [team.wins for team in teams]
                label = "Wins"
            elif independent == "c":  # y=Winrate
                teams = team_search.order_by(Team.wins.desc()).all()
                teams = teams[:team_choice]
                y_ = [100 * divide(team.wins, team.games) for team in teams]
                label = "Winrate"
            if len(y_) < team_choice:
                continue
            y.append(y_)
            labels.append([team.team for team in teams])
            x.append(map.map)
        plotter(x, y, label, Tournaments[tournament_choice-1], labels, n=team_choice)

    elif title == "b":  # Title=Team
        team_choice = int(choice_check("What team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        teams = session.query(Team).\
            where((Team.tournament == "Overall") &
                  (Team.map != "") &
                  (Team.team == Teams[team_choice-1])).order_by(Team.map).all()
        x = [team.map for team in teams]
        if independent == "a":  # y=Matches
            y = [[team.games] for team in teams]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[team.wins] for team in teams]
            label = "Wins"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(team.wins, team.games)] for team in teams]
            label = "Winrate"
        plotter(x, y, label, Teams[team_choice-1])

    elif title == "c":  # Title=teamOnTournament
        team_choice = int(choice_check("What team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        tournament_choice = int(choice_check("What Tournament do you want to view " +
                                             f"{Teams[team_choice-1]} on?\n" + tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        teams = session.query(Team).\
            where((Team.tournament == Tournaments[tournament_choice-1]) &
                  (Team.map != "") &
                  (Team.team == Teams[team_choice-1])).all()
        x = [team.map for team in teams]
        if independent == "a":  # y=Matches
            y = [[team.games] for team in teams]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[team.wins] for team in teams]
            label = "Wins"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(team.wins, team.games)] for team in teams]
            label = "Winrate"
        plotter(x, y, label, f"{Teams[team_choice-1]} on {Tournaments[tournament_choice-1]}")


def plot_teams_teams(Tournaments: list, tournament_msg: str, Maps: list, map_msg: str,
                     independent: str, session):
    """Function to retrieve plot team data where the X-axis is teams. Y-axis can be
    Pickrate, Winrate or Rating. Plots can be focuses around a specific map, a specific tournament
    or a specific map on a specific tournament.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    session : session.Session"""

    title = choice_check("Choose Plot Focus\n" +
                         "a) Map\n" +
                         "b) Tournament\n" +
                         "c) Map in a Given Tournament\n",
                         ["a", "b", "c"])
    if title == "a":  # Title=Map
        map_choice = int(choice_check("What Team do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        teams = session.query(Team).\
            where((Team.tournament == "Overall") &
                  (Team.map == Maps[map_choice-1])).order_by(Team.agent).all()
        x = [team.team for team in teams]
        if independent == "a":  # y=Matches
            y = [[team.games] for team in teams]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[team.wins] for team in teams]
            label = "Wins"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(team.wins, team.games)] for team in teams]
            label = "Winrate"
        plotter(x, y, label, Maps[map_choice-1])

    elif title == "b":  # Title=Tournament
        tournament_choice = int(choice_check("What Team do you want to view?\n" + tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        teams = session.query(Team).where((Team.tournament == Tournaments[tournament_choice-1]) &
                                          (Team.map == "")).order_by(Team.agent).all()
        x = [team.team for team in teams]
        if independent == "a":  # y=Matches
            y = [[team.games] for team in teams]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[team.wins] for team in teams]
            label = "Wins"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(team.wins, team.games)] for team in teams]
            label = "Winrate"
        plotter(x, y, label, Maps[map_choice-1])
        plotter(x, y, label, Tournaments[tournament_choice-1])

    elif title == "c":  # Title=MapOnTournament
        map_choice = int(choice_check("What Team do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        tournament_choice = int(choice_check("What Tournament do you want to view " +
                                             f"{Maps[map_choice-1]} on?\n" + tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        teams = session.query(Team).where(
            (Team.map == Maps[map_choice-1]) &
            (Team.tournament == Tournaments[tournament_choice-1])).all()
        x = [team.team for team in teams]
        if independent == "a":  # y=Matches
            y = [[team.games] for team in teams]
            label = "Matches"
        elif independent == "b":  # y=Wins
            y = [[team.wins] for team in teams]
            label = "Winrate"
        elif independent == "c":  # y=Winrate
            y = [[100 * divide(team.wins, team.games)] for team in teams]
            label = "Winrate"
        plotter(x, y, label, f"{Maps[map_choice-1]} on {Tournaments[tournament_choice-1]}")


def plot_teams(Tournaments: list, tournament_msg: str, Maps: list, map_msg: str, Teams: list,
               team_msg: str, session: session.Session):
    """Function to retrieve plot team data. X-axis can be Maps, tournaments or teams. Y-axis can be
    Matches, wins or winrate.

    Parameters
    ----------
    Tournaments : list[str]
    tournament_msg : str
        String containing all available tournaments, numbered.
    Maps : list[str]
    map_msg : str
        String containing all available maps, numbered.
    Teams : list[str]
    team_msg : str
        String containing all available teams, numbered.
    session : session.Session"""

    dependent = choice_check("Choose Dependent Variable\n" +
                             "a) Tournaments\n" +
                             "b) Maps\n" +
                             "c) Teams\n",
                             ["a", "b", "c"])
    independent = choice_check("Choose Independent Variable\n" +
                               "a) Matches\n" +
                               "b) Wins\n" +
                               "c) Winrate\n",
                               ["a", "b", "c"])

    if dependent == "a":  # x=Tournaments
        plot_teams_tournaments(Maps, map_msg, Teams, team_msg, independent, session)

    elif dependent == "b":  # x=Maps
        plot_teams_maps(Tournaments, tournament_msg, Teams, team_msg, independent, session)

    elif dependent == "c":  # x=Teams
        plot_teams_teams(Tournaments, tournament_msg, Maps, map_msg, independent, session)


# visualises data
def data_viewer(session):
    """Main Hub Function to determine which data should be presented and how.

    Parameters
    ----------
    session"""

    # creates options of all tournaments
    Tournaments = [tournament.tournament for tournament in session.query(Tournament)]
    tournament_msg = ""
    for n, tournament in enumerate(Tournaments):
        tournament_msg += str(n+1) + ") " + tournament + "\n"

    # creates options of all maps
    Maps = [map.map for map in session.query(Map).where(Map.tournament == "Overall").all()]
    map_msg = ""
    for n, map in enumerate(Maps):
        map_msg += str(n+1) + ") " + map + "\n"

    # creates options of all teams
    Agents = [agent.agent
              for agent in session.query(Agent).where(Map.tournament == "Overall").all()]
    agent_msg = ""
    for n, agent in enumerate(Agents):
        agent_msg += str(n+1) + ") " + agent + "\n"

    # creates options of all teams
    Teams = [team.team for team in session.query(Team).where(Map.tournament == "Overall").all()]
    team_msg = ""
    for n, team in enumerate(Teams):
        team_msg += str(n+1) + ") " + team + "\n"

    while True:
        view = choice_check("What Data do you want to view?\n" +
                            "a) Map Statistics\n" +
                            "b) Comp Statistics\n" +
                            "c) Agent Statistics\n" +
                            "d) Team Statistics\n",
                            ["a", "b", "c", "d"])
        plot = choice_check("Do you want to plot data? (y/n)\n",
                            ["y", "n"])

        if plot == "y":
            if view == "a":  # map statistics
                plot_maps(Tournaments, tournament_msg, Maps, map_msg, session)
            elif view == "b":  # comp statistics
                plot_comps(Tournaments, tournament_msg, Maps, map_msg, session)
            elif view == "c":  # agent statistics
                plot_agents(Tournaments, tournament_msg, Maps, map_msg, Agents, agent_msg, session)
            elif view == "d":  # team statistics
                plot_teams(Tournaments, tournament_msg, Maps, map_msg, Teams, team_msg, session)

        elif plot == "n":
            if view == "a":  # map statistics
                output = view_maps(Tournaments, tournament_msg, Maps, map_msg, session)

            elif view == "b":  # comp statistics
                output = view_comps(Tournaments, tournament_msg, Maps, map_msg, session)

            elif view == "c":  # agent statistics
                output = view_agents(
                    Tournaments, tournament_msg, Maps, map_msg, Agents, agent_msg, session)

            elif view == "d":  # team statistics
                output = view_teams(
                    Tournaments, tournament_msg, Maps, map_msg, Teams, team_msg, session)

            print(output)

        session.close()

        done = choice_check("Are you still viewing data? (y/n) ", ["y", "n"])
        if done == "n":
            break
