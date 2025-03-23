from textual.app import (
    App,
    ComposeResult,
    RenderResult
)
from textual.containers import (
    Container,
    Vertical,
    Grid,
    ScrollableContainer
)
from textual.widgets import (
    Static,
    Input,
    Button,
    Footer,
    Header,
    Placeholder,
    Label,
    DataTable,
    ListView,
    ListItem
)
from textual.screen import Screen
from textual import events
from pathlib import Path
import os
from textual.reactive import reactive
from textual.message import Message
from textual import log
from textual import on
from time import time
from textual.renderables.gradient import LinearGradient
from time import time

from .widgets import *

import asyncio
import time
import subprocess
import shutil


class MainScreen(Screen):

    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle sidebar")
    ]

    def __init__(self):
        super().__init__()

    def action_toggle_sidebar(self) -> None:
        self.query_one(Sidebar).toggle_class("-hidden")

    # def get_consummation_amount(self) -> float:
    #     self.sebastian_ate_list = self.app.get_screen(
    #         "item_processor").consumed_by_sebastian
    def on_mount(self) -> None:
        self.stylesheet = "styles.css"


    def compose(self) -> ComposeResult:
        # yield Sidebar(classes="-hidden")
        yield ScrollableContainer(
            Label(
                "Slither Insight",
                classes="main-title"
            ),
            Container(
                Label("Consummation Amount", classes="content-title"),
                SampleDataTable(),
                classes="content"
            ),
            Container(
                Label("Consummation Amount", classes="content-title"),
                SampleDataTable(),
                classes="content"
            ),
            Container(
                Label("Histogram Plot", classes="content-title"),
                HistogramPlot(),
                classes="content"
            )

            
        )

        # yield Placeholder(
        #     id="placeholder",
        #     classes="content"
        # )
    # Remove the render method override if not needed for the whole screen
    # def render(self) -> RenderResult:
    #     return LinearGradient(time() * 90, STOPS)  # Apply the gradient