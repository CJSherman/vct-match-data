from .databases import Comp, Match, Agent, Map, Team, Tournament


# adjusts map data from a new map
def new_game_map(match: Match, session):
    """Function to Update the Map Table from data in a new Match.

    Parameters
    ----------
    match : Match
        The Match object to update the table from.
    session"""

    specific_map = match.map_ref
    ovr = session.query(Map).where((Map.tournament == "Overall") &
                                   (Map.map == "Overall")).first()
    ovr_map = session.query(Map).where((Map.tournament == "Overall") &
                                       (Map.map == specific_map.map)).first()
    ovr_tour = session.query(Map).where((Map.tournament == match.tournament) &
                                        (Map.map == "Overall")).first()

    maps = [specific_map, ovr, ovr_map, ovr_tour]
    for map in maps:
        map.games += 1
        map.ct_wins += match.team_1_half + match.team_2_half_2
        map.t_wins += match.team_1_half_2 + match.team_2_half

    session.commit()


def new_game_agent(team: list[Agent], result: int, session):
    """Function to Update the Agent Table from data in a new Match.

    Paramaters
    ----------
    team : list[Agent]
        The Agents on a given team.
    result : int
        Int showing whether the team won."""

    for agent in team:
        specific_agent = agent
        map_agent = session.query(Agent).where((Agent.tournament == "Overall") &
                                               (Agent.map == agent.map) &
                                               (Agent.agent == agent.agent)).first()
        tour_agent = session.query(Agent).where((Agent.tournament == agent.tournament) &
                                                (Agent.map == "Overall") &
                                                (Agent.agent == agent.agent)).first()
        ovr_agent = session.query(Agent).where((Agent.tournament == "Overall") &
                                               (Agent.map == "Overall") &
                                               (Agent.agent == agent.agent)).first()
        agents = [specific_agent, map_agent, tour_agent, ovr_agent]
        for agent_ in agents:
            agent_.games += 1
            agent_.wins += result


# adjusts agent and comp data from a new map
def new_game_comp(match: Match, result: int, session):
    """Function to Update the Comp Table from data in a new Match.

    Parameters
    ----------
    match : Match
        The match object for the new match.
    result : int
        Int showing which team won.
    session"""

    team_1 = [[match.team_1_agent_1_ref,
               match.team_1_agent_2_ref,
               match.team_1_agent_3_ref,
               match.team_1_agent_4_ref,
               match.team_1_agent_5_ref],
              [match.team_1_comp_ref,
               "{} {} {} {} {}".format(
                   match.team_1_agent_1_ref.agent_ref.abbreviation,
                   match.team_1_agent_2_ref.agent_ref.abbreviation,
                   match.team_1_agent_3_ref.agent_ref.abbreviation,
                   match.team_1_agent_4_ref.agent_ref.abbreviation,
                   match.team_1_agent_5_ref.agent_ref.abbreviation)]]

    team_2 = [[match.team_2_agent_1_ref,
               match.team_2_agent_2_ref,
               match.team_2_agent_3_ref,
               match.team_2_agent_4_ref,
               match.team_2_agent_5_ref],
              [match.team_2_comp_ref,
               "{} {} {} {} {}".format(
                   match.team_2_agent_1_ref.agent_ref.abbreviation,
                   match.team_2_agent_2_ref.agent_ref.abbreviation,
                   match.team_2_agent_3_ref.agent_ref.abbreviation,
                   match.team_2_agent_4_ref.agent_ref.abbreviation,
                   match.team_2_agent_5_ref.agent_ref.abbreviation)]]

    teams = [team_1, team_2]

    for team in teams:
        comp = session.query(Comp).where((Comp.tournament == match.tournament) &
                                         (Comp.map == match.map) &
                                         (Comp.agent_1 == team[0][0].agent) &
                                         (Comp.agent_2 == team[0][1].agent) &
                                         (Comp.agent_3 == team[0][2].agent) &
                                         (Comp.agent_4 == team[0][3].agent) &
                                         (Comp.agent_5 == team[0][4].agent)).first()

        map_comp = session.query(Comp).where((Comp.tournament == "Overall") &
                                             (Comp.map == match.map) &
                                             (Comp.agent_1 == team[0][0].agent) &
                                             (Comp.agent_2 == team[0][1].agent) &
                                             (Comp.agent_3 == team[0][2].agent) &
                                             (Comp.agent_4 == team[0][3].agent) &
                                             (Comp.agent_5 == team[0][4].agent)).first()

        tour_comp = session.query(Comp).where((Comp.tournament == match.tournament) &
                                              (Comp.map == "Overall") &
                                              (Comp.agent_1 == team[0][0].agent) &
                                              (Comp.agent_2 == team[0][1].agent) &
                                              (Comp.agent_3 == team[0][2].agent) &
                                              (Comp.agent_4 == team[0][3].agent) &
                                              (Comp.agent_5 == team[0][4].agent)).first()

        ovr_comp = session.query(Comp).where((Comp.tournament == "Overall") &
                                             (Comp.map == "Overall") &
                                             (Comp.agent_1 == team[0][0].agent) &
                                             (Comp.agent_2 == team[0][1].agent) &
                                             (Comp.agent_3 == team[0][2].agent) &
                                             (Comp.agent_4 == team[0][3].agent) &
                                             (Comp.agent_5 == team[0][4].agent)).first()
        comps = [[ovr_comp, map_comp, tour_comp, comp],
                 [["Overall", "Overall"],
                  ["Overall", match.map],
                  [match.tournament, "Overall"],
                  [match.tournament, match.map]]]

        for n, comp_ in enumerate(comps[0]):
            if comp_:
                comp_.games += 1
                comp_.wins += result
            else:
                new_comp = Comp(tournament=comps[1][n][0],
                                map=comps[1][n][1],
                                agent_1=team[0][0].agent,
                                agent_2=team[0][1].agent,
                                agent_3=team[0][2].agent,
                                agent_4=team[0][3].agent,
                                agent_5=team[0][4].agent,
                                games=1,
                                wins=result,
                                ref=team[1][1])
                session.add(new_comp)

        if not team[1][0]:
            team[1][0] = comp

        new_game_agent(team[0], result, session)

        # swaps result for the other team
        result = (result + 1) % 2

        session.commit()


# adjusts team data from a new map
def new_game_team(match: Match, result: int, session):
    """Function to Update the Team table from data in a new Match.

    Parameters
    ----------
    match : Match
        The Match object of the new match.
    result : int
        Int showing which team won the match.
    session"""

    teams = [match.team_1_ref,
             match.team_2_ref]

    # updates team
    for team in teams:
        specific_team = team
        map_team = session.query(Team).where((Team.tournament == "Overall") &
                                             (Team.map == team.map) &
                                             (Team.team == team.team)).first()
        tour_team = session.query(Team).where((Team.tournament == team.tournament) &
                                              (Team.map == "Overall") &
                                              (Team.team == team.team)).first()
        ovr_team = session.query(Team).where((Team.tournament == "Overall") &
                                             (Team.map == "Overall") &
                                             (Team.team == team.team)).first()
        teams_ = [specific_team, map_team, tour_team, ovr_team]
        for team_ in teams_:
            team_.games += 1
            team_.wins += result
        team.games += 1
        team.wins += result

        # swaps result for the other team
        result = (result + 1) % 2

    session.commit()


# adjusts tournament data from a new map
def new_game_tournament(match: Match, session):
    """Function to update the Tournament table with data from a new Match.

    Parameters
    ----------
    match : Match
        The Match object for the new Match.
    session"""
    ovr = session.query(Tournament).where(Tournament.tournament == "Overall").first()
    ovr.games += 1
    match.tournament_ref.games += 1
    session.commit()


def new_game(match: Match, result: int, session):
    """Hub Function to update the database based on a new match.

    Parameters
    ----------
    match : Match
        The Match object for the new Match.
    result : int
        Int showing which team won."""
    new_game_tournament(match, session)
    new_game_map(match, session)
    new_game_comp(match, result, session)
    new_game_team(match, result, session)
