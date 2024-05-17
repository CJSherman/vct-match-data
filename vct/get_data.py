import requests
from bs4 import BeautifulSoup
import datetime
import re
import copy

from .databases import Match, Tournament, Referall
from .functions import setup


class VLRScrape:
    base = "https://www.vlr.gg"
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "http://thewebsite.com",
        "Connection": "keep-alive"}
    last_scrape = datetime.datetime.now()

    def __init__(self, session, tournament_urls=None, match_urls=None):
        if tournament_urls is None:
            tournament_urls = []
        if match_urls is None:
            match_urls = []
        self.tournament_urls = tournament_urls
        self.match_urls = []
        self.session = session

    @property
    def scanned_matches(self):
        with open("ScannedMatches.txt") as file:
            matches = file.read().split("\n")
        return matches

    @property
    def existing_tournaments(self):
        return dict([(tournament.tournament, tournament)
                     for tournament in self.session.query(Tournament).all()])

    @property
    def existing_agents(self):
        return [referall.name
                for referall in self.session.query(Referall).where(Referall.type == "AGENT")]

    @property
    def existing_maps(self):
        return [referall.name
                for referall in self.session.query(Referall).where(Referall.type == "MAP")]

    @property
    def existing_teams(self):
        return [referall.name
                for referall in self.session.query(Referall).where(Referall.type == "TEAM")]

    def add_tournaments(self, tournaments: list | str):
        if isinstance(tournaments, str):
            self.tournament_urls.append(tournaments)
        elif isinstance(tournaments, list):
            self.tournament_urls += tournaments
        else:
            raise TypeError

    def add_matches(self, matches: list | str):
        if isinstance(matches, str):
            self.match_urls.append(matches)
        elif isinstance(matches, list):
            self.match_urls += matches
        else:
            raise TypeError

    def find_match_pages(self):
        urls = copy.copy(self.tournament_urls)
        for url in urls:
            self._find_match_pages(url)
            self.tournament_urls.remove(url)

    def _find_match_pages(self, url):
        new_url = url.split("/")
        new_url.insert(4, "matches")
        matches_url = "/".join(new_url) + "/?series=all"
        matches_soup = self.scrape(matches_url)

        matches = matches_soup.find_all("a", class_="match-item")
        self.match_urls += [self.base + match["href"] for match in matches
                            if (match.find("div", class_="match-item-event-series").text.split()[0]
                                != "Showmatch")]

    def find_match_data(self):
        urls = copy.copy(self.match_urls)
        for url in urls:
            scanned = self._find_match_data(url)
            if scanned:
                self.match_urls.remove(url)

    def _find_match_data(self, url):
        scanned_matches = self.scanned_matches
        code = url.split("/")[3]
        if code not in scanned_matches:
            soup = self.scrape(url)
            if soup.find("div", class_="match-header-vs-note").text.split()[0] != "final":
                print("Match is not completed.")
                return False
            maps = [map for map in soup.find_all("div", class_="vm-stats-game")
                    if map["data-game-id"] != "all"]
            tournament = soup.find("a", class_="match-header-event").text.split("\t")[6].upper()
            if tournament not in self.existing_tournaments:
                self.create_tournament(soup, tournament)
            for map in maps:
                self._find_map_data(map, tournament)

            scanned_matches.append(code)
            with open("ScannedMatches.txt", "w") as file:
                file.write("\n".join(scanned_matches))
            return True
        else:
            print("Match already scanned.")
            return True

    def _find_map_data(self, soup, tournament):
        tournament_obj = self.existing_tournaments[tournament]
        map_name = soup.find("div", class_="map").text.split("\t")[7].upper()
        if map_name not in tournament_obj.map_pool:
            tournament_obj.map_pool += f" - {map_name}"
            if map_name not in self.existing_maps:
                self.create_new_map(map_name)

        teams = [team.text.split("\t")[7].upper()
                 for team in soup.find_all("div", class_="team-name")]
        for team in teams:
            if team not in tournament_obj.team_pool:
                tournament_obj.team_pool += f" - {team}"
                if team not in self.existing_teams:
                    self.create_new_team(team)

        half_scores = soup.find_all("span", class_=re.compile("mod-(ct|t)"))[0:4]

        if "mod-ct" in half_scores[0]["class"]:
            ct, t = 0, 1
        elif "mod-t" in half_scores[0]["class"]:
            ct, t = 1, 0
        else:
            raise ValueError
        half1 = [int(half_scores[0].text), int(half_scores[2].text)]
        half2 = [int(half_scores[1].text), int(half_scores[3].text)]
        scores = [int(score.text) for score in soup.find_all("div", class_=re.compile("score *"))]

        agent_names = [agent.img.attrs["title"].upper()
                       for agent in soup.find_all("span", class_="mod-agent")]
        for agent in agent_names:
            if agent not in tournament_obj.agent_pool:
                tournament_obj.agent_pool += f" - {agent}"
                if agent not in self.existing_agents:
                    self.create_new_agent(agent)

        agents_1 = agent_names[:5]
        agents_1.sort()
        agents_2 = agent_names[5:]
        agents_2.sort()
        agents = [agents_1, agents_2]

        match = Match(tournament=tournament,
                      map=map_name,
                      team_1=teams[ct],
                      team_2=teams[t],
                      team_1_score=scores[ct],
                      team_2_score=scores[t],
                      team_1_half=half1[ct],
                      team_2_half=half1[t],
                      team_1_half_2=half2[ct],
                      team_2_half_2=half2[t],
                      team_1_agent_1=agents[ct][0],
                      team_1_agent_2=agents[ct][1],
                      team_1_agent_3=agents[ct][2],
                      team_1_agent_4=agents[ct][3],
                      team_1_agent_5=agents[ct][4],
                      team_2_agent_1=agents[t][0],
                      team_2_agent_2=agents[t][1],
                      team_2_agent_3=agents[t][2],
                      team_2_agent_4=agents[t][3],
                      team_2_agent_5=agents[t][4])

        self.session.add(match)
        self.session.commit()

    def create_tournament(self, soup, tournament):
        tournament_link = soup.find("a", class_="match-header-event")["href"].split("/")[:3]
        tournament_link.insert(2, "agents")
        url = self.base + "/".join(tournament_link)

        soup = self.scrape(url)

        tables = soup.find_all("table", class_="wf-table")
        table_1 = tables[0]
        table_2 = tables[1]

        agents = [agent.img["src"].split("/")[-1].split(".")[0].upper()
                  for agent in table_1.find_all("th", class_="mod-center")]

        existing_agents = self.existing_agents
        existing_maps = self.existing_maps
        existing_teams = self.existing_teams

        for agent in agents:
            if agent not in existing_agents:
                self.create_new_agent(agent)

        maps = [map.text.split("\t")[6].upper()
                for map in table_1.find_all("tr", class_="pr-global-row")
                if "mod-all" not in map["class"]]

        for map in maps:
            if map not in existing_maps:
                self.create_new_map(map)

        teams = [team.find("span", class_="text-of").text.split("\t")[10].upper()
                 for team in table_2.find_all("tr", class_="pr-matrix-row")
                 if "mod-dropdown" not in team["class"]]

        for team in teams:
            if team not in existing_teams:
                self.create_new_team(team)

        tournament_obj = Tournament(tournament=tournament,
                                    games=0,
                                    map_pool=" - ".join(maps),
                                    agent_pool=" - ".join(agents),
                                    team_pool=" - ".join(teams))
        self.session.add(tournament_obj)
        self.session.commit()

        setup(tournament_obj, self.session)

    def scrape(self, url):
        print(f"Scraping: {url}")
        while datetime.datetime.now() - self.last_scrape < datetime.timedelta(seconds=60):
            pass
        page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(page.text, "html")
        self.update_last_scrape()
        print("Done")
        return soup

    @classmethod
    def update_last_scrape(cls):
        cls.last_scrape = datetime.datetime.now()

    def create_new_map(self, map):
        referall = Referall(name=map,
                            abbreviation=map,
                            type="MAP")
        self.session.add(referall)
        self.session.commit()

    def create_new_agent(self, agent):
        ref = input(f"Enter Abbreviation for {agent}: ").upper()
        referall = Referall(name=agent,
                            abbreviation=ref,
                            type="AGENT")
        self.session.add(referall)
        self.session.commit()

    def create_new_team(self, team):
        ref = input(f"Enter Abbreviation for {team}: ").upper()
        referall = Referall(name=team,
                            abbreviation=ref,
                            type="TEAM")
        self.session.add(referall)
        self.session.commit()
