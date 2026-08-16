from app.services.news import select_personalized_news


def test_news_prioritizes_assets_then_general_items_without_duplicates():
    solana_news, status = select_personalized_news(["solana"], limit=4)
    bitcoin_news, _ = select_personalized_news(["bitcoin"], limit=4)

    assert status == "fallback"
    assert [item.id for item in solana_news[:2]] == ["sol-001", "sol-002"]
    assert all(item.related_assets == ["general"] for item in solana_news[2:])
    assert len({item.id for item in solana_news}) == len(solana_news)
    assert solana_news[0].id != bitcoin_news[0].id
    assert all(item.source == "CoinSight Market Brief" for item in solana_news)
    assert all(item.title and item.summary and item.content for item in solana_news)
    assert all(item.published_at for item in solana_news)

