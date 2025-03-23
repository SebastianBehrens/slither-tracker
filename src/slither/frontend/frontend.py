from textual.app import (
    App,
)

import logging
from textual.screen import Screen
from pathlib import Path
import os
from slither.util import SlitherDatabaseMinimal
import pandas as pd

from .screens import *

class Frontend(App):
    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_mode", "Toggle Dark/Light Mode"),
    ]

    SCREENS = {
        "main": MainScreen
    }

    def __init__(self, connection_string: str, logger: logging.Logger):
        super().__init__()
        self.logger = logger
        self.database = SlitherDatabaseMinimal(
            connection_string=connection_string,
            logger=self.logger
        )


    def on_mount(self) -> None:
        self.push_screen("main")
        self.set_interval(interval=2, callback=self.fetch_data, repeat=4)

    def fetch_data(self):
        self.notify("Fetching data...", timeout=1)
        result = self.database.query(
            query="SELECT * FROM public.server_user_rank LIMIT 3;",
            fetch='all'
        )
        df = pd.DataFrame(result)
        self.query_one()
        print(result)

        self.notify("Data updated!", timeout=1)

    def action_quit(self):
        self.exit()

    def action_toggle_mode(self):
        self.dark = not self.dark

