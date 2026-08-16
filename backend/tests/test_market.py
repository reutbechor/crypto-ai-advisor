import httpx
import logging

from app.services import market


def coin_payload(identifier, name, symbol, price):
    return {
        "id": identifier,
        "name": name,
        "symbol": symbol,
        "current_price": price,
        "price_change_percentage_24h": 1.25,
        "market_cap": 1_000_000,
        "last_updated": "2026-08-16T09:00:00Z",
    }


class FakeResponse:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


class FakeClient:
    def __init__(self, response, calls):
        self.response = response
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def test_market_requests_only_selected_assets_and_preserves_preference_order(monkeypatch):
    calls = []
    demo_key = "test-demo-key-not-a-real-secret"
    payload = [
        coin_payload("bitcoin", "Bitcoin", "btc", 60_000),
        coin_payload("ethereum", "Ethereum", "eth", 3_000),
        coin_payload("ripple", "XRP", "xrp", 0.55),
    ]
    monkeypatch.setattr(
        market.httpx,
        "Client",
        lambda **_kwargs: FakeClient(FakeResponse(payload), calls),
    )
    monkeypatch.setattr(market, "COINGECKO_API_KEY", demo_key)

    coins, status = market.fetch_market_data(["ripple", "bitcoin"])

    assert status == "available"
    assert [coin.id for coin in coins] == ["ripple", "bitcoin"]
    assert all(coin.id != "ethereum" for coin in coins)
    assert calls[0][0] == "https://api.coingecko.com/api/v3/coins/markets"
    assert calls[0][1]["params"]["ids"] == "ripple,bitcoin"
    assert calls[0][1]["params"]["vs_currency"] == "usd"
    assert calls[0][1]["headers"]["x-cg-demo-api-key"] == demo_key
    assert "x-cg-pro-api-key" not in calls[0][1]["headers"]
    assert demo_key not in "".join(coin.model_dump_json() for coin in coins)


def test_market_missing_demo_key_keeps_keyless_local_behavior(monkeypatch):
    calls = []
    payload = [coin_payload("bitcoin", "Bitcoin", "btc", 60_000)]
    monkeypatch.setattr(market, "COINGECKO_API_KEY", None)
    monkeypatch.setattr(
        market.httpx,
        "Client",
        lambda **_kwargs: FakeClient(FakeResponse(payload), calls),
    )

    coins, status = market.fetch_market_data(["bitcoin"])

    assert status == "available"
    assert [coin.id for coin in coins] == ["bitcoin"]
    assert "x-cg-demo-api-key" not in calls[0][1]["headers"]


def test_market_provider_failures_return_a_safe_unavailable_state(monkeypatch):
    request = httpx.Request("GET", market.COINGECKO_MARKETS_URL)
    provider_error = httpx.HTTPStatusError(
        "provider detail that must stay internal",
        request=request,
        response=httpx.Response(503, request=request),
    )
    cases = [
        FakeResponse([], httpx.ReadTimeout("timeout", request=request)),
        FakeResponse([], provider_error),
        FakeResponse({"unexpected": "shape"}),
        FakeResponse([coin_payload("bitcoin", "Bitcoin", "btc", 60_000)]),
    ]

    for response in cases:
        monkeypatch.setattr(
            market.httpx,
            "Client",
            lambda response=response, **_kwargs: FakeClient(response, []),
        )
        coins, status = market.fetch_market_data(["bitcoin", "ethereum"])

        assert coins == []
        assert status == "unavailable"


def test_market_http_error_logs_safe_debug_context_without_secrets(
    monkeypatch,
    caplog,
):
    demo_key = "private-test-demo-key"
    request = httpx.Request(
        "GET",
        f"{market.COINGECKO_MARKETS_URL}?ids=bitcoin",
        headers={"x-cg-demo-api-key": demo_key},
    )
    response = httpx.Response(
        401,
        request=request,
        text=f"Invalid API key: {demo_key}\nAuthorization: Bearer private-token",
    )
    error = httpx.HTTPStatusError(
        "request failed",
        request=request,
        response=response,
    )
    monkeypatch.setattr(market, "COINGECKO_API_KEY", demo_key)
    monkeypatch.setattr(
        market.httpx,
        "Client",
        lambda **_kwargs: FakeClient(FakeResponse([], error), []),
    )

    with caplog.at_level(logging.WARNING, logger="app.services.market"):
        coins, status = market.fetch_market_data(["bitcoin"])

    log_message = caplog.text
    assert coins == []
    assert status == "unavailable"
    assert "status=401" in log_message
    assert f"url={market.COINGECKO_MARKETS_URL}" in log_message
    assert "?ids=bitcoin" not in log_message
    assert "response=Invalid API key: [REDACTED]" in log_message
    assert demo_key not in log_message
    assert "private-token" not in log_message
    assert "x-cg-demo-api-key" not in log_message
