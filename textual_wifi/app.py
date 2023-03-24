import nmcli
from textual import log
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Input
from textual.widgets._data_table import Coordinate

from .app_header import WifiAppHeader
from .app_loading_indicator import WifiLoadingIndicator
from .app_password_input import PasswordInput
from .app_search import SearchInput
from .app_table import WifiTable
from .utils import run_background

nmcli.disable_use_sudo()


class WifiApp(App):
    CSS_PATH = "app.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_devices", "Refresh"),
        ("n", "next_search", "Next"),
        ("N", "prev_search", "Prev"),
    ]

    is_waiting = reactive(False)

    def compose(self) -> ComposeResult:
        yield WifiAppHeader()

        yield WifiLoadingIndicator()
        yield PasswordInput()
        yield SearchInput()
        yield WifiTable(id="data")

        yield Footer()

    def on_mount(self):
        self.action_refresh_devices()

    ################################################################################
    # ACTIONS
    def action_refresh_devices(self):
        if self.is_waiting:
            return
        self.is_waiting = True
        log("WifiApp is_waiting now true")

        table = self.query_one(WifiTable)

        def task(app):
            devices = nmcli.device.wifi()

            def callback():
                table.action_refresh_table(devices)
                self.is_waiting = False
                table.focus()

            app.call_from_thread(callback)

        run_background(task, self.app)

    def action_wifi_up_or_down(self):
        if self.is_waiting:
            return

        wifi_table = self.app.query_one(WifiTable)
        self.is_waiting = True

        def on_error(app):
            self.is_waiting = False
            app.query_one(PasswordInput).focus()

        def on_success():
            self.is_waiting = False
            self.action_refresh_devices()

        def task(app):
            try:
                if wifi_table.selected_device.in_use:
                    nmcli.connection.down(wifi_table.selected_device.ssid)
                else:
                    nmcli.connection.up(wifi_table.selected_device.ssid)
                log("WifiApp: Connection success")

                app.call_from_thread(on_success)

            except Exception as e:
                log(f"WifiApp: Connection error, trying with password: {e}")
                app.call_from_thread(on_error, app)

        run_background(task, self.app)

    def action_next_search(self):
        search_input = self.query_one(SearchInput)
        wifi_table = self.query_one(WifiTable)

        start = wifi_table.cursor_row + 1
        if start >= len(wifi_table.devices):
            start = 0

        # first search from the current coord till the end
        search_term = search_input.last_search.lower()
        for row, device in enumerate(wifi_table.devices[start:], start=start):
            if search_term in device.ssid.lower():
                wifi_table.cursor_coordinate = Coordinate(row, 0)
                break
        else:
            # then search from the beginning to the current coordinate
            if start != 0:
                for row, device in enumerate(wifi_table.devices[:start]):
                    if search_term in device.ssid.lower():
                        wifi_table.cursor_coordinate = Coordinate(row, 0)
                        break

    def action_prev_search(self):
        search_input = self.query_one(SearchInput)
        wifi_table = self.query_one(WifiTable)

        start = wifi_table.cursor_row
        if start == 0:
            start = len(wifi_table.devices) - 1

        search_term = search_input.last_search.lower()
        for row, device in reversed(list(enumerate(wifi_table.devices[:start]))):
            if search_term in device.ssid.lower():
                wifi_table.cursor_coordinate = Coordinate(row, 0)
                break
        else:
            # then search from the beginning to the current coordinate
            if start != len(wifi_table.devices) - 1:
                for row, device in reversed(
                    list(enumerate(wifi_table.devices[start:], start=start))
                ):
                    if search_term in device.ssid.lower():
                        wifi_table.cursor_coordinate = Coordinate(row, 0)
                        break

    ################################################################################
    # WATCH
    def watch_is_waiting(self, is_waiting):
        wifi_table = self.query_one(WifiTable)
        wifi_table.is_waiting = is_waiting

        loading_indicator = self.query_one(WifiLoadingIndicator)
        loading_indicator.is_waiting = is_waiting

    ################################################################################
    # GLOBAL INPUT HANDLER
    def on_input_submitted(self, msg: Input.Submitted):
        if isinstance(msg.input, SearchInput):
            self.on_search_input_submitted(msg)
        elif isinstance(msg.input, PasswordInput):
            self.on_password_input_submitted(msg)

    def on_input_changed(self, msg: Input.Changed):
        if isinstance(msg.input, SearchInput):
            self.on_search_input_changed(msg)

    ################################################################################
    # SEARCH HANDLER
    def on_wifi_table_search_requested(self, event):
        self.query_one(SearchInput).focus()

    def on_search_input_submitted(self, msg):
        search_input = self.query_one(SearchInput)
        search_input.last_search = search_input.value
        search_input.value = ""

        wifi_table = self.query_one(WifiTable)
        wifi_table.focus()

    def on_search_input_cancelled(self):
        search_input = self.query_one(SearchInput)
        search_input.value = ""

        wifi_table = self.query_one(WifiTable)
        wifi_table.focus()

    def on_search_input_changed(self, msg: Input.Changed):
        search_input = self.query_one(SearchInput)
        if not search_input.value:
            return

        wifi_table = self.query_one(WifiTable)

        search_term = search_input.value.lower()
        for row, device in enumerate(wifi_table.devices):
            if search_term in device.ssid.lower():
                wifi_table.cursor_coordinate = Coordinate(row, 0)
                break

    ################################################################################
    # DATA TABLE SELECTED HANDLER
    def on_data_table_cell_selected(self, msg: DataTable.CellSelected):
        """Trigger the wifi up / wifi down / input password action"""
        wifi_table = self.query_one(WifiTable)
        if not wifi_table.selected_device:
            return

        self.action_wifi_up_or_down()

    ################################################################################
    # PASSWORD HANDLER
    def on_password_input_cancelled(self):
        wifi_table = self.query_one(WifiTable)
        wifi_table.focus()

        password_input = self.query_one(PasswordInput)
        password_input.value = ""

    def on_password_input_submitted(self, msg: PasswordInput.Submitted):
        wifi_table = self.app.query_one(WifiTable)
        wifi_table.focus()
        self.is_waiting = True

        password_input = self.query_one(PasswordInput)
        password_input.value = ""

        def on_error():
            self.is_waiting = False

        def on_success():
            self.is_waiting = False
            self.action_refresh_devices()

        def task(app, password):
            try:
                nmcli.device.wifi_connect(wifi_table.selected_device.ssid, password)
                app.call_from_thread(on_success)
            except Exception as e:
                log(f"PasswordInput: error submitting password: {e}")
                app.call_from_thread(on_error)

        password = msg.value
        run_background(task, self.app, password)
