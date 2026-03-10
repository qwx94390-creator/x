class MultiNotifier:
    def __init__(self, notifiers: list) -> None:
        self.notifiers = notifiers

    def send_message(self, message: str) -> None:
        for notifier in self.notifiers:
            notifier.send_message(message)
