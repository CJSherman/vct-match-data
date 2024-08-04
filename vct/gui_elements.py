import matplotlib
import threading
import customtkinter as ctk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from .gui_viewer import plot
from .get_data import VLRScrape
from .databases import Tournament, Map, Agent, Team, Comp
from . import data_refresh

matplotlib.use("TkAgg")


class BasePage(ctk.CTkFrame):
    def switch_form(self):
        for form in self.forms:
            if form is not self.form:
                self.form = form
                break


class HomePage(BasePage):
    def __init__(self, parent, controller, *args, **kwargs):
        """
        The landing page.
        ADD DATA Button - Opens the :class:`AddDataPage`.
        VIEW DATA Button - Opens the :class:`GraphPage`.
        REFRESH DATA Button - Refreshes the database.
        EXIT Button - Closes the program.
        """
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller

        frame = ctk.CTkFrame(self)
        frame.pack(pady=12, padx=10)

        label = ctk.CTkLabel(frame, text="VCT Statistics")
        label.pack(pady=20, padx=20)

        button_add = ctk.CTkButton(frame, text="ADD DATA",
                                   command=self.data_page)
        button_add.configure(height=80, width=300)
        button_add.pack(pady=20, padx=20)

        button_view = ctk.CTkButton(frame, text="VIEW DATA",
                                    command=self.graph_page)
        button_view.configure(height=80, width=300)
        button_view.pack(pady=20, padx=20)

        button_refresh = ctk.CTkButton(frame, text="REFRESH DATA",
                                       command=self.press_refresh)
        button_refresh.configure(height=80, width=300)
        button_refresh.pack(pady=20, padx=20)

        button_exit = ctk.CTkButton(frame, text="EXIT", command=self.quit)
        button_exit.configure(height=80, width=300)
        button_exit.pack(pady=20, padx=20)

        self.label = ctk.StringVar()
        ctk.CTkLabel(frame, textvariable=self.label).pack(pady=20, padx=20)
        self.label.set("Select your option")

        self.refreshing = threading.Thread(target=self.press_refresh, args=[None])

        self._update()

    def press_refresh(self):
        """Checks if a refresh is occuring. If one is not then it will be started."""
        if self.refreshing.is_alive():
            self.label.set("Data Refresh Already in Progress: Please Wait")
        else:
            self.label.set("Data Refresh in Progress: Please Wait")
            self.refreshing = threading.Thread(target=self._refresh)
            self.refreshing.start()

    def _refresh(self):
        session = sessionmaker(bind=self.controller.engine)()
        data_refresh(session)
        session.close()

    def data_page(self):
        """
        Checks if a refresh is occuring.
        If one is not then the :class:`AddDataPage` is opened.
        """

        if self.refreshing.is_alive():
            self.label.set("Can not exit, refreshing in progress")
        else:
            self.controller.show_frame(AddDataPage)

    def graph_page(self):
        """Checks if a refresh is occuring. If one is not then the :class:`GraphPage` is opened."""
        if self.refreshing.is_alive():
            self.label.set("Can not exit, refreshing in progress")
        else:
            self.label.set("")
            self.controller.show_frame(GraphPage)

    def quit(self):
        """Checks if a refresh is occuring. If one is not then program is closed."""
        if self.refreshing.is_alive():
            self.label.set("Can not exit, refreshing in progress")
        else:
            quit()

    def _update(self):
        if not self.refreshing.is_alive():
            self.label.set("Select your option")
        self.after(1000, self._update)


class AddDataPage(BasePage):
    def __init__(self, parent, controller, *args, **kwargs):
        """
        This page is used to add data to the database through scraping.

        Text Entry Box - Tournament or Match URLs can be entered here. Both the ENTER Button and the
        Enter key will submit the text.
        SCRAPE Button - Begins the scraping of the submitted urls.
        DONE - Returns to the landing page.
        """
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)

        self.controller = controller
        self.clicked = False
        frame = ctk.CTkFrame(self)
        frame.pack(pady=12, padx=10)

        ctk.CTkLabel(frame, text="Enter URL:").grid(row=0, column=3)

        self.entry = ctk.CTkEntry(frame)
        self.entry.grid(row=1, column=0, columnspan=6, pady=10)
        self.entry.configure(height=20, width=300)
        self.entry.bind("<Return>", self.enter_data)

        button_scrape = ctk.CTkButton(frame, text="SCRAPE", command=self.press_scrape)
        button_scrape.grid(row=3, column=0, columnspan=7, pady=10)
        button_scrape.configure(height=80, width=350)

        button_done = ctk.CTkButton(frame, text="DONE", command=self.exit_page)
        button_done.grid(row=4, column=0, columnspan=7, pady=10)
        button_done.configure(height=80, width=350)

        self.label = ctk.StringVar()
        ctk.CTkLabel(frame, textvariable=self.label).grid(row=2, column=0, columnspan=7, pady=10)
        self.label.set("")

        self.label_2 = ctk.StringVar()
        ctk.CTkLabel(frame, textvariable=self.label_2).grid(row=5, column=0, columnspan=7, pady=10)
        self.label_2.set(f"Loaded Tournaments: {len(self.controller.scraper.tournament_urls)}")

        self.label_3 = ctk.StringVar()
        ctk.CTkLabel(frame, textvariable=self.label_3).grid(row=6, column=0, columnspan=7, pady=10)
        self.label_3.set(f"Loaded Matches: {len(self.controller.scraper.match_urls)}")

        button_send = ctk.CTkButton(frame, text="ENTER", command=self.enter_data)
        button_send.grid(row=1, column=6, pady=10)
        button_send.configure(height=20, width=50)

        self.scraping = threading.Thread(target=self._scrape)
        self._update()

    def enter_data(self, *args):
        """Adds entered text to the correct array in the :class:`~get_data.VLRScrape`."""
        url = self.entry.get()
        split_url = url.split("/")
        if split_url[2] == "www.vlr.gg" and not len(split_url) < 4:
            if split_url[3] == "event":
                self.controller.scraper.add_tournaments(url)
                self.label.set("Tournament Entered")
            else:
                self.controller.scraper.add_matches(url)
                self.label.set("Match Entered")
        else:
            self.label.set("INVALID URL: Must be a www.vlr.gg match or event url")
        self.entry.delete(0, "end")

    def press_scrape(self):
        """Runs the :class:`~get_data.VLRScrape` if it isn't already."""
        if self.scraping.is_alive():
            self.label.set("Scraping already in progress")
        else:
            self.clicked = True
            self.label.set("Scraping in progress")
            self.scraping = threading.Thread(target=self._scrape)
            self.scraping.start()

    def _scrape(self):
        session = sessionmaker(bind=self.controller.engine)()
        self.controller.scraper.session = session
        self.controller.scraper.find_match_pages()
        self.controller.scraper.find_match_data()
        self.controller.scraper.session = None
        session.close()

    def exit_page(self):
        """Returns to the landing page if the scraper is not running."""
        if self.scraping.is_alive():
            self.label.set("Can not exit, scraping in progress")
        else:
            self.label.set("")
            self.controller.show_frame(HomePage)

    def _update(self):
        if self.clicked and not self.scraping.is_alive():
            self.label.set("")
            self.clicked = False
        self.label_2.set(f"Loaded Tournaments: {len(self.controller.scraper.tournament_urls)}")
        self.label_3.set(f"Loaded Matches: {len(self.controller.scraper.match_urls)}")
        self.after(1000, self._update)


class GraphPage(BasePage):

    def __init__(self, parent, controller, *args, **kwargs):
        """
        Plots the data obtained from the database.

        DONE Button - Returns to the Landing Page.
        Tournaments Scroll - Select the desired tournaments.
        Maps Scroll - Select the desired maps.
        Comps Scroll - Select the desired comps.
        Agents Scroll - Select the desired agents.
        Teams Scroll - Select the desired teams.
        Title Dropdown - Select the table from which data is pulled.
        X-Axis Dropdown - Select the grouping to be plotted on the x-axis.
        Y-Axis Dropdown - Select the grouping to be plotted on the y-axis.
        Split By Dropdown - Select the grouping for the stacked bars.
        Number of Subplots Slider - The desired number of stacked bars.
        """
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.frame = ctk.CTkFrame(self)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, sticky="ew")
        self.forms = (ctk.CTkFrame(self), ctk.CTkFrame(self))
        self.form = self.forms[1]
        self.canvas = None
        self.controller = controller

        session = sessionmaker(bind=self.controller.engine)()
        self.tournaments = [tournament.tournament for tournament in session.query(Tournament).where(
            Tournament.tournament != "Overall")]
        self.maps = [map.map for map in session.query(Map).where(
            (Map.tournament == "Overall") & (Map.map != "Overall"))]
        self.agents = [agent.agent for agent in session.query(Agent).where(
            (Agent.tournament == "Overall") & (Agent.map == "Overall"))]
        self.teams = [team.team for team in session.query(Team).where(
            (Team.tournament == "Overall") & (Team.map == "Overall"))]
        self.comps = [comp.ref for comp in session.query(Comp).where(
            (Comp.tournament == "Overall") & (Comp.map == "Overall"))]
        session.close()

        self.selected_tournaments = self.tournaments
        self.selected_maps = self.maps
        self.selected_comps = self.comps
        self.selected_agents = self.agents
        self.selected_teams = self.teams

        self.tour_vars = []
        self.map_vars = []
        self.comp_vars = []
        self.agent_vars = []
        self.team_vars = []

        self.title = ctk.StringVar(value="Tournaments")
        self.x_axis = ctk.StringVar(value="Tournaments")
        self.y_axis = ctk.StringVar(value="Games")
        self.split = ctk.StringVar(value="Tournaments")
        self.count = ctk.IntVar(value=1)
        self.split_var = ctk.BooleanVar(value=False)

        button_done = ctk.CTkButton(self.frame, text="DONE", command=self.exit_page)
        button_done.grid(row=0, column=0)
        button_done.configure(height=80, width=350)

        self.get_tournaments()
        self.get_maps()
        self.get_comps()
        self.get_agents()
        self.get_teams()
        for form in self.forms:
            form.grid_columnconfigure(0, weight=1)
            form.grid_columnconfigure(1, weight=1)
            form.grid_columnconfigure(2, weight=1)
            form.grid_columnconfigure(3, weight=1)
            form.grid_columnconfigure(4, weight=1)
            form.grid_columnconfigure(5, weight=1)
            form.grid(row=1, sticky="new")
            self._update()

    def exit_page(self):
        """Return to the landing page."""
        self.controller.show_frame(HomePage)

    def _update(self, *args, **kwargs):
        for child in self.form.winfo_children():
            child.destroy()
        self.switch_form()

        self.get_splitting()
        self.get_title()
        self.get_x_axis()
        self.get_y_axis()
        self.get_split()

        session = sessionmaker(bind=self.controller.engine)()
        f = plot(self.selected_tournaments, self.selected_maps, self.selected_comps,
                 self.selected_agents, self.selected_teams, self.title.get(), self.x_axis.get(),
                 self.y_axis.get(), self.split.get(), self.count.get(), session)
        session.close()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2)

        self.update_idletasks()
        self.form.tkraise()

    def get_splitting(self):
        """Creates and places the "Number of Subplots" Slider."""
        ctk.CTkSlider(self.form, variable=self.count, number_of_steps=9,
                      from_=1, to=10, command=self._update_splitting).grid(row=1, column=4)
        self.split_label = ctk.StringVar(value=f"Number of Subplots: {self.count.get()}")
        ctk.CTkLabel(self.form, textvariable=self.split_label).grid(row=2, column=4)

    def _update_splitting(self, *args):
        self._update()

    def get_title(self):
        titles = ["Tournaments", "Maps", "Comps", "Agents", "Teams"]
        ctk.CTkOptionMenu(self.form, values=titles, command=self._update_title,
                          variable=self.title).grid(row=1, column=0)
        label = ctk.StringVar(value="Title")
        ctk.CTkLabel(self.form, textvariable=label).grid(row=2, column=0)

    def _update_title(self, *args):
        """Create and places the "Title" Dropdown."""
        if self.title.get() == "Tournaments":
            self.count.set(1)
            self.x_axis.set("Tournaments")
            self.y_axis.set("Games")
        else:
            if self.x_axis.get() in ["Comps", "Agents", "Teams"]:
                self.x_axis.set("Tournaments")
            self.y_axis.set("Pickrate")
        self.split.set(self.x_axis.get())
        self._update()

    def get_x_axis(self):
        """Create and places the "X-Axis" Dropdown."""
        x_labels = ["Tournaments"]
        if self.title.get() != "Tournaments":
            x_labels.append("Maps")
            if self.title.get() not in x_labels:
                x_labels.append(self.title.get())
        ctk.CTkOptionMenu(self.form, values=x_labels, command=self._update_x_axis,
                          variable=self.x_axis).grid(row=1, column=1)
        label = ctk.StringVar(value="X-Axis")
        ctk.CTkLabel(self.form, textvariable=label).grid(row=2, column=1)

    def _update_x_axis(self, *args):
        self.split.set(self.x_axis.get())
        self._update()

    def get_y_axis(self):
        """Create and places the "Y-Axis" Dropdown."""
        if self.title.get() == "Tournaments":
            y_labels = ["Games"]
        else:
            y_labels = ["Pickrate"]
            if self.title.get() == "Maps":
                y_labels.append("Sidedness")
            else:
                y_labels += ["Winrate", "Rating"]
        ctk.CTkOptionMenu(self.form, values=y_labels, command=self._update_y_axis,
                          variable=self.y_axis).grid(row=1, column=2)
        label = ctk.StringVar(value="Y-Axis")
        ctk.CTkLabel(self.form, textvariable=label).grid(row=2, column=2)

    def _update_y_axis(self, *args):
        self._update()

    def get_split(self):
        """Create and places the "Split By" Dropdown."""
        splits = ["Tournaments"]
        if self.title.get() != "Tournaments":
            splits += ["Maps"]
            if self.title.get() not in splits:
                splits.append(self.title.get())
        ctk.CTkOptionMenu(self.form, values=splits,
                          command=self._update_split,
                          variable=self.split).grid(row=1, column=3)
        label = ctk.StringVar(value="Split By")
        ctk.CTkLabel(self.form, textvariable=label).grid(row=2, column=3)

    def _update_split(self, *args):
        if self.split.get() == "Comps":
            self.count.set(3)
        self._update()

    def get_tournaments(self):
        """Create and places the "Tournaments" Checkboxes."""
        scroll = ctk.CTkScrollableFrame(self.frame, orientation="horizontal", height=25)
        scroll.grid(row=1, column=0, sticky="ew", columnspan=5)
        self.tour_vars.append(ctk.IntVar(value=1))
        box = ctk.CTkCheckBox(scroll, text="All", variable=self.tour_vars[0],
                              onvalue=1, offvalue=0, command=self._update_tournaments)
        box.pack(side="left", padx=5)
        for i in range(len(self.tournaments)):
            self.tour_vars.append(ctk.IntVar())
            box = ctk.CTkCheckBox(scroll, text=self.tournaments[i],
                                  variable=self.tour_vars[i+1], onvalue=1, offvalue=0,
                                  command=self._update_tournaments)
            box.pack(side="left", padx=5)

    def _update_tournaments(self):
        self.selected_tournaments = []
        if self.tour_vars[0].get() == 1:
            self.selected_tournaments = self.tournaments
            for i in range(len(self.tournaments)):
                self.tour_vars[i+1].set(0)
        else:
            for i in range(len(self.tournaments)):
                if self.tour_vars[i+1].get() == 1:
                    self.selected_tournaments.append(self.tournaments[i])
        self._update()

    def get_maps(self):
        """Create and places the "Maps" Checkboxes."""
        scroll = ctk.CTkScrollableFrame(self.frame, orientation="horizontal", height=25)
        scroll.grid(row=2, column=0, sticky="ew", columnspan=5)
        self.map_vars.append(ctk.IntVar(value=1))
        box = ctk.CTkCheckBox(scroll, text="All", variable=self.map_vars[0],
                              onvalue=1, offvalue=0, command=self._update_maps)
        box.pack(side="left", padx=5)
        for i in range(len(self.maps)):
            self.map_vars.append(ctk.IntVar())
            box = ctk.CTkCheckBox(scroll, text=self.maps[i],
                                  variable=self.map_vars[i+1], onvalue=1, offvalue=0,
                                  command=self._update_maps)
            box.pack(side="left", padx=5)

    def _update_maps(self):
        self.selected_maps = []
        if self.map_vars[0].get() == 1:
            self.selected_maps = self.maps
            for i in range(len(self.maps)):
                self.map_vars[i+1].set(0)
        else:
            for i in range(len(self.maps)):
                if self.map_vars[i+1].get() == 1:
                    self.selected_maps.append(self.maps[i])
        self._update()

    def get_comps(self) -> list[str]:
        """Create and places the "Comps" Checkboxes."""
        scroll = ctk.CTkScrollableFrame(self.frame, orientation="horizontal", height=25)
        scroll.grid(row=3, column=0, sticky="ew", columnspan=5)
        self.comp_vars.append(ctk.IntVar(value=1))
        box = ctk.CTkCheckBox(scroll, text="All", variable=self.comp_vars[0],
                              onvalue=1, offvalue=0, command=self._update_comps)
        box.pack(side="left", padx=5)
        for i in range(len(self.comps)):
            self.comp_vars.append(ctk.IntVar())
            box = ctk.CTkCheckBox(scroll, text=self.comps[i],
                                  variable=self.comp_vars[i+1], onvalue=1, offvalue=0,
                                  command=self._update_comps)
            box.pack(side="left", padx=5)

    def _update_comps(self):
        self.selected_comps = []
        if self.comp_vars[0].get() == 1:
            self.selected_comps = self.comps
            for i in range(len(self.comps)):
                self.comp_vars[i+1].set(0)
        else:
            for i in range(len(self.comps)):
                if self.comp_vars[i+1].get() == 1:
                    self.selected_comps.append(self.comps[i])
        self._update()

    def get_agents(self):
        """Create and places the "Agents" Checkboxes."""
        scroll = ctk.CTkScrollableFrame(self.frame, orientation="horizontal", height=25)
        scroll.grid(row=4, column=0, sticky="ew", columnspan=5)
        self.agent_vars.append(ctk.IntVar(value=1))
        box = ctk.CTkCheckBox(scroll, text="All", variable=self.agent_vars[0],
                              onvalue=1, offvalue=0, command=self._update_agents)
        box.pack(side="left", padx=5)
        for i in range(len(self.agents)):
            self.agent_vars.append(ctk.IntVar())
            box = ctk.CTkCheckBox(scroll, text=self.agents[i],
                                  variable=self.agent_vars[i+1], onvalue=1, offvalue=0,
                                  command=self._update_agents)
            box.pack(side="left", padx=5)

    def _update_agents(self):
        self.selected_agents = []
        if self.agent_vars[0].get() == 1:
            self.selected_agents = self.agents
            for i in range(len(self.agents)):
                self.agent_vars[i+1].set(0)
        else:
            for i in range(len(self.agents)):
                if self.agent_vars[i+1].get() == 1:
                    self.selected_agents.append(self.agents[i])
        self._update()

    def get_teams(self):
        """Create and places the "Teams" Checkboxes."""
        scroll = ctk.CTkScrollableFrame(self.frame, orientation="horizontal", height=25)
        scroll.grid(row=5, column=0, sticky="ew", columnspan=5)
        self.team_vars.append(ctk.IntVar(value=1))
        box = ctk.CTkCheckBox(scroll, text="All", variable=self.team_vars[0],
                              onvalue=1, offvalue=0, command=self._update_teams)
        box.pack(side="left", padx=5)
        for i in range(len(self.teams)):
            self.team_vars.append(ctk.IntVar())
            box = ctk.CTkCheckBox(scroll, text=self.teams[i],
                                  variable=self.team_vars[i+1], onvalue=1, offvalue=0,
                                  command=self._update_teams)
            box.pack(side="left", padx=5)

    def _update_teams(self):
        self.selected_teams = []
        if self.team_vars[0].get() == 1:
            self.selected_teams = self.teams
            for i in range(len(self.teams)):
                self.team_vars[i+1].set(0)
        else:
            for i in range(len(self.teams)):
                if self.team_vars[i+1].get() == 1:
                    self.selected_teams.append(self.teams[i])
        self._update()


class tkinterApp(ctk.CTk):
    def __init__(self, engine: Engine, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)

        self.engine = engine
        self.scraper = VLRScrape(session=None)

        self.geometry("1280x720")

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, AddDataPage, GraphPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
