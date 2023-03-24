from textual import log
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable
from textual.widgets._data_table import Coordinate


class WifiTable(DataTable):
    class SearchRequested(Message):
        pass

    HEADER = ("SSID", "Signal", "Security", "Connected")
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("left", "", ""),
        ("right", "", ""),
        ("slash", "pop_search_requested", "Search"),
    ]

    is_waiting = reactive(False)
    devices = []
    last_cursor_row = 0
    selected_device = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_columns(*WifiTable.HEADER)

    def action_refresh_table(self, devices):
        self.clear()
        self.devices = [dev for dev in devices if dev.ssid]

        data = [
            (
                dev.ssid,
                dev.signal,
                dev.security,
                "[green]*[/green]" if dev.in_use else "",
            )
            for dev in self.devices
            if dev.ssid
        ]
        self.add_rows(data)

        if self.last_cursor_row < len(self.devices):
            self.cursor_coordinate = Coordinate(self.last_cursor_row, 0)
        else:
            self.last_cursor_row = 0

    def action_pop_search_requested(self):
        self.post_message(self.SearchRequested())

    ################################################################################
    # HANDLERS
    def watch_is_waiting(self, is_waiting):
        log(f"WifiTable::watch_is_waiting: is_waiting({is_waiting})")
        if is_waiting:
            self.add_class("hidden")
        else:
            self.remove_class("hidden")

    def on_data_table_cell_highlighted(self, msg: DataTable.CellHighlighted):
        """Change the currently selected device in the table"""
        self.selected_device = next(
            dev for dev in self.devices if dev.ssid == msg.value
        )
        self.last_cursor_row = self.cursor_row
