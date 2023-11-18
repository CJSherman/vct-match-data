from .databases import Comp, Match, Agent


# adjusts map data from a new map
def new_game_map(match: Match, session):

    map = match.map_ref
    map.games += 1
    map.ct_wins += match.team_1_half + match.team_2_half_2
    map.t_wins += match.team_1_half_2 + match.team_2_half

    session.commit()


def new_game_agent(team: list[Agent], result: int):
    for agent in team:
        agent.games += 1
        agent.wins += result


# adjusts agent and comp data from a new map
def new_game_comp(match: Match, result: int, session):

    team_1 = [[match.team_1_agent_1_ref,
               match.team_1_agent_2_ref,
               match.team_1_agent_3_ref,
               match.team_1_agent_4_ref,
               match.team_1_agent_5_ref],
              [match.team_1_comp_id,
               match.team_1_comp_ref,
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
              [match.team_2_comp_id,
               match.team_2_comp_ref,
               "{} {} {} {} {}".format(
                   match.team_2_agent_1_ref.agent_ref.abbreviation,
                   match.team_2_agent_2_ref.agent_ref.abbreviation,
                   match.team_2_agent_3_ref.agent_ref.abbreviation,
                   match.team_2_agent_4_ref.agent_ref.abbreviation,
                   match.team_2_agent_5_ref.agent_ref.abbreviation)]]

    teams = [team_1, team_2]

    for team in teams:
        comp = session.query(Comp).filter_by(id=team[1][0]).first()
        # if comp already has an entry, update it
        if comp:
            comp.games += 1
            comp.wins += result
            if not team[1][1]:
                team[1][1] = comp
        # otherwise create new entry
        else:
            new_comp = Comp(tournament=match.tournament,
                            map=match.map,
                            agent_1=team[0][0].agent,
                            agent_2=team[0][1].agent,
                            agent_3=team[0][2].agent,
                            agent_4=team[0][3].agent,
                            agent_5=team[0][4].agent,
                            games=1,
                            wins=result,
                            id=team[1][0],
                            ref=team[1][2],
                            map_id=match.map_id,
                            agent_1_id=team[0][0].id,
                            agent_2_id=team[0][1].id,
                            agent_3_id=team[0][2].id,
                            agent_4_id=team[0][3].id,
                            agent_5_id=team[0][4].id)
            session.add(new_comp)

        new_game_agent(team[0], result)

        # swaps result for the other team
        result = (result + 1) % 2

        session.commit()


# adjusts team data from a new map
def new_game_team(match: Match, result: int, session):

    teams = [match.team_1_ref,
             match.team_2_ref]

    # updates team
    for team in teams:
        team.games += 1
        team.wins += result

        # swaps result for the other team
        result = (result + 1) % 2

    session.commit()


# adjusts tournament data from a new map
def new_game_tournament(match: Match, session):
    match.tournament_ref.games += 1
    session.commit()


def new_game(match: Match, result: int, session):

    new_game_tournament(match, session)
    new_game_map(match, session)
    new_game_comp(match, result, session)
    new_game_team(match, result, session)
