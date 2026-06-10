"""Async Hacker News client. Wraps the public Firebase HN API + Algolia HN search.

Public APIs, no credentials.
- HN Firebase API: https://github.com/HackerNews/API
- Algolia HN Search: https://hn.algolia.com/api
"""

import asyncio
import logging
import time
from typing import Any, Optional

import httpx

log = logging.getLogger(__name__)

FIREBASE_BASE = "https://hacker-news.firebaseio.com/v0"
ALGOLIA_BASE = "https://hn.algolia.com/api/v1"
TIMEOUT = httpx.Timeout(10.0)

CATEGORY_ENDPOINT = {
    "top": "topstories",
    "new": "newstories",
    "best": "beststories",
    "ask": "askstories",
    "show": "showstories",
    "job": "jobstories",
}


class HNError(Exception):
    """Raised for any HN API request failure."""


async def _firebase_get(client: httpx.AsyncClient, path: str) -> Any:
    try:
        r = await client.get(f"{FIREBASE_BASE}/{path}.json")
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        raise HNError(f"HN Firebase API failed for /{path}: {e}") from e


async def _algolia_get(client: httpx.AsyncClient, path: str, params: dict) -> Any:
    try:
        r = await client.get(f"{ALGOLIA_BASE}/{path}", params=params)
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        raise HNError(f"Algolia HN API failed for /{path}: {e}") from e


async def get_item(item_id: int) -> Optional[dict]:
    """Fetch a single item (story / comment / job / poll) by id."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        return await _firebase_get(client, f"item/{item_id}")


async def _fetch_many(item_ids: list[int], concurrency: int = 20) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        async def fetch_one(sid: int) -> Optional[dict]:
            async with sem:
                try:
                    return await _firebase_get(client, f"item/{sid}")
                except HNError as e:
                    log.warning("skip item %s: %s", sid, e)
                    return None
        results = await asyncio.gather(*[fetch_one(i) for i in item_ids])
    return [r for r in results if r]


async def get_category(category: str, limit: int = 10) -> list[dict]:
    """Fetch stories from one of: top, new, best, ask, show, job."""
    if category not in CATEGORY_ENDPOINT:
        raise HNError(
            f"Unknown HN category: {category!r}. "
            f"Allowed: {', '.join(CATEGORY_ENDPOINT.keys())}"
        )
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        ids = await _firebase_get(client, CATEGORY_ENDPOINT[category])
    if not ids:
        return []
    return await _fetch_many(ids[:limit])


async def get_top_window(
    limit: int = 10, hours: int = 24, scan_limit: int = 200
) -> list[dict]:
    """Top stories within the last `hours` window, ranked by score.

    Scans up to `scan_limit` current top stories, filters by age, returns top `limit`.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        ids = await _firebase_get(client, "topstories")
    if not ids:
        return []
    items = await _fetch_many(ids[:scan_limit])
    cutoff = time.time() - hours * 3600
    fresh = [
        it for it in items
        if it and it.get("type") == "story" and it.get("time", 0) >= cutoff
    ]
    fresh.sort(key=lambda x: x.get("score", 0), reverse=True)
    return fresh[:limit]


async def get_comments(item_id: int, limit: int = 10) -> list[dict]:
    """Top-level comments for a story, in HN ranking order."""
    story = await get_item(item_id)
    if not story:
        return []
    kids = story.get("kids") or []
    if not kids:
        return []
    comments = await _fetch_many(kids[:limit])
    return [c for c in comments if c.get("type") == "comment" and not c.get("deleted")]


async def search(query: str, sort: str = "relevance", limit: int = 20) -> dict:
    """Full-text search across HN posts and comments via Algolia.

    sort: "relevance" (default) or "date" (newest first).
    """
    path = "search" if sort == "relevance" else "search_by_date"
    params = {"query": query, "hitsPerPage": limit}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        return await _algolia_get(client, path, params)
