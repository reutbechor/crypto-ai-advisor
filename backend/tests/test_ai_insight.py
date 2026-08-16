import httpx
from unittest.mock import Mock

from app.schemas.dashboard import MarketCoinResponse
from app.services import ai_insight


SAFE_INSIGHT = " ".join(
    "Bitcoin and Ethereum show measured movement across the available market data. "
    "For a day trader, relative volatility and liquidity provide useful context when "
    "reviewing short term behavior. Comparing several time windows can distinguish a "
    "temporary fluctuation from a broader change, while uncertainty and personal risk "
    "limits remain important parts of any independent market review.".split()
)


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

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def market_coin():
    return MarketCoinResponse(
        id="bitcoin",
        name="Bitcoin",
        symbol="btc",
        current_price=60_000,
        price_change_percentage_24h=1.5,
    )


def test_ai_success_uses_supplied_context_without_fetching_market_again(monkeypatch):
    calls = []
    unexpected_market_fetch = Mock()
    monkeypatch.setattr(ai_insight, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        ai_insight.httpx,
        "Client",
        lambda **_kwargs: FakeClient(
            FakeResponse({"choices": [{"message": {"content": SAFE_INSIGHT}}]}),
            calls,
        ),
    )
    monkeypatch.setattr(
        "app.services.market.fetch_market_data",
        unexpected_market_fetch,
    )

    insight, status = ai_insight.generate_ai_insight(
        "day_trader", ["bitcoin", "ethereum"], [market_coin()]
    )

    prompt = calls[0][1]["json"]["messages"][1]["content"]
    assert status == "available"
    assert insight.content == SAFE_INSIGHT
    assert "day-trader profile" in prompt
    assert "Bitcoin, Ethereum" in prompt
    assert "$60,000.00" in prompt
    assert calls[0][1]["headers"]["Authorization"] == "Bearer test-key"
    unexpected_market_fetch.assert_not_called()


def test_ai_provider_failures_use_safe_fallback_without_exposing_errors(monkeypatch):
    request = httpx.Request("POST", ai_insight.OPENROUTER_CHAT_URL)
    provider_error = httpx.HTTPStatusError(
        "secret provider response",
        request=request,
        response=httpx.Response(500, request=request),
    )
    responses = [
        FakeResponse({}, httpx.ReadTimeout("private timeout", request=request)),
        FakeResponse({}, provider_error),
        FakeResponse({"choices": []}),
        FakeResponse({"choices": [{"message": {"content": "too short"}}]}),
        FakeResponse({"choices": [{"message": {"content": "You should buy now " + SAFE_INSIGHT}}]}),
    ]

    monkeypatch.setattr(ai_insight, "OPENROUTER_API_KEY", "test-key")
    for response in responses:
        monkeypatch.setattr(
            ai_insight.httpx,
            "Client",
            lambda response=response, **_kwargs: FakeClient(response, []),
        )
        insight, status = ai_insight.generate_ai_insight(
            "hodler", ["bitcoin"], [market_coin()]
        )

        assert status == "fallback"
        assert "secret provider response" not in insight.content
        assert "private timeout" not in insight.content
        assert insight.generated_for.crypto_assets == ["bitcoin"]

    monkeypatch.setattr(ai_insight, "OPENROUTER_API_KEY", "")
    monkeypatch.setattr(
        ai_insight.httpx,
        "Client",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("HTTP must not run")),
    )
    _, status = ai_insight.generate_ai_insight("hodler", ["bitcoin"], [])
    assert status == "fallback"

