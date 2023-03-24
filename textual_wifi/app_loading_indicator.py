from textual import log
from textual.reactive import reactive
from textual.widgets import LoadingIndicator


class WifiLoadingIndicator(LoadingIndicator):
    is_waiting = reactive(False)

    def watch_is_waiting(self, is_waiting):
        log(f"WifiLoadingIndicator::watch_is_waiting: is_waiting({is_waiting})")
        if is_waiting:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")
