import numpy as np

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from .databases import Tournament, Map, Agent, Comp, Team, Match, Referall
from .functions import data_check, choice_check, int_input, setup
from .new_game import new_game
from .viewer import data_viewer
from .get_data import VLRScrape


def data_refresh(session: Session) -> None:
    """
    Function to clear the current processed data and re-enter the data into databases. This is
    useful for if changes to how data is processed are made.

    Parameters
    ----------
    session : Session
    """

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

    tournaments = session.query(Tournament).all()
    for tournament in tournaments:

        if tournament.tournament == "Overall":
            tournament.map_pool = " - ".join([referall.name for referall in session.query(
                Referall).where(Referall.type == "MAP")])
            tournament.agent_pool = " - ".join([referall.name for referall in session.query(
                Referall).where(Referall.type == "AGENT")])
            tournament.team_pool = " - ".join([referall.name for referall in session.query(
                Referall).where(Referall.type == "TEAM")])
            session.commit()
        tournament.games = 0
        setup(tournament, session)

    matches = session.query(Match).all()
    for match in matches:
        result = 0
        if match.team_1_score > match.team_2_score:
            result = 1

        new_game(match, result, session)


def new_tournament(session: Session) -> str:
    """
    Function to take the input of the base information for a new tournament.

    Parameters
    ----------
    session : Session

    Returns
    -------
    str
        The name of the created tournament.
    """

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
        if agent_pool == "ALL":
            all_agents = session.query(Referall).where(Referall.type == "AGENT").all()
            agent_pool = " ".join([agents.name for agents in all_agents])
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

    tournament = Tournament(tournament=tournament_name,
                            games=0,
                            map_pool=map_pool,
                            agent_pool=agent_pool,
                            team_pool=team_pool)
    session.add(tournament)
    session.commit()

    setup(tournament, session)

    return tournament_name


def select_tournament(session: Session) -> Tournament:
    """
    Function to select which tournament data should be added to, allows options to choose an
    existing tournament or to create a new tournament.

    Parameters
    ----------
    session : Session

    Returns
    -------
    Tournament
        The object of the chosen tournament.
    """

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
            tournament_msg += str(n+1) + ") " + tournament.tournament + "\n"

        tournament_id = int(choice_check("Which tournament do you want to open?\n" +
                                         tournament_msg,
                                         np.arange(1, len(tournaments)+1)))
        tournament_name = tournaments[tournament_id-1].tournament

    tournament = session.query(Tournament).filter_by(tournament=tournament_name).first()

    return tournament


def data_add(tournament: Tournament, session: Session) -> None:
    """
    Function to enter data for a new tournament match. Cleans data and makes sure it fits the
    correct format

    Parameters
    ----------
    tournament : Tournament
        The object of the tournament the entered match belongs to.
    session : Session
    """

    maps = tournament.map_pool.split()
    agents = tournament.agent_pool.split()
    teams = tournament.team_pool.split()

    while True:
        while True:
            data = input("Enter Match Information:\n")
            datasplit = data.split()
            if len(datasplit) == 16:
                break
            else:
                print("Please Enter Data in Correct Format")

        map = data_check("Enter a Valid Map for " + datasplit[0] +
                         ":\n", maps, datasplit[0].upper())

        team1 = data_check("Enter a valid team for " + datasplit[1] +
                           ":\n", teams, datasplit[1].upper())
        team2 = data_check("Enter a valid team for " + datasplit[5] +
                           ":\n", teams, datasplit[5].upper())
        team = [team1, team2]

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
        team2half = 12 - team1half
        while team1half < 0 or team1half > 12 or team1half > team1score or team2half > team2score:
            team1half = int_input(team1 + "'s Score at Half Time")
            team2half = 12 - team1half
        if team1score+team2score <= 24:
            team1half2 = team1score - team1half
            team2half2 = team2score - team2half
        else:
            team1half2, team2half2 = team2half, team1half
        score = [team1score, team2score, team1half, team2half, team1half2, team2half2]

        team1_agents = agents.copy()
        team1comp = datasplit[-10:-5]
        team1comp = [agent.upper() for agent in team1comp]
        for n, agent in enumerate(team1comp):
            agent = data_check("Enter a valid agent for " + agent + "\n", team1_agents, agent)
            team1comp[n] = agent
            team1_agents.remove(agent)
        team1comp.sort()

        team2_agents = agents.copy()
        team2comp = datasplit[-5:]
        team2comp = [agent.upper() for agent in team2comp]
        for n, agent in enumerate(team2comp):
            agent = data_check("Enter a valid agent for " + agent + "\n", team2_agents, agent)
            team2comp[n] = agent
            team2_agents.remove(agent)
        team2comp.sort()

        match = Match(tournament=tournament.tournament,
                      map=map,
                      team_1=team[0],
                      team_2=team[1],
                      team_1_score=score[0],
                      team_2_score=score[1],
                      team_1_half=score[2],
                      team_2_half=score[3],
                      team_1_half_2=score[4],
                      team_2_half_2=score[4],
                      team_1_agent_1=team1comp[0],
                      team_1_agent_2=team1comp[1],
                      team_1_agent_3=team1comp[2],
                      team_1_agent_4=team1comp[3],
                      team_1_agent_5=team1comp[4],
                      team_2_agent_1=team2comp[0],
                      team_2_agent_2=team2comp[1],
                      team_2_agent_3=team2comp[2],
                      team_2_agent_4=team2comp[3],
                      team_2_agent_5=team2comp[4])
        session.add(match)
        session.commit()

        result = 0
        if match.team_1_score > match.team_2_score:
            result = 1

        new_game(match, result, session)

        done = choice_check("Are you still adding data? (y/n)\n", ["y", "n"])
        if done == "n":
            break


def add_referall(type: str, session: Session) -> None:
    """
    Function to add a new map, agent or team to the Referall table.
    Parameters
    ----------
    type : {"MAP", "AGENT", "TEAM"}
    session : Session
    """

    name = input(f"Enter {type.title()} Name: ").upper()
    short = input(f"Enter Abbreviation for {name.title()}: ").upper()

    shorthand = Referall(name=name,
                         abbreviation=short,
                         type=type)
    session.add(shorthand)
    session.commit()
    session.close()


def vlr_scraper(session) -> None:
    scraper = VLRScrape(session)
    while True:
        url = input("Enter the URL to be scraped")
        split_url = url.split("/")
        if len(split_url) < 4:
            print("INVALID URL: Must be a www.vlr.gg match or event url")
        elif split_url[2] == "www.vlr.gg":
            if split_url[3] == "event":
                scraper.add_tournaments(url)
            else:
                scraper.add_matches(url)
        else:
            print("INVALID URL: Must be a www.vlr.gg match or event url")

        done = choice_check("Would you like to do anything else? (y/n) ",
                            ["y", "n"])
        if done == "n":
            break
    scraper.find_match_pages()
    scraper.find_match_data()
    left_matches = "\n".join(scraper.match_urls)
    print(f"The following matches were not scraped:\n {left_matches}")


def game_loop(database: str) -> None:
    """
    Main Function loop to call required destinations.

    Parameters
    ----------
    database : str
        The name of the database file where all data is stored.
    """

    while True:
        engine = create_engine(f"sqlite:///{database}.db")
        Session = sessionmaker(bind=engine)
        session = Session()

        task = choice_check("What do you want to do?\n" +
                            "a) Add new data\n" +
                            "b) View data\n" +
                            "c) Update data\n",
                            ["a", "b", "c"])

        if task == "a":  # add new data
            while True:
                website = choice_check("Where do you want to scrape from?\n" +
                                       "a) VLR.gg\n",
                                       ["a"])
                if website == "a":
                    vlr_scraper(session)

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
