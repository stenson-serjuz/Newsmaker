from __future__ import annotations

import aiohttp


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NewsmakerBot/1.0)"
    ),
}


async def fetch_html(
    url: str,
    *,
    timeout: int = 10,
) -> str | None:
    try:
        client_timeout = (
            aiohttp.ClientTimeout(
                total=timeout,
            )
        )

        async with aiohttp.ClientSession(
            timeout=client_timeout,
            headers=HEADERS,
        ) as session:
            async with session.get(
                url,
                allow_redirects=True,
            ) as response:
                if response.status != 200:
                    return None

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    )
                )

                if "text/html" not in (
                    content_type.lower()
                ):
                    return None

                return await response.text()

    except Exception:
        return None
