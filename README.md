# necl-hn-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-9370DB.svg)](./LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-9370DB)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/python-3.10+-9370DB.svg)](https://www.python.org/downloads/)
[![Built by NeCL](https://img.shields.io/badge/Built_by-NeCL-9370DB)](https://neclco.com)

> **Hacker News tools for AI agents.** Top stories, story details, comments thread, full-text search.
>
> **Zero credentials.** Public HN API. Install and use.

Built by [NeCL](https://neclco.com) — AI engineering studio. Production-tested in our own content pipelines (powers [baraban_agent](https://github.com/adjacentai/necl/tree/main/03_DEV/baraban_agent), our internal HN→drafts engine running 3× daily for months).

## Tools

| Tool | What it does |
|---|---|
| `hn_top_stories(limit, hours)` | Top N stories from the last N hours, ranked by score. Default: top 10 from last 24h. |
| `hn_get_story(id)` | Full story metadata: title, url, score, author, comments count, posted time. |
| `hn_get_comments(id, limit)` | Top-level comments thread for a story, sorted by HN ranking. |
| `hn_search(query, sort)` | Full-text search across HN posts and comments (via Algolia HN API). |
| `hn_category(category, limit)` | Stories from a specific category: `top`, `new`, `best`, `ask`, `show`, `job`. |

## Why this MCP

- **Zero credentials, zero config** — public HN API, no rate limits worth worrying about, no signup.
- **Battle-tested code** — extracted from [baraban_agent](https://github.com/adjacentai/necl/tree/main/03_DEV/baraban_agent), our internal HN-to-drafts content engine that's been running 3×/day for months.
- **Built for AI agents** — every tool returns clean structured data that LLMs can chain together (search → top story → comments → summary).
- **Use case** — content research, trend monitoring, automatic news digests, prompt-context enrichment.

## Install

### Via Smithery (recommended)

```bash
npx -y @smithery/cli install necl-hn-mcp --client claude
```

### Via Claude Desktop / Claude Code config

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "necl-hn": {
      "command": "uvx",
      "args": ["necl-hn-mcp"]
    }
  }
}
```

Or if you prefer pip:

```json
{
  "mcpServers": {
    "necl-hn": {
      "command": "python",
      "args": ["-m", "necl_hn_mcp"]
    }
  }
}
```

### From source

```bash
git clone https://github.com/adjacentai/necl-hn-mcp.git
cd necl-hn-mcp
pip install -e .
```

Then add to your MCP client config:
```json
{
  "mcpServers": {
    "necl-hn": {
      "command": "python",
      "args": ["-m", "necl_hn_mcp"]
    }
  }
}
```

## Example use in Claude

Once installed, just ask Claude things like:

- "What are the top 5 stories on HN in the last 6 hours?"
- "Get the comments thread for HN story 38420000"
- "Search HN for posts about RAG performance, sorted by date"
- "Show me everything in the Ask HN category right now"
- "Find the top 3 Show HN posts about AI agents this week"

Claude will call the right tool, no further setup.

## What you can build with this

- **Daily content brief** — pull top HN stories, summarize, generate cross-platform posts.
- **Competitive research bot** — search HN for mentions of your competitors, surface negative comments.
- **Trend detector** — monitor `new` and `best` categories on a cron, alert when a topic spikes.
- **Newsletter pipeline** — search by keyword window, cluster results, generate editorial digest.
- **Customer-discovery agent** — search Ask HN for problems your product solves, generate cold-outreach drafts.
- **Tech-radar updater** — periodically scan `show` category for new tools in your stack.

## Troubleshooting

**"`mcp` command not found" / install errors.**
Make sure your Python is 3.10+. If using `uvx`, ensure [uv](https://docs.astral.sh/uv/) is installed (`pip install uv`). For pip install: `pip install necl-hn-mcp` then verify `python -m necl_hn_mcp --help` doesn't error.

**Tool calls timeout.**
HN's Firebase API can be slow when fetching many items (e.g. `hn_top_stories(limit=30, hours=168)` scans 200 stories). Default timeout is 10s per request. For long-window queries, use lower `limit`.

**Algolia returns no hits.**
Algolia indexes HN content with a delay (~5-15 min for fresh items). Try `sort="date"` for recent activity.

**Comments thread is empty for a story I see on HN.**
`hn_get_comments` returns only top-level comments. Replies aren't recursively fetched (to keep token cost predictable for LLMs). Use the `replies_count` field on each comment to know if there's deeper discussion.

**Tools don't show up in Claude.**
After editing `mcp.json`, fully restart Claude Desktop / Claude Code (not just reload). Check the MCP logs in Settings → Developer.

## Pair with

- [necl-content-poster](https://github.com/adjacentai/necl-skills/tree/main/necl-content-poster) Skill — turn HN stories into ready-to-publish posts for TG/LinkedIn/Threads.

Full pipeline:
```
necl-hn-mcp (find story) → necl-content-poster (write 3 posts) → you publish
```

## Built by NeCL

[neclco.com](https://neclco.com) — production AI engineering. RAG systems, voice agents, Telegram bots, custom MCPs and content engines for companies that need more than wrappers.

**Need a custom MCP wired to your internal APIs / databases / SaaS?** [Book a call](https://calendly.com/neclcompany/30min?utm_source=marketplace&utm_medium=mcp&utm_campaign=hn-mcp).

## Development

```bash
git clone https://github.com/adjacentai/necl-hn-mcp.git
cd necl-hn-mcp
pip install -e ".[dev]"

# Run locally with MCP inspector
mcp dev src/necl_hn_mcp/server.py
```

## License

MIT — see [LICENSE](./LICENSE).

---

Follow NeCL: [Telegram](https://t.me/necl_company) · [LinkedIn](https://www.linkedin.com/company/107986921) · [X](https://x.com/neclco) · [Site](https://neclco.com)
