from textual.app import (
    App,
    ComposeResult
)
from textual_plotext import PlotextPlot
from textual.containers import (
    Container,
    Vertical,
    Horizontal,
    Grid,
    ScrollableContainer
)
from textual.widget import Widget
from textual.widgets import (
    Static,
    Switch,
    Button,
    Footer,
    Header,
    Placeholder,
    Label,
    DataTable,
    ListView,
    ListItem,
    Input
)
from rich.text import Text
from textual.screen import Screen, ModalScreen
from textual import events, work
from pathlib import Path
import os
from textual.reactive import reactive
from textual.message import Message
from textual import log
from textual import on

from textual.geometry import Offset, Region
from textual.coordinate import Coordinate

from typing import Any
import random

from time import time

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.renderables.gradient import LinearGradient
from textual.widgets import Static

class Sidebar(ScrollableContainer):
    def compose(self) -> ComposeResult:
        text = """
This is your receipt processor.

Here's the gist of it.
    You select a folder that in which images of receipts are stored.
    Make sure to set the one who paid by pressing 'p'. This will be used to decide who needs to pay what to whom later on.
    After pressing 'e' (extract directory) you will be led to the next page.

    There you will see a list of files (think receipts) in that folder.

On each file (highlighted in blue) you can run press 'e' to extract the receipt items into a table. This will also open the receipt in Preview so you can verify the extraction.
    Alternatively, you can skip a receipt by pressing 's'. The file will then be placed in a subfolder called 'skipped'.

    Once all files (receipts) have been dealt with (extracted or skipped), you will be presented led to the next page.

    Here you sort through each item from those receipts. Decide who consumed (and therefore should pay for) the item.

    Once all items are sorted, you will be presented of a final tally of the amounts that each person consumed and the final invoicing.

[bold]Note[/bold]: if you skipped a receipt, you will need to process it manually.

Otherwise, all receipts have been processed.
        """

        yield Label("[underline][bold]Receipt Processor[/bold][/underline]", classes='sidebar-title')
        yield Label(text, classes='sidebar-text')

class DurationRankingTable(DataTable):
    def __init__(self) -> None:
        super().__init__()
        self.data = []
        self.refresh()

    def compose(self) -> ComposeResult:
        self.add_columns('Rank', width=10)
        self.add_columns('User', width=20)
        self.add_columns('Duration (sec)', width=10)
        self.add_columns('Date', width=20)
        self.refresh()
        yield self.table

    def refresh(self):
        self.clear()
        self.data = self.app.database.query(
            query="""
            SELECT
                min_rank
                ,nick
                ,duration_seconds
                ,start_time
            FROM public.user_run
            WHERE duration_seconds IS NOT NULL
            ORDER BY duration_seconds DESC
            LIMIT 3;
            """,
            fetch='all'
        )
        for row in self.data:
            self.add_row(row[0], row[1], row[2], row[3])



class HistogramPlot(PlotextPlot):

    def __init__(self) -> None:
        super().__init__()
        self.plot = PlotextPlot()

    def compose(self) -> ComposeResult:
        yield self.plot

    def on_mount(self) -> None:
        plt = self.plot.plt
        plt.title("Histogram") # to apply a title
        l = 7 * 10 ** 2
        data1 = [random.gauss(0, 1) for el in range(10 * l)]
        plt.hist(data1, bins=50, label = "mean 0")
        # y = plt.sin() # sinusoidal test signal
        # plt.scatter(y)
