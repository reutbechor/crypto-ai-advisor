# Future Recommendation Improvement Using User Feedback

User feedback can be stored in the database together with the user, content item, content type, and additional attributes such as the related cryptocurrency or topic.

Over time, the system can calculate simple preference scores and use them to determine which content should receive higher priority for each user.

## Preference Score

The preference score can be calculated as follows:

```text
Preference Score = (Likes - Dislikes) / (Likes + Dislikes)
```

A score closer to `1` means that the user usually likes that type of content, while a score closer to `-1` means that the user usually dislikes it.

## Example 1: Learning the Preferred Content Type

Suppose a user provides the following feedback:

| Content type | Likes | Dislikes | Preference score |
| --- | ---: | ---: | ---: |
| Market News | 8 | 2 | `(8 - 2) / (8 + 2) = 0.60` |
| AI Insights | 6 | 1 | `(6 - 1) / (6 + 1) ≈ 0.71` |
| Meme content | 2 | 6 | `(2 - 6) / (2 + 6) = -0.50` |

The system can learn that this user strongly prefers AI Insights and Market News, while meme content is less relevant.

In future dashboard sessions, AI-generated insights and market news could receive higher priority, while meme content could be shown less often or placed lower in the dashboard.

## Example 2: Learning Crypto Asset Preferences

The same method can be applied to the cryptocurrency associated with each content item. Suppose the user gives positive feedback mainly to Ethereum-related content:

| Crypto asset | Likes | Dislikes | Preference score |
| --- | ---: | ---: | ---: |
| Ethereum | 9 | 1 | `(9 - 1) / (9 + 1) = 0.80` |
| Bitcoin | 4 | 4 | `(4 - 4) / (4 + 4) = 0.00` |
| Solana | 2 | 5 | `(2 - 5) / (2 + 5) ≈ -0.43` |

When several new Market News or AI Insight items are available, the dashboard could:

- Prioritize Ethereum-related content
- Give neutral priority to Bitcoin-related content
- Assign lower priority to Solana-related content

The system could also combine several characteristics. For example, if a user repeatedly likes content associated with both Ethereum and AI Insights, items with this combination could receive a higher recommendation score than content that does not match the user's learned preferences.

## Personalization Loop

```text
Content shown
      ↓
User feedback
      ↓
Stored preference scores
      ↓
Better content ranking
      ↓
More personalized future content
```

Initially, this could be implemented as a recommendation-ranking mechanism without retraining the language model itself.

Later, after enough feedback has been collected, stored and anonymized feedback could also be used to:

- Improve prompts
- Evaluate recommendation quality
- Train a dedicated personalization model
