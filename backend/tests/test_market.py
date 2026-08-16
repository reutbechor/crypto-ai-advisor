import httpx

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

    coins, status = market.fetch_market_data(["ripple", "bitcoin"])

    assert status == "available"
    assert [coin.id for coin in coins] == ["ripple", "bitcoin"]
    assert all(coin.id != "ethereum" for coin in coins)
    assert calls[0][1]["params"]["ids"] == "ripple,bitcoin"
    assert calls[0][1]["params"]["vs_currency"] == "usd"


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

