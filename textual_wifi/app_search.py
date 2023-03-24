from textual.message import Message
from textual.widgets import Input


class SearchInput(Input):
    class Cancelled(Message):
        pass

    BINDINGS = [
        ("escape,tab", "pop_input_cancelled", "cancel"),
    ]

    last_search = ""

    def __init__(self):
        super().__init__()

    ################################################################################
    # HANDLERS
    def on_mount(self):
        self.add_class("hidden")

    def watch_has_focus(self):
        if self.has_focus:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")

    ################################################################################
    # ACTIONS
    def action_pop_input_cancelled(self):
        self.post_message(self.Cancelled())
