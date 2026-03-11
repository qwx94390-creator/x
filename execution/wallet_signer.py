import base64
import hashlib
import hmac
import time
from collections.abc import Callable


SignatureAlgorithm = Callable[[str, str], str]


class WalletSigner:
    """Signature template with pluggable algorithm.

    Default uses HMAC-SHA256(base64) over prehash text.
    Replace by passing `algorithm=` callable when exchange requires another scheme.
    """

    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        algorithm: SignatureAlgorithm | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.algorithm = algorithm or self._default_hmac_sha256

    @staticmethod
    def _default_hmac_sha256(secret: str, prehash: str) -> str:
        digest = hmac.new(secret.encode("utf-8"), prehash.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(digest).decode("utf-8")

    @staticmethod
    def build_prehash(timestamp: str, method: str, path: str, body: str) -> str:
        return f"{timestamp}{method.upper()}{path}{body}"

    def build_auth_headers(self, method: str, path: str, body: str = "") -> dict[str, str]:
        if not self.api_key or not self.api_secret:
            return {}

        timestamp = str(int(time.time() * 1000))
        prehash = self.build_prehash(timestamp, method, path, body)
        signature = self.algorithm(self.api_secret, prehash)

        return {
            "POLY_API_KEY": self.api_key,
            "POLY_PASSPHRASE": self.passphrase,
            "POLY_TIMESTAMP": timestamp,
            "POLY_SIGNATURE": signature,
        }
class WalletSigner:
    def sign(self, payload: dict) -> dict:
        return payload
