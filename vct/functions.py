from sqlalchemy import create_engine
from sqlalchemy.orm import session

from .databases import Tournament, Map, Agent, Team, Referall, base


# checks if a choice was an acceptable option
def choice_check(question: str, options: list[str | int]) -> str:
    """Function to check if an input is in a given set.

    Parameters
    ----------
    question : str
    options : list[str | int]

    Returns
    -------
    str
        The Result."""

    while True:
        choice = input(question).lower()
        if choice in str(options) and len(choice) > 0:
            break

    return choice


# checks if data is valid
def data_check(question: str, options: list[str], data: str) -> str:
    """Function to check if an input is in a given set.

    Parameters
    ----------
    question : str
    options : list[str]
    data : str
        The initial input.

    Returns
    -------
    str
        The Result."""

    while data not in options:
        data = input(question).upper()
    return data


# checks if an expected integer input is an integer
def int_input(quantity: str, result=None) -> int:
    """Function to confirm an input is an integer.

    Parameter
    ---------
    quantity : str
        The question to be asked.
    result
        The current given answer.

    Returns
    -------
    int
        The answer to the question."""

    msg = "Please Enter an Integer Value For " + quantity + "\n"
    if not result:
        result = input(msg)
    while True:
        try:
            result = int(result)
            break
        except ValueError:
            result = input(msg)
    return result


# divides 2 numbers, returning 0 if denominator is 0
def divide(numerator: int, denominator: int, offset=0) -> float:
    """Function to divide two values and return 0 if the denominator is 0 (e.g. K/D for 10/0 is 10).

    Parameters
    ----------
    numerator : int
    denominator : int
    offset : float, default: 0
        How much to shift the result by.

    Returns
    -------
    result : float"""

    try:
        result = numerator / denominator + offset
    except ZeroDivisionError:
        result = 0
    return result


# Creates a new database with a given name
def create_database(name, session):
    engine = create_engine(f"sqlite:///{name}.db", echo=True)
    base.metadata.create_all(bind=engine)
    tournaments = [tournament.tournament for tournament in session.query(Tournament)]
    if "Overall" not in tournaments:
        maps = " - ".join([referall.name for referall in session.query(Referall).where(
            Referall.type == "MAP")])
        agents = " - ".join([referall.name for referall in session.query(Referall).where(
            Referall.type == "AGENT")])
        teams = " - ".join([referall.name for referall in session.query(Referall).where(
            Referall.type == "TEAM")])

        tournament = Tournament(tournament="Overall",
                                games=0,
                                map_pool=maps,
                                agent_pool=agents,
                                team_pool=teams)
        session.add(tournament)
        session.commit()


# creates the initial maps, agents and teams tables
def setup(tournament: Tournament, session: session.Session):
    """Function to create all the required fields in the databases for a new tournament.

    Parameter
    ---------
    tournament : Tournament
        The database the contains base information of the tournament to be created.
    session : session.Session"""

    maps = tournament.map_pool.split(" - ")
    agents = tournament.agent_pool.split(" - ")
    teams = tournament.team_pool.split(" - ")
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

    session.commit()
