"""MCP server exposing Hacker News tools to AI agents.

By NeCL (https://neclco.com). Public HN API, no credentials.
"""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from . import hn

mcp = FastMCP("necl-hn-mcp")


def _hn_url(item_id: int) -> str:
    return f"https://news.ycombinator.com/item?id={item_id}"


def _format_story(item: dict) -> dict:
    """Shape a Firebase HN item into a stable, LLM-friendly dict."""
    item_id = item.get("id")
    hn_link = _hn_url(item_id) if item_id else None
    external_url = item.get("url")
    return {
        "id": item_id,
        "title": item.get("title"),
        "url": external_url or hn_link,
        "score": item.get("score", 0),
        "author": item.get("by"),
        "comments_count": item.get("descendants", 0),
        "posted_unix": item.get("time"),
        "hn_url": hn_link,
        "type": item.get("type", "story"),
        "text": (item.get("text") or "").strip() or None,
    }


def _format_comment(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "author": item.get("by"),
        "text": (item.get("text") or "").strip(),
        "posted_unix": item.get("time"),
        "replies_count": len(item.get("kids") or []),
    }


@mcp.tool()
async def hn_top_stories(limit: int = 10, hours: int = 24) -> list[dict]:
    """Get the top Hacker News stories from the last N hours, ranked by score.

    Args:
        limit: Number of stories to return (1-30). Default 10.
        hours: Time window in hours back from now. Default 24.

    Returns:
        List of story dicts with id, title, url, score, author, comments_count,
        posted_unix, hn_url, type, text (for Ask/Show HN posts).
    """
    limit = max(1, min(int(limit), 30))
    hours = max(1, min(int(hours), 168))  # cap at 1 week
    items = await hn.get_top_window(limit=limit, hours=hours)
    return [_format_story(i) for i in items]


@mcp.tool()
async def hn_category(
    category: Literal["top", "new", "best", "ask", "show", "job"] = "top",
    limit: int = 10,
) -> list[dict]:
    """Get stories from a specific HN category.

    Args:
        category: One of "top", "new", "best", "ask", "show", "job".
        limit: Number of stories to return (1-30). Default 10.

    Returns:
        List of story dicts.
    """
    limit = max(1, min(int(limit), 30))
    items = await hn.get_category(category=category, limit=limit)
    return [_format_story(i) for i in items]


@mcp.tool()
async def hn_get_story(story_id: int) -> dict:
    """Get full metadata for a single HN story by id.

    Args:
        story_id: The HN item id.

    Returns:
        Story dict with id, title, url, score, author, comments_count, posted_unix,
        hn_url, type, text. Returns {"error": "..."} if not found.
    """
    item = await hn.get_item(int(story_id))
    if not item:
        return {"error": f"Story {story_id} not found."}
    return _format_story(item)


@mcp.tool()
async def hn_get_comments(story_id: int, limit: int = 10) -> list[dict]:
    """Get the top-level comments thread for a story, in HN ranking order.

    Args:
        story_id: The HN item id of the parent story.
        limit: Number of comments to return (1-30). Default 10.

    Returns:
        List of comment dicts with id, author, text, posted_unix, replies_count.
    """
    limit = max(1, min(int(limit), 30))
    comments = await hn.get_comments(int(story_id), limit=limit)
    return [_format_comment(c) for c in comments]


def _format_algolia_hit(hit: dict) -> dict:
    """Shape an Algolia HN hit into a stable, LLM-friendly dict."""
    obj_id = hit.get("objectID")
    item_id = int(obj_id) if obj_id and str(obj_id).isdigit() else None
    return {
        "id": item_id,
        "kind": "comment" if hit.get("comment_text") else "story",
        "title": hit.get("title") or hit.get("story_title"),
        "url": hit.get("url"),
        "hn_url": _hn_url(item_id) if item_id else None,
        "author": hit.get("author"),
        "points": hit.get("points"),
        "comments_count": hit.get("num_comments"),
        "story_text": (hit.get("story_text") or "").strip() or None,
        "comment_text": (hit.get("comment_text") or "").strip() or None,
        "created_at": hit.get("created_at"),
        "tags": hit.get("_tags"),
    }


@mcp.tool()
async def hn_search(
    query: str,
    sort: Literal["relevance", "date"] = "relevance",
    limit: int = 20,
) -> dict:
    """Full-text search across HN stories and comments via Algolia.

    Args:
        query: Search query string.
        sort: "relevance" (default) or "date" (newest first).
        limit: Number of hits to return (1-50). Default 20.

    Returns:
        Dict with `hits` (list of clean dicts: id, kind, title, url, hn_url,
        author, points, comments_count, story_text, comment_text, created_at, tags)
        and `total_hits` (total matches Algolia found, may exceed limit).
    """
    limit = max(1, min(int(limit), 50))
    raw = await hn.search(query=query, sort=sort, limit=limit)
    hits = [_format_algolia_hit(h) for h in raw.get("hits") or []]
    return {
        "hits": hits,
        "total_hits": raw.get("nbHits", len(hits)),
        "query": query,
        "sort": sort,
    }
