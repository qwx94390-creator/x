from execution.wallet_signer import WalletSigner


def test_wallet_signer_build_headers_with_default_algo():
    signer = WalletSigner(api_key="k", api_secret="s", passphrase="p")
    headers = signer.build_auth_headers(method="POST", path="/order", body='{"a":1}')
    assert headers["POLY_API_KEY"] == "k"
    assert headers["POLY_PASSPHRASE"] == "p"
    assert "POLY_SIGNATURE" in headers
    assert "POLY_TIMESTAMP" in headers


def test_wallet_signer_supports_custom_algorithm():
    signer = WalletSigner(
        api_key="k",
        api_secret="s",
        passphrase="p",
        algorithm=lambda secret, prehash: f"{secret}:{prehash}",
    )
    headers = signer.build_auth_headers(method="GET", path="/orders", body="")
    assert headers["POLY_SIGNATURE"].startswith("s:")
