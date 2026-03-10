import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class ClobResponse:
    ok: bool
    status_code: int
    data: dict[str, Any]
    error: str = ""


class ClobClient:
    def __init__(self, api_url: str, timeout_sec: int = 10) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout_sec = timeout_sec

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ClobResponse:
        url = f"{self.api_url}{path}"
        body: bytes | None = None
        final_headers = {"Content-Type": "application/json"}
        if headers:
            final_headers.update(headers)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = Request(url=url, data=body, method=method.upper(), headers=final_headers)
        try:
            with urlopen(req, timeout=self.timeout_sec) as resp:  # nosec B310
                text = resp.read().decode("utf-8")
                data = json.loads(text) if text else {}
                return ClobResponse(ok=True, status_code=getattr(resp, "status", 200), data=data)
        except HTTPError as exc:
            raw = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
            return ClobResponse(ok=False, status_code=exc.code, data={}, error=raw or str(exc))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            return ClobResponse(ok=False, status_code=0, data={}, error=str(exc))

    def create_order(self, payload: dict[str, Any], headers: dict[str, str] | None = None) -> ClobResponse:
        return self._request("POST", "/order", payload=payload, headers=headers)

    def cancel_order(self, order_id: str, headers: dict[str, str] | None = None) -> ClobResponse:
        return self._request("DELETE", f"/order/{order_id}", headers=headers)

    def get_order(self, order_id: str, headers: dict[str, str] | None = None) -> ClobResponse:
        return self._request("GET", f"/order/{order_id}", headers=headers)

    def list_open_orders(self, headers: dict[str, str] | None = None) -> ClobResponse:
        return self._request("GET", "/orders", headers=headers)
