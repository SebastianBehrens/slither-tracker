from textual.app import (
    App,
)


from textual.screen import Screen
from pathlib import Path
import os
from database import database

from screens import *

class SlitherInsight(App):
    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_mode", "Toggle Dark/Light Mode"),
    ]

    SCREENS = {
        "main": MainScreen
    }

    def on_mount(self) -> None:
        self.push_screen("main")
        self.set_interval(interval=2, callback=self.fetch_data, repeat=4)
        self.database = Database()

    def fetch_data(self):
        self.notify("Fetching data...", timeout=1)

        self.notify("Data updated!", timeout=1)

    def action_quit(self):
        self.exit()

    def action_toggle_mode(self):
        self.dark = not self.dark

if __name__ == "__main__":
    app = SlitherInsight()
    app.run()