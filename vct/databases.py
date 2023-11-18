from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

base = declarative_base()


class Tournament(base):
    __tablename__ = "tournaments"

    id: Mapped[str] = mapped_column(primary_key=True)
    games: Mapped[int]
    map_pool: Mapped[str]
    agent_pool: Mapped[str]
    team_pool: Mapped[str]


class Map(base):
    __tablename__ = "maps"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.id"))
    tournament_ref: Mapped[Tournament] = relationship("Tournament")
    map: Mapped[str]
    games: Mapped[int]
    ct_wins: Mapped[int]
    t_wins: Mapped[int]

    id: Mapped[str] = mapped_column(primary_key=True)

class Agent_Shorthand(base):
    __tablename__ = "agent_referall"

    name: Mapped[str] = mapped_column(primary_key=True)
    abbreviation: Mapped[str] = mapped_column(unique=True)

class Agent(base):
    __tablename__ = "agents"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.id"))
    tournament_ref: Mapped[Tournament] = relationship("Tournament")
    map: Mapped[str]
    agent: Mapped[str] = mapped_column(ForeignKey("agent_referall.name"))
    agent_ref: Mapped[Agent_Shorthand] = relationship("Agent_Shorthand")
    games: Mapped[int]
    wins: Mapped[int]

    id: Mapped[str] = mapped_column(primary_key=True)
    map_id: Mapped[str] = mapped_column(ForeignKey("maps.id"))
    map_ref: Mapped[Map] = relationship("Map")


class Comp(base):
    __tablename__ = "comps"
    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.id"))
    tournament_ref: Mapped[Tournament] = relationship("Tournament")
    map: Mapped[str]
    agent_1: Mapped[str]
    agent_2: Mapped[str]
    agent_3: Mapped[str]
    agent_4: Mapped[str]
    agent_5: Mapped[str]
    games: Mapped[int]
    wins: Mapped[int]

    id: Mapped[str] = mapped_column(primary_key=True)
    ref: Mapped[str]
    map_id: Mapped[str] = mapped_column(ForeignKey("maps.id"))
    map_ref: Mapped[Map] = relationship("Map")
    agent_1_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    agent_1_ref: Mapped[Agent] = relationship("Agent", foreign_keys=agent_1_id)
    agent_2_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    agent_2_ref: Mapped[Agent] = relationship("Agent", foreign_keys=agent_2_id)
    agent_3_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    agent_3_ref: Mapped[Agent] = relationship("Agent", foreign_keys=agent_3_id)
    agent_4_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    agent_4_ref: Mapped[Agent] = relationship("Agent", foreign_keys=agent_4_id)
    agent_5_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    agent_5_ref: Mapped[Agent] = relationship("Agent", foreign_keys=agent_5_id)


class Team(base):
    __tablename__ = "teams"
    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.id"))
    tournament_ref: Mapped[Tournament] = relationship("Tournament")
    map: Mapped[str]
    team: Mapped[str]
    games: Mapped[int]
    wins: Mapped[int]

    id: Mapped[str] = mapped_column(primary_key=True)
    map_id: Mapped[str] = mapped_column(ForeignKey("maps.id"))
    map_ref: Mapped[Map] = relationship("Map")


class Match(base):
    __tablename__ = "matches"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.id"))
    tournament_ref: Mapped[Tournament] = relationship("Tournament")
    map: Mapped[str]
    team_1: Mapped[str]
    team_2: Mapped[str]

    team_1_score: Mapped[int]
    team_2_score: Mapped[int]

    team_1_half: Mapped[int]
    team_2_half: Mapped[int]
    team_1_half_2: Mapped[int]
    team_2_half_2: Mapped[int]

    team_1_agent_1: Mapped[str]
    team_1_agent_2: Mapped[str]
    team_1_agent_3: Mapped[str]
    team_1_agent_4: Mapped[str]
    team_1_agent_5: Mapped[str]
    team_2_agent_1: Mapped[str]
    team_2_agent_2: Mapped[str]
    team_2_agent_3: Mapped[str]
    team_2_agent_4: Mapped[str]
    team_2_agent_5: Mapped[str]

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    map_id: Mapped[str] = mapped_column(ForeignKey("maps.id"))
    map_ref: Mapped[Map] = relationship("Map")
    team_1_id: Mapped[str] = mapped_column(ForeignKey("teams.id"))
    team_1_ref: Mapped[Team] = relationship("Team", foreign_keys=team_1_id)
    team_2_id: Mapped[str] = mapped_column(ForeignKey("teams.id"))
    team_2_ref: Mapped[Team] = relationship("Team", foreign_keys=team_2_id)
    team_1_agent_1_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_1_agent_1_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_1_agent_1_id)
    team_1_agent_2_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_1_agent_2_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_1_agent_2_id)
    team_1_agent_3_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_1_agent_3_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_1_agent_3_id)
    team_1_agent_4_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_1_agent_4_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_1_agent_4_id)
    team_1_agent_5_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_1_agent_5_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_1_agent_5_id)
    team_2_agent_1_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_2_agent_1_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_2_agent_1_id)
    team_2_agent_2_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_2_agent_2_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_2_agent_2_id)
    team_2_agent_3_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_2_agent_3_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_2_agent_3_id)
    team_2_agent_4_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_2_agent_4_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_2_agent_4_id)
    team_2_agent_5_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))
    team_2_agent_5_ref: Mapped[Agent] = relationship("Agent", foreign_keys=team_2_agent_5_id)
    team_1_comp_id: Mapped[str] = mapped_column(ForeignKey("comps.id"))
    team_1_comp_ref: Mapped[Comp] = relationship("Comp", foreign_keys=team_1_comp_id)
    team_2_comp_id: Mapped[str] = mapped_column(ForeignKey("comps.id"))
    team_2_comp_ref: Mapped[Comp] = relationship("Comp", foreign_keys=team_2_comp_id)
