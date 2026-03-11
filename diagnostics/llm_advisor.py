import os

import httpx


class LLMAdvisor:
    def __init__(self, provider: str = "", api_key: str = "", model: str = "", base_url: str = "") -> None:
        self.provider = provider
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model
        self.base_url = base_url

    def enabled(self) -> bool:
        return bool(self.api_key and self.model and self.base_url)

    def diagnose(self, report: dict) -> str:
        if not self.enabled():
            return "LLM diagnosis disabled (missing api key/model/base_url)."

        prompt = (
            "你是量化交易风控顾问。请根据日报给出：1) 收益/亏损主要原因；"
            "2) 可执行的参数优化建议；3) 次日风险提示。\n"
            f"日报数据: {report}"
        )

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是严谨的量化交易诊断助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            resp = httpx.post(self.base_url, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            return f"LLM diagnosis unavailable: {exc}"
