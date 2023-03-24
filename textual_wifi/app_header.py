from textual.widgets import Header
from textual.widgets._header import HeaderIcon


class WifiAppHeader(Header):
    HEADER_ICON = ""

    def on_mount(self):
        self.query_one(HeaderIcon).icon = WifiAppHeader.HEADER_ICON
