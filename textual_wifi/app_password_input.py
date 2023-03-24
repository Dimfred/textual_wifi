from textual.message import Message
from textual.widgets import Input


class PasswordInput(Input):
    class Cancelled(Message):
        pass

    BINDINGS = [
        ("escape", "pop_input_cancelled", "cancel"),
        ("tab", "pop_input_cancelled", "cancel"),
    ]

    def __init__(self):
        super().__init__(password=True)

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
