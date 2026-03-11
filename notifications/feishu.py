import httpx


class FeishuNotifier:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send_message(self, message: str) -> None:
        if not self.webhook_url:
            return
        payload = {
            "msg_type": "text",
            "content": {
                "text": message,
            },
        }
        httpx.post(self.webhook_url, json=payload, timeout=5)
