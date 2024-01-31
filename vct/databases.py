from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

base = declarative_base()


class Tournament(base):
    __tablename__ = "tournaments"

    tournament: Mapped[str] = mapped_column(primary_key=True)

    games: Mapped[int]
    map_pool: Mapped[str]
    agent_pool: Mapped[str]
    team_pool: Mapped[str]


class Referall(base):
    __tablename__ = "referall"

    name: Mapped[str] = mapped_column(primary_key=True)

    abbreviation: Mapped[str] = mapped_column(unique=True)
    type: Mapped[str]


class Map(base):
    __tablename__ = "maps"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.tournament"), primary_key=True)
    map: Mapped[str] = mapped_column(ForeignKey("referall.name"), primary_key=True)

    games: Mapped[int]
    ct_wins: Mapped[int]
    t_wins: Mapped[int]

    tournament_ref: Mapped[Tournament] = relationship("Tournament", foreign_keys=tournament)
    map_ref: Mapped[Referall] = relationship("Referall", foreign_keys=map)


class Agent(base):
    __tablename__ = "agents"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.tournament"),
                                            primary_key=True)
    map: Mapped[str] = mapped_column(primary_key=True)
    agent: Mapped[str] = mapped_column(ForeignKey("referall.name"), primary_key=True)

    games: Mapped[int]
    wins: Mapped[int]

    tournament_ref: Mapped[Tournament] = relationship("Tournament", foreign_keys=tournament)
    map_ref: Mapped[Map] = relationship("Map", foreign_keys=[tournament, map])
    agent_ref: Mapped[Referall] = relationship("Referall", foreign_keys=agent)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tournament", "map"],
            ["maps.tournament", "maps.map"]
        ),
    )


class Team(base):
    __tablename__ = "teams"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.tournament"),
                                            primary_key=True)
    map: Mapped[str] = mapped_column(primary_key=True)
    team: Mapped[str] = mapped_column(ForeignKey("referall.name"), primary_key=True)

    games: Mapped[int]
    wins: Mapped[int]

    tournament_ref: Mapped[Tournament] = relationship("Tournament", foreign_keys=tournament)
    map_ref: Mapped[Map] = relationship("Map", foreign_keys=[tournament, map])
    team_ref: Mapped[Referall] = relationship("Referall", foreign_keys=team)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tournament", "map"],
            ["maps.tournament", "maps.map"]
        ),
    )


class Comp(base):
    __tablename__ = "comps"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.tournament"),
                                            primary_key=True)
    map: Mapped[str] = mapped_column(primary_key=True)
    agent_1: Mapped[str] = mapped_column(primary_key=True)
    agent_2: Mapped[str] = mapped_column(primary_key=True)
    agent_3: Mapped[str] = mapped_column(primary_key=True)
    agent_4: Mapped[str] = mapped_column(primary_key=True)
    agent_5: Mapped[str] = mapped_column(primary_key=True)

    games: Mapped[int]
    wins: Mapped[int]
    ref: Mapped[str]

    tournament_ref: Mapped[Tournament] = relationship("Tournament", foreign_keys=tournament)
    map_ref: Mapped[Map] = relationship("Map", foreign_keys=[tournament, map])
    agent_1_ref: Mapped[Agent] = relationship("Agent", foreign_keys=[tournament, map, agent_1])
    agent_2_ref: Mapped[Agent] = relationship("Agent", foreign_keys=[tournament, map, agent_2])
    agent_3_ref: Mapped[Agent] = relationship("Agent", foreign_keys=[tournament, map, agent_3])
    agent_4_ref: Mapped[Agent] = relationship("Agent", foreign_keys=[tournament, map, agent_4])
    agent_5_ref: Mapped[Agent] = relationship("Agent", foreign_keys=[tournament, map, agent_5])

    __table_args__ = (
        ForeignKeyConstraint(
            ["tournament", "map"],
            ["maps.tournament", "maps.map"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "agent_1"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "agent_2"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "agent_3"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "agent_4"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "agent_5"],
            ["agents.tournament", "agents.map", "agents.agent"]
        )
    )


class Match(base):
    __tablename__ = "matches"

    tournament: Mapped[str] = mapped_column(ForeignKey("tournaments.tournament"))
    map: Mapped[str] = mapped_column()

    team_1: Mapped[str] = mapped_column()
    team_1_score: Mapped[int]
    team_2_score: Mapped[int]
    team_2: Mapped[str] = mapped_column()
    team_1_half: Mapped[int]
    team_2_half: Mapped[int]
    team_1_half_2: Mapped[int]
    team_2_half_2: Mapped[int]

    team_1_agent_1: Mapped[str] = mapped_column()
    team_1_agent_2: Mapped[str] = mapped_column()
    team_1_agent_3: Mapped[str] = mapped_column()
    team_1_agent_4: Mapped[str] = mapped_column()
    team_1_agent_5: Mapped[str] = mapped_column()
    team_2_agent_1: Mapped[str] = mapped_column()
    team_2_agent_2: Mapped[str] = mapped_column()
    team_2_agent_3: Mapped[str] = mapped_column()
    team_2_agent_4: Mapped[str] = mapped_column()
    team_2_agent_5: Mapped[str] = mapped_column()
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tournament_ref: Mapped[Tournament] = relationship("Tournament", foreign_keys=tournament)
    map_ref: Mapped[Map] = relationship("Map", foreign_keys=[tournament, map])
    team_1_ref: Mapped[Team] = relationship("Team", foreign_keys=[tournament, map, team_1])
    team_2_ref: Mapped[Team] = relationship("Team", foreign_keys=[tournament, map, team_2])
    team_1_agent_1_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_1_agent_1])
    team_1_agent_2_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_1_agent_2])
    team_1_agent_3_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_1_agent_3])
    team_1_agent_4_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_1_agent_4])
    team_1_agent_5_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_1_agent_5])
    team_1_comp_ref: Mapped[Comp] = relationship("Comp",
                                                 foreign_keys=[tournament, map, team_1_agent_1,
                                                               team_1_agent_2, team_1_agent_3,
                                                               team_1_agent_4, team_1_agent_5])
    team_2_agent_1_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_2_agent_1])
    team_2_agent_2_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_2_agent_2])
    team_2_agent_3_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_2_agent_3])
    team_2_agent_4_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_2_agent_4])
    team_2_agent_5_ref: Mapped[Agent] = relationship("Agent",
                                                     foreign_keys=[tournament, map, team_2_agent_5])
    team_2_comp_ref: Mapped[Comp] = relationship("Comp",
                                                 foreign_keys=[tournament, map, team_2_agent_1,
                                                               team_2_agent_2, team_2_agent_3,
                                                               team_2_agent_4, team_2_agent_5])

    __table_args__ = (
        ForeignKeyConstraint(
            ["tournament", "map"],
            ["maps.tournament", "maps.map"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1_agent_1"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1_agent_2"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1_agent_3"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1_agent_4"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1_agent_5"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2_agent_1"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2_agent_2"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2_agent_3"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2_agent_4"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2_agent_5"],
            ["agents.tournament", "agents.map", "agents.agent"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1"],
            ["teams.tournament", "teams.map", "teams.team"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2"],
            ["teams.tournament", "teams.map", "teams.team"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_1_agent_1", "team_1_agent_2", "team_1_agent_3",
             "team_1_agent_4", "team_1_agent_5"],
            ["comps.tournament", "comps.map", "comps.agent_1", "comps.agent_2", "comps.agent_3",
             "comps.agent_4", "comps.agent_5"]
        ),
        ForeignKeyConstraint(
            ["tournament", "map", "team_2_agent_1", "team_2_agent_2", "team_2_agent_3",
             "team_2_agent_4", "team_2_agent_5"],
            ["comps.tournament", "comps.map", "comps.agent_1", "comps.agent_2", "comps.agent_3",
             "comps.agent_4", "comps.agent_5"]
        )
    )
