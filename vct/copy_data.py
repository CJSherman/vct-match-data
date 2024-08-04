from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .databases import Tournament, Match, Referall


def copy_data(old_db: str, new_db: str):
    """
    Copys a database for backing up purposes.

    Parameters
    ----------
    old_db : str
        Name of the old database.
    new_db : str
        Name of the new database.
    """
    engine_1 = create_engine(f"sqlite:///{old_db}.db", echo=True)
    Session = sessionmaker(bind=engine_1)
    session = Session()

    engine_2 = create_engine(f"sqlite:///{new_db}.db", echo=True)
    Session_2 = sessionmaker(bind=engine_2)
    session_2 = Session_2()

    tournaments = session.query(Tournament).all()
    matches = session.query(Match).all()
    referalls = session.query(Referall).all()

    for referall in referalls:
        new_ref = Referall(name=referall.name,
                           abbreviation=referall.abbreviation,
                           type=referall.type)
        session_2.add(new_ref)

    for tournament in tournaments:
        new_tour = Tournament(tournament=tournament.tournament,
                              games=tournament.games,
                              map_pool=tournament.map_pool,
                              agent_pool=tournament.agent_pool,
                              team_pool=tournament.team_pool)
        session_2.add(new_tour)

    for match in matches:
        new_match = Match(tournament=match.tournament,
                          map=match.map,
                          team_1=match.team_1,
                          team_1_score=match.team_1_score,
                          team_2_score=match.team_2_score,
                          team_2=match.team_2,
                          team_1_half=match.team_1_half,
                          team_2_half=match.team_2_half,
                          team_1_half_2=match.team_1_half_2,
                          team_2_half_2=match.team_2_half_2,
                          team_1_agent_1=match.team_1_agent_1,
                          team_1_agent_2=match.team_1_agent_2,
                          team_1_agent_3=match.team_1_agent_3,
                          team_1_agent_4=match.team_1_agent_4,
                          team_1_agent_5=match.team_1_agent_5,
                          team_2_agent_1=match.team_2_agent_1,
                          team_2_agent_2=match.team_2_agent_2,
                          team_2_agent_3=match.team_2_agent_3,
                          team_2_agent_4=match.team_2_agent_4,
                          team_2_agent_5=match.team_2_agent_5)
        session_2.add(new_match)

    session_2.commit()
