# Changelog

All notable changes to `necl-hn-mcp` will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] — 2026-06-12

### Changed
- README: removed reference to an internal (non-open-source) project and its dead link; clarified the production-tested claim.

## [0.1.0] — 2026-06-09

### Added
- Initial release.
- 5 tools: `hn_top_stories`, `hn_get_story`, `hn_get_comments`, `hn_search`, `hn_category`.
- Smithery and direct (`python -m necl_hn_mcp`) install paths.
- No-credentials operation — uses public HN Firebase API and Algolia HN search API.
