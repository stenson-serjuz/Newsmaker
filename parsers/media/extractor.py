from __future__ import annotations

from bs4 import BeautifulSoup


def extract_og_image(
    html: str,
) -> str | None:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    tag = soup.find(
        "meta",
        property="og:image",
    )

    if not tag:
        return None

    content = tag.get("content")

    if not content:
        return None

    content = content.strip()

    if not content.startswith(
        (
            "http://",
            "https://",
        )
    ):
        return None

    return content
