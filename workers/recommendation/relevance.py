from __future__ import annotations


class RelevanceScorer:
    def score(
        self,
        *,
        user_city: str | None,
        user_category: str | None,
        user_language: str | None,
        user_urgency: str | None,
        news_city: str | None,
        news_category: str | None,
        news_language: str | None,
        news_urgency: str | None,
        priority_score: int,
    ) -> int:
        score = 0

        if (
            user_city
            and user_city == news_city
        ):
            score += 30

        if (
            user_category
            and user_category
            == news_category
        ):
            score += 40

        if (
            user_language
            and user_language
            == news_language
        ):
            score += 10

        if (
            user_urgency
            and user_urgency
            == news_urgency
        ):
            score += 20

        score += int(
            priority_score * 0.3
        )

        return min(score, 100)
