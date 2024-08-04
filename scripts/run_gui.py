import customtkinter as ctk

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vct.gui_elements import tkinterApp
from vct.functions import create_database

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("dark-blue")

database: str = "VCT"

path = fr"sqlite:///{str(Path(__file__).parents[1])}/{database}.db"
engine = create_engine(path)
Session = sessionmaker(bind=engine)
session = Session()
create_database(database, session)

app = tkinterApp(engine)
app.attributes("-fullscreen", "True")
app.mainloop()
