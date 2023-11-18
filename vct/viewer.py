import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from sqlalchemy.orm import session
from collections import Counter

from .databases import Tournament, Map, Agent, Comp, Team
from .functions import choice_check, divide


def view_maps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
              session: session.Session) -> str:
    tournaments_or_maps = choice_check("How do you want to view Map stats?\n" +
                                       "a) By Maps\n" +
                                       "b) By Tournaments\n",
                                       ["a", "b"])

    if tournaments_or_maps == "a":  # by maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        # list of maps that were played in the chosen tournament
        maps = session.query(Map).where(Map.tournament == Tournaments[tournament_choice-1]).\
            order_by(Map.games.desc()).all()
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
        maps = session.query(Map).where(Map.map == Maps[map_choice-1]).all()
        output = "Tournament{:10s}Pickrate{:>2s}Sidedness\n".format("", "")
        for map in maps:
            pickrate = divide(map.games, map.tournament_ref.games)
            sidedness = divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5)
            output += "{:<20s}{:>7.2f}%{:>10.2f}%\n".format(
                map.tournament, 100*pickrate, 100*sidedness)

    return output


def view_comps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
               session: session.Session) -> str:
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
        map = session.query(Map).where(
            Map.id == (Tournaments[tournament_choice-1] + Maps[map_choice-1])).first()
        # list of comps played in the chosen tournament on the chosen map
        comps = session.query(Comp).where(
            Comp.map_id == (Tournaments[tournament_choice-1] + Maps[map_choice-1])).\
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
        Comps_list = ["{} {} {} {} {}".format(
            comp.agent_1, comp.agent_2, comp.agent_3, comp.agent_4, comp.agent_5)
                      for comp in session.query(Comp).where(
                        Comp.tournament == Tournaments[tournament_choice-1]).all()]
        Comps = list(set(Comps_list))
        Comps = sorted(Comps, key=Counter(Comps_list).get, reverse=True)
        comp_msg = ""
        for n, comp in enumerate(Comps):
            comp_msg += "{}) {}\n".format(n+1, comp)
        comp_choice = int(choice_check("What Comp do you want to view?\n" + comp_msg,
                                       np.arange(1, len(Comps)+1)))
        # list comp objects of the chosen comp and tournament
        comps = session.query(Comp).where(
            (Comp.tournament == Tournaments[tournament_choice-1]) &
            (Comp.ref == Comps[comp_choice-1])).order_by(Comp.wins/Comp.games).all()
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
        Comps_list = ["{} {} {} {} {}".format(
            comp.agent_1, comp.agent_2, comp.agent_3, comp.agent_4, comp.agent_5)
                      for comp in session.query(Comp).where(Comp.map == Maps[map_choice-1]).all()]
        Comps = list(set(Comps_list))
        Comps = sorted(Comps, key=Counter(Comps_list).get, reverse=True)
        comp_msg = ""
        for n, comp in enumerate(Comps):
            comp_msg += "{}) {}\n".format(n+1, comp)
        comp_choice = int(choice_check("What Comp do you want to view?\n" + comp_msg,
                                       np.arange(1, len(Comps)+1)))
        # list of comp objects of the chosen comp and map
        comps = session.query(Comp).where(
            (Comp.map == Maps[map_choice-1]) & (Comp.ref == Comps[comp_choice-1])).all()
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
        map = session.query(Map).where(
            Map.id == (Tournaments[tournament_choice-1] + Maps[map_choice-1])).first()
        # list of agents played in the chosen tournament on the chosen map
        agents = session.query(Agent).where(
            Agent.map_id == (Tournaments[tournament_choice-1] + Maps[map_choice-1])).\
            order_by((Agent.wins/map.games).desc()).all()
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
            (Agent.agent == Agents[agent_choice-1])).order_by((Agent.wins/Agent.games).desc()).all()
        output = "Map{:7s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for agent in agents:
            pickrate = divide(agent.games, 2*agent.map_ref.games)
            winrate = divide(agent.wins, agent.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                agent.map, 100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_agents == "c":  # tournaments
        map_choice = int(choice_check("What Tournament do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        agent_choice = int(choice_check("What Agent do you want to view?\n" + agent_msg,
                                        np.arange(1, len(Agents)+1)))
        # list of agent objects of the chosen agent and map
        agents = session.query(Agent).where(
            (Agent.map == Maps[map_choice-1]) & (Agent.agent == Agents[agent_choice-1])).all()
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
            Map.id == (Tournaments[tournament_choice-1] + Maps[map_choice-1])).first()
        # list of teams in the chosen tournament on the chosen map
        teams = session.query(Team).where(
            Team.map_id == (Tournaments[tournament_choice-1] + Maps[map_choice-1])).\
            order_by((Team.wins/map.games).desc()).all()
        output = "Team{:11s}Games{:3s}Winrate{:4s}Rating\n".format("", "", "")
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
            (Team.team == Teams[team_choice-1])).order_by((Team.wins/Team.games).desc()).all()
        output = "Map{:7s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for team in teams:
            pickrate = divide(team.games, 2*team.map_ref.games)
            winrate = divide(team.wins, team.games)
            rating = pickrate * winrate * 200
            output += "{:<10s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                team.map, 100*pickrate, 100*winrate, rating)

    elif tournaments_maps_or_teams == "c":  # tournaments
        map_choice = int(choice_check("What Tournament do you want to view?\n" + map_msg,
                                      np.arange(1, len(Maps)+1)))
        team_choice = int(choice_check("What Team do you want to view?\n" + team_msg,
                                       np.arange(1, len(Teams)+1)))
        # list of team objects of the chosen team and map
        teams = session.query(Team).where(
            (Team.map == Maps[map_choice-1]) & (Team.team == Teams[team_choice-1])).all()
        output = "Tournament{:10s}Pickrate{:<2s}Winrate{:<3s}Rating\n".format("", "", "")
        for team in teams:
            pickrate = divide(team.games, 2*team.map_ref.games)
            winrate = divide(team.wins, team.games)
            rating = pickrate * winrate * 200
            output += "{:<20s}{:>7.2f}%{:>8.2f}%{:>9.0f}\n".format(
                team.tournament, 100*pickrate, 100*winrate, rating)

    return output


def plot_maps(Tournaments: list[str], tournament_msg: str, Maps: list[str], map_msg: str,
              session: session.Session):
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
        maps = session.query(Map).where(Map.map == Maps[map_choice-1]).all()
        x = [map.tournament for map in maps]

        if independent == "a":  # y=Pickrate
            y = [divide(map.games, map.tournament_ref.games) for map in maps]
            label = "Pickrate"
        elif independent == "b":  # y=Sidedness
            y = [divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5) for map in maps]
            label = "Sidedness"

        plt.figure()
        plt.title(Maps[map_choice-1])
        plt.ylabel(label)
        plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
        plt.xticks(rotation="vertical")
        plt.tight_layout()
        plt.show()

    elif dependent == "b":  # x=Maps
        tournament_choice = int(choice_check("What Tournament do you want to view?\n" +
                                             tournament_msg,
                                             np.arange(1, len(Tournaments)+1)))
        maps = session.query(Map).where(Map.tournament == Tournaments[tournament_choice-1]).all()
        x = [map.map for map in maps]

        if independent == "a":  # y=Pickrate
            y = [divide(map.games, map.tournament_ref.games) for map in maps]
            label = "Pickrate"
        elif independent == "b":  # y=Sidedness
            y = [divide(map.ct_wins, map.ct_wins + map.t_wins, -0.5) for map in maps]
            label = "Sidedness"

        plt.figure()
        plt.title(Tournaments[tournament_choice-1])
        plt.ylabel(label)
        plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
        plt.xticks(rotation="vertical")
        plt.tight_layout()
        plt.show()


def plot_comps(Tournaments: list, Maps: list, session: session.Session):
    dependent = choice_check("Choose Dependent Variable\n" +
                             "a) Tournaments\n" +
                             "b) Maps\n" +
                             "c) Comps\n",
                             ["a", "b", "c"])
    independent = choice_check("Choose Independent Variable\n" +
                               "a) Pickrate\n" +
                               "b) Winrate\n" +
                               "c) Rating\n",
                               ["a", "b", "c"])

    if dependent == "a":  # x=Tournaments
        for map_ in Maps:
            Comps_list = ["{} {} {} {} {}".format(
                comp.agent_1, comp.agent_2, comp.agent_3, comp.agent_4, comp.agent_5)
                for comp in session.query(Comp).where(Comp.map == map_).all()]
            Comps = list(set(Comps_list))
            Comps = sorted(Comps, key=Counter(Comps_list).get, reverse=True)
            for comp_ in Comps:
                comps = session.query(Comp).where((Comp.map == map_) & (Comp.ref == comp_)).all()
                x = [comp.tournament for comp in comps]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(comp.games, 2*comp.map_ref.games) for comp in comps]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(comp.wins, comp.games) for comp in comps]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(comp.wins, comp.map_ref.games) for comp in comps]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(map_, comp_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()

    elif dependent == "b":  # x=Maps
        for tournament_ in Tournaments:
            Comps_list = ["{} {} {} {} {}".format(
                comp.agent_1, comp.agent_2, comp.agent_3, comp.agent_4, comp.agent_5)
                for comp in session.query(Comp).where(Comp.tournament == tournament_).all()]
            Comps = list(set(Comps_list))
            Comps = sorted(Comps, key=Counter(Comps_list).get, reverse=True)
            for comp_ in Comps:
                comps = session.query(Comp).where(
                    (Comp.tournament == tournament_) & (Comp.ref == comp_)).all()
                x = [comp.map for comp in comps]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(comp.games, 2*comp.map_ref.games) for comp in comps]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(comp.wins, comp.games) for comp in comps]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(comp.wins, comp.map_ref.games) for comp in comps]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(tournament_, comp_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()

    elif dependent == "c":  # x=Comps
        for tournament_ in Tournaments:
            for map_ in Maps:
                comps = session.query(Comp).where(
                    (Comp.tournament == tournament_) & (Comp.map == map_)).all()
                x = [comp.ref for comp in comps]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(comp.games, 2*comp.map_ref.games) for comp in comps]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(comp.wins, comp.games) for comp in comps]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(comp.wins, comp.map_ref.games) for comp in comps]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(tournament_, map_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()


def plot_agents(Tournaments: list, Maps: list, Agents: list, session: session.Session):
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
        for map_ in Maps:
            for agent_ in Agents:
                agents = session.query(Agent).where(
                    (Agent.map == map_) & (Agent.agent == agent_)).all()
                x = [agent.tournament for agent in agents]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(agent.games, 2*agent.map_ref.games) for agent in agents]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(agent.wins, agent.games) for agent in agents]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(agent.wins, agent.map_ref.games) for agent in agents]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(map_, agent_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()

    elif dependent == "b":  # x=Maps
        for tournament_ in Tournaments:
            for agent_ in Agents:
                agents = session.query(Agent).where(
                    (Agent.tournament == tournament_) & (Agent.agent == agent_)).all()
                x = [agent.map for agent in agents]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(agent.games, 2*agent.map_ref.games) for agent in agents]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(agent.wins, agent.games) for agent in agents]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(agent.wins, agent.map_ref.games) for agent in agents]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(tournament_, agent_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()

    elif dependent == "c":  # x=Agents
        for tournament_ in Tournaments:
            for map_ in Maps:
                agents = session.query(Agent).where(
                    (Agent.tournament == tournament_) & (Agent.map == map_)).all()
                x = [agent.agent for agent in agents]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(agent.games, 2*agent.map_ref.games) for agent in agents]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(agent.wins, agent.games) for agent in agents]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(agent.wins, agent.map_ref.games) for agent in agents]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(tournament_, map_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()


def plot_teams(Tournaments: list, Maps: list, Teams: list, session: session.Session):
    dependent = choice_check("Choose Dependent Variable\n" +
                             "a) Tournaments\n" +
                             "b) Maps\n" +
                             "c) Teams\n",
                             ["a", "b", "c"])
    independent = choice_check("Choose Independent Variable\n" +
                               "a) Pickrate\n" +
                               "b) Winrate\n" +
                               "c) Rating\n",
                               ["a", "b", "c"])

    if dependent == "a":  # x=Tournaments
        for map_ in Maps:
            for team_ in Teams:
                teams = session.query(Team).where(
                    (Team.map == map_) & (Team.team == team_)).all()
                x = [team.tournament for team in teams]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(team.games, 2*team.map_ref.games) for team in teams]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(team.wins, team.games) for team in teams]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(team.wins, team.map_ref.games) for team in teams]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(map_, team_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()

    elif dependent == "b":  # x=Maps
        for tournament_ in Tournaments:
            for team_ in Teams:
                teams = session.query(Team).where(
                    (Team.tournament == tournament_) & (Team.team == team_)).all()
                x = [team.map for team in teams]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(team.games, 2*team.map_ref.games) for team in teams]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(team.wins, team.games) for team in teams]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(team.wins, team.map_ref.games) for team in teams]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(tournament_, team_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()

    elif dependent == "c":  # x=teams
        for tournament_ in Tournaments:
            for map_ in Maps:
                teams = session.query(Team).where(
                    (Team.tournament == tournament_) & (Team.map == map_)).all()
                x = [team.team for team in teams]
                if len(x) < 3:
                    continue

                if independent == "a":  # y=Pickrate
                    y = [divide(team.games, 2*team.map_ref.games) for team in teams]
                    label = "Pickrate"
                elif independent == "b":  # y=Winrate
                    y = [divide(team.wins, team.games) for team in teams]
                    label = "Winrate"
                elif independent == "c":  # y=Rating
                    y = [100 * divide(team.wins, team.map_ref.games) for team in teams]
                    label = "Rating"

                plt.figure()
                plt.title("{} {}".format(tournament_, map_))
                plt.ylabel(label)
                plt.bar(x, y, color=mcolors.TABLEAU_COLORS)
                plt.xticks(rotation="vertical")
                plt.tight_layout()
                plt.show()


# visualises data
def data_viewer(session):
    # creates options of all tournaments
    Tournaments = []
    for tournament in session.query(Tournament):
        Tournaments.append(tournament.id)
    tournament_msg = ""
    for n, tournament in enumerate(Tournaments):
        tournament_msg += str(n+1) + ") " + tournament + "\n"

    # creates options of all maps
    Maps = []
    for map in session.query(Map.map).distinct():
        Maps.append(map.map)
    map_msg = ""
    for n, map in enumerate(Maps):
        map_msg += str(n+1) + ") " + map + "\n"

    # creates options of all agents
    Agents = []
    for agent in session.query(Agent.agent).distinct():
        Agents.append(agent.agent)
    agent_msg = ""
    for n, agent in enumerate(Agents):
        agent_msg += str(n+1) + ") " + agent + "\n"

    # creates options of all teams
    Teams = []
    for team in session.query(Team.team).distinct():
        Teams.append(team.team)
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
                plot_comps(Tournaments, Maps, session)
            elif view == "c":  # agent statistics
                plot_agents(Tournaments, Maps, Agents, session)
            elif view == "d":  # team statistics
                plot_teams(Tournaments, Maps, Teams, session)

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
