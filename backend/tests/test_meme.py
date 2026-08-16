import unittest
from unittest.mock import Mock, patch

import httpx

from app.services.meme import _normalize_candidate, fetch_meme


def make_candidate(**overrides):
    candidate = {
        "postLink": "https://redd.it/example1",
        "subreddit": "CryptoCurrencyMemes",
        "title": "How it feels to hold Bitcoin through another market cycle",
        "url": "https://i.redd.it/example1.png",
        "nsfw": False,
        "spoiler": False,
    }
    candidate.update(overrides)
    return candidate


class MemeFilteringTests(unittest.TestCase):
    def test_normalizes_safe_crypto_image(self):
        meme = _normalize_candidate(make_candidate())

        self.assertIsNotNone(meme)
        self.assertEqual(meme.id, "reddit-example1")
        self.assertEqual(meme.image_url, "https://i.redd.it/example1.png")

    def test_rejects_unsafe_or_unsupported_items(self):
        cases = [
            {"nsfw": True},
            {"spoiler": True},
            {"is_video": True},
            {"is_gallery": True},
            {"subreddit": "memes"},
            {"url": "https://i.redd.it/video.mp4"},
            {"url": "https://untrusted.example/meme.png"},
            {"title": "A political war meme about Russia"},
        ]

        for overrides in cases:
            with self.subTest(overrides=overrides):
                self.assertIsNone(_normalize_candidate(make_candidate(**overrides)))


class MemeProviderTests(unittest.TestCase):
    @patch("app.services.meme.secrets.choice", side_effect=lambda values: values[0])
    @patch("app.services.meme.httpx.Client")
    def test_fetches_once_and_selects_filtered_candidate(self, client_class, _choice):
        response = Mock()
        response.json.return_value = {
            "memes": [
                make_candidate(nsfw=True),
                make_candidate(postLink="https://redd.it/safe2", url="https://i.redd.it/safe2.webp"),
            ]
        }
        client = client_class.return_value.__enter__.return_value
        client.get.return_value = response

        meme, status = fetch_meme()

        client.get.assert_called_once()
        response.raise_for_status.assert_called_once()
        self.assertEqual(status, "available")
        self.assertEqual(meme.id, "reddit-safe2")

    @patch("app.services.meme.secrets.choice", side_effect=lambda values: values[0])
    @patch("app.services.meme.httpx.Client")
    def test_provider_timeout_returns_local_fallback(self, client_class, _choice):
        client = client_class.return_value.__enter__.return_value
        client.get.side_effect = httpx.TimeoutException("provider timed out")

        meme, status = fetch_meme()

        client.get.assert_called_once()
        self.assertEqual(status, "fallback")
        self.assertTrue(meme.id.startswith("coinsight-"))
        self.assertTrue(meme.image_url.startswith("/memes/"))

    @patch("app.services.meme.secrets.choice", side_effect=lambda values: values[0])
    @patch("app.services.meme.httpx.Client")
    def test_no_safe_image_returns_local_fallback(self, client_class, _choice):
        response = Mock()
        response.json.return_value = {"memes": [make_candidate(url="https://i.redd.it/clip.gif")]}
        client = client_class.return_value.__enter__.return_value
        client.get.return_value = response

        meme, status = fetch_meme()

        client.get.assert_called_once()
        self.assertEqual(status, "fallback")
        self.assertIsNotNone(meme)


if __name__ == "__main__":
    unittest.main()
