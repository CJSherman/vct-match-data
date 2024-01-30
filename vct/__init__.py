import numpy as np

from sqlalchemy.orm import sessionmaker, session
from sqlalchemy import create_engine

from .databases import Tournament, Map, Agent, Comp, Team, Match, Referall
from .functions import data_check, choice_check, int_input
from .new_game import new_game
from .viewer import data_viewer


# creates the initial maps, agents and teams tables
def setup(tournament: Tournament, session: session.Session):
    """Function to create all the required fields in the databases for a new tournament.

    Parameter
    ---------
    tournament : Tournament
        The database the contains base information of the tournament to be created.
    session : session.Session"""

    maps = tournament.map_pool.split()
    agents = tournament.agent_pool.split()
    teams = tournament.team_pool.split()
    tournament = tournament.tournament

    ovr_map = Map(tournament=tournament,
                  map="Overall",
                  games=0,
                  ct_wins=0,
                  t_wins=0)
    session.add(ovr_map)

    for agent in agents:
        ovr_agent = Agent(tournament=tournament,
                          map="Overall",
                          agent=agent,
                          games=0,
                          wins=0)
        session.add(ovr_agent)

    for team in teams:
        ovr_team = Team(tournament=tournament,
                        map="Overall",
                        team=team,
                        games=0,
                        wins=0)
        session.add(ovr_team)

    session.commit()

    for map in maps:
        map_row = Map(tournament=tournament,
                      map=map,
                      games=0,
                      ct_wins=0,
                      t_wins=0)
        session.add(map_row)

        for agent in agents:
            agent_row = Agent(tournament=tournament,
                              map=map,
                              agent=agent,
                              games=0,
                              wins=0)
            session.add(agent_row)

        for team in teams:
            team_row = Team(tournament=tournament,
                            map=map,
                            team=team,
                            games=0,
                            wins=0)
            session.add(team_row)


# reloads all match data
def data_refresh(session: session.Session):
    """Function to clear the current processed data and re-enter the data into databases. This is
    useful for if changes to how data is processed are made.

    Parameters
    ----------
    session : session.Session"""

    # clears existing tables
    maps = session.query(Map).all()
    for map in maps:
        session.delete(map)
    agents = session.query(Agent).all()
    for agent in agents:
        session.delete(agent)
    comps = session.query(Comp).all()
    for comp in comps:
        session.delete(comp)
    teams = session.query(Team).all()
    for team in teams:
        session.delete(team)

    session.commit()

    # creates entries in each table for each tournament
    tournaments = session.query(Tournament).all()
    for tournament in tournaments:
        tournament.games = 0
        setup(tournament, session)

    # adds all existing match data
    matches = session.query(Match).all()
    for match in matches:
        result = 0
        if match.team_1_score > match.team_2_score:
            result = 1

        new_game(match, result, session)


# creates a new entry in the tournaments table and accompaning records for maps, agents and teams
# TODO add check that reference exists for agents, teams and maps
def new_tournament(session: session.Session) -> str:
    """Function to take the input of the base information for a new tournament.

    Parameters
    ----------
    session : session.Session

    Returns
    -------
    str
        The name of the created tournament."""

    while True:
        tournament_name = input("Enter the Tournament Name: ")
        confirm = choice_check("Confirm This is the Tournament Name: " +
                               tournament_name + " (y/n) ",
                               ["y", "n"])
        if confirm == "y":
            break

    while True:
        map_pool = input("Enter the Tournaments Map Pool: ").upper()
        confirm = choice_check("Confirm This is the Map Pool: " + map_pool + " (y/n) ",
                               ["y", "n"])
        if confirm == "y":
            break

    while True:
        agent_pool = input("Enter the Tournaments Agent Pool: ").upper()
        confirm = choice_check("Confirm This is the Agent Pool: " + agent_pool + " (y/n) ",
                               ["y", "n"])
        if confirm == "y":
            break

    while True:
        team_pool = input("Enter the Tournaments Teams: ").upper()
        confirm = choice_check("Confirm This is the Team List: " + team_pool + " (y/n) ",
                               ["y", "n"])
        if confirm == "y":
            break

    tournament = Tournament(id=tournament_name,
                            map_pool=map_pool,
                            agent_pool=agent_pool,
                            team_pool=team_pool)
    session.add(tournament)
    session.commit()

    setup(tournament)

    return tournament_name


# selects the tournament for which to add data
def select_tournament(session: session.Session) -> Tournament:
    """Function to select which tournament data should be added to, allows options to choose an
    existing tournament or to create a new tournament.

    Parameters
    ----------
    session : session.Session

    Returns
    -------
    Tournament
        The object of the chosen tournament."""

    choice = choice_check("Select Option:\n" +
                          "a) Create new tournament database\n" +
                          "b) Open existing tournament\n",
                          ["a", "b"])

    if choice == "a":  # new tournament
        tournament_name = new_tournament(session)

    elif choice == "b":  # existing tournament
        tournament_msg = ""
        tournaments = session.query(Tournament).all()
        for n, tournament in enumerate(tournaments):
            tournament_msg += str(n+1) + ") " + tournament.id + "\n"

        tournament_id = int(choice_check("Which tournament do you want to open?\n" +
                                         tournament_msg,
                                         np.arange(1, len(tournaments)+1)))
        tournament_name = tournaments[tournament_id-1].id

    tournament = session.query(Tournament).filter_by(id=tournament_name).first()

    return tournament


# enters new match data to match table
def data_add(tournament: Tournament, session: session.Session):
    """Function to enter data for a new tournament match. Cleans data and makes sure it fits the
    correct format

    Parameters
    ----------
    tournament : Tournament
        The object of the tournament the entered match belongs to.
    session : session.Session"""

    maps = tournament.map_pool.split()
    agents = tournament.agent_pool.split()
    teams = tournament.team_pool.split()

    while True:
        while True:
            data = input("Enter Match Information:\n")
            datasplit = data.split()
            # ensures right amount of data is given
            if len(datasplit) == 16:
                break
            else:
                print("Please Enter Data in Correct Format")

        # checks the map is in the tournament
        map = data_check("Enter a Valid Map for " + datasplit[0] +
                         ":\n", maps, datasplit[0].upper())
        map = [map, tournament.id + map]

        # checks the team is in the tournament
        team1 = data_check("Enter a valid team for " + datasplit[1] +
                           ":\n", teams, datasplit[1].upper())
        team2 = data_check("Enter a valid team for " + datasplit[5] +
                           ":\n", teams, datasplit[5].upper())
        team = [team1, team2]

        # checks the score is possible
        team1score = int_input((team1 + "'s Score"), datasplit[2])
        team2score = int_input((team2 + "'s Score"), datasplit[4])
        while (team1score < 0 or team2score < 0 or not
               ((team1score + team2score <= 24 and
                 (team1score == 13 or team2score == 13) and
                 abs(team1score-team2score) >= 2) or
                (team1score + team2score > 24 and abs(team1score - team2score) == 2))):
            score = input("Please Enter a Valid Score\n").split()
            team1score = int_input((team1 + "'s Score"), score[0])
            team2score = int_input((team2 + "'s Score"), score[1])
        team1half = int_input((team1 + "'s Score at Half Time"), datasplit[3])
        team2half = 12-team1half
        while team1half < 0 or team1half > 12 or team1half > team1score or team2half > team2score:
            team1half = int_input(team1 + "'s Score at Half Time")
            team2half = 12-team1half
        if team1score+team2score <= 24:
            team1half2 = team1score - team1half
            team2half2 = team2score - team2half
        else:
            team1half2, team2half2 = team2half, team1half
        score = [team1score, team2score, team1half, team2half, team1half2, team2half2]

        # makes sure each agent is real and the comps are possible
        team1_agents = agents.copy()
        team1comp = datasplit[-10:-5]
        team1comp.sort()
        team1comp = [agent.upper() for agent in team1comp]
        for n, agent in enumerate(team1comp):
            agent = data_check("Enter a valid agent for " + agent + "\n", team1_agents, agent)
            team1comp[n] = agent
            team1_agents.remove(agent)
        team1comp.append(map[1] + "".join(team1comp))

        team2_agents = agents.copy()
        team2comp = datasplit[-5:]
        team2comp.sort()
        team2comp = [agent.upper() for agent in team2comp]
        for n, agent in enumerate(team2comp):
            agent = data_check("Enter a valid agent for " + agent + "\n", team2_agents, agent)
            team2comp[n] = agent
            team2_agents.remove(agent)
        team2comp.append(map[1] + "".join(team2comp))

        # adds match to matches table
        match = Match(tournament=tournament.id,
                      map=map[0],
                      team_1=team[0],
                      team_2=team[1],
                      team_1_score=score[0],
                      team_2_score=score[1],
                      team_1_half=score[2],
                      team_2_half=score[3],
                      team_1_half_2=score[4],
                      team_2_half_2=score[4],
                      team_1_pick_1=team1comp[0],
                      team_1_pick_2=team1comp[1],
                      team_1_pick_3=team1comp[2],
                      team_1_pick_4=team1comp[3],
                      team_1_pick_5=team1comp[4],
                      team_2_pick_1=team2comp[0],
                      team_2_pick_2=team2comp[1],
                      team_2_pick_3=team2comp[2],
                      team_2_pick_4=team2comp[3],
                      team_2_pick_5=team2comp[4],
                      map_id=map[1],
                      team_1_id=map[1]+team[0],
                      team_2_id=map[1]+team[1],
                      team_1_agent_1_id=map[1]+team1comp[0],
                      team_1_agent_2_id=map[1]+team1comp[1],
                      team_1_agent_3_id=map[1]+team1comp[2],
                      team_1_agent_4_id=map[1]+team1comp[3],
                      team_1_agent_5_id=map[1]+team1comp[4],
                      team_2_agent_1_id=map[1]+team2comp[0],
                      team_2_agent_2_id=map[1]+team2comp[1],
                      team_2_agent_3_id=map[1]+team2comp[2],
                      team_2_agent_4_id=map[1]+team2comp[3],
                      team_2_agent_5_id=map[1]+team2comp[4],
                      team_1_comp_id=team1comp[5],
                      team_2_comp_id=team2comp[5])
        session.add(match)
        session.commit()

        # calculates the result for team 1
        result = 0
        if match.team_1_score > match.team_2_score:
            result = 1

        # updates all tables
        new_game(match, result, session)

        done = choice_check("Are you still adding data? (y/n)\n", ["y", "n"])
        if done == "n":
            break


def add_referall(type: str, session: session.Session):
    """Function to add a new map, agent or team to the Referall table.
    Parameters
    ----------
    type : {"MAP", "AGENT", "TEAM"}
    session : session.Session"""

    name = input(f"Enter {type.title()} Name: ").upper()
    short = input(f"Enter Abbreviation for {name.title()}: ").upper()

    shorthand = Referall(name=name,
                         abbreviation=short,
                         type=type)
    session.add(shorthand)
    session.commit()
    session.close()


# loops options until not needed
def game_loop(database: str):
    """Main Function loop to call required destinations.

    Parameters
    ----------
    database : str
        The name of the database file where all data is stored."""

    while True:
        engine = create_engine(f"sqlite:///{database}.db", echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()

        task = choice_check("What do you want to do?\n" +
                            "a) Add new data\n" +
                            "b) View data\n" +
                            "c) Update data\n",
                            ["a", "b", "c"])

        if task == "a":  # add new data
            while True:
                match_or_agent = choice_check("What do you want to add?\n" +
                                              "a) A new VCT Match\n" +
                                              "b) A new Map\n" +
                                              "c) A new Agent\n" +
                                              "d) A new Team\n",
                                              ["a", "b", "c", "d"])
                if match_or_agent == "a":
                    tournament = select_tournament(session)
                    data_add(tournament, session)
                elif match_or_agent == "b":
                    add_referall("MAP", session)
                elif match_or_agent == "c":
                    add_referall("AGENT", session)
                elif match_or_agent == "d":
                    add_referall("TEAM", session)

                done = choice_check("Would you like to add something else? (y/n) ",
                                    ["y", "n"])
                if done == "n":
                    break

        elif task == "b":  # view data
            data_viewer(session)

        elif task == "c":  # update data
            data_refresh(session)

        session.close()

        done = choice_check("Would you like to do anything else? (y/n) ",
                            ["y", "n"])
        if done == "n":
            break
