from urllib.parse import urlencode
from urllib.request import urlopen
import httpx


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message: str) -> None:
        if not self.token or not self.chat_id:
            return
        data = urlencode({"chat_id": self.chat_id, "text": message}).encode("utf-8")
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            with urlopen(url, data=data, timeout=5):  # nosec B310
                return
        except Exception:
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        httpx.post(url, data={"chat_id": self.chat_id, "text": message}, timeout=5)
